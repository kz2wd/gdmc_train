import time

import requests


class World:
    BUFFER_SIZE: int = 100
    MAX_REQUESTS_AMOUNT = 0

    def __init__(self, build_limits, address='http://localhost:9000/'):
        self.address = address
        self.buffer = []
        self.build_limits = build_limits

        # for stats purpose
        self.start = time.time()
        self.requests_amount = 0
        self.block_placed = 0

    def set_block(self, x: int, y: int, z: int, block: str) -> None:
        # If the block to place is not inside the boundaries
        if not (self.build_limits[0][0] <= x <= self.build_limits[1][0] and self.build_limits[0][1] <= z <= self.build_limits[1][1]):
            return

        self.buffer.append((x, y, z, block))
        if len(self.buffer) >= World.BUFFER_SIZE:
            self.write_buffer()

    def get_block(self, x: int, y: int, z: int) -> str:
        r = requests.get(self.address + f'blocks?x={x}&y={y}&z={z}')
        r.close()
        return r.text

    def write_buffer(self) -> None:
        data = "\n".join(f"~{i[0]} ~{i[1]} ~{i[2]} {i[3]}" for i in self.buffer)
        requests.put(self.address + f'blocks?x=0&y=0&z=0', data=data).close()
        self.block_placed += len(self.buffer)
        self.requests_amount += 1
        self.buffer = []

    def show_stats(self) -> None:
        took = round(time.time() - self.start, 2)
        print(f"Did {self.requests_amount}rqs ({self.block_placed} blocks) in {took}")
        if took != 0:
            print(f"Average : {round(self.requests_amount / took, 2)}rq/s")


    def get_chunk_height_map(self, pos_chunk_x: int, pos_chunk_z: int, size_x: int, size_z: int) -> list:
        rq = requests.get(self.address + f'chunks?x={pos_chunk_x}&z={pos_chunk_z}&dx={size_x}&dz={size_z}').text.split('MOTION_BLOCKING_NO_LEAVES:[L;')
        h_map_chunks = []
        for i in range(1, len(rq)):
            h_map_chunks.append(treat_chunk_data(rq[i].split(']')[0].replace('L', '').split(',')))

        heightmap_dict = dict()

        for chunk_x in range(size_x):
            for chunk_z in range(size_z):
                for x in range(16):
                    for z in range(16):
                        heightmap_dict[(x + (chunk_x + pos_chunk_x) * 16, z + (chunk_z + pos_chunk_z) * 16)] = h_map_chunks[chunk_x + (chunk_z * size_x)][x + z * 16]

        return heightmap_dict

    def get_chunks_NBT_data(self, pos_chunk_x: int, pos_chunk_z: int, size_x: int, size_z: int) -> list:
        return requests.get(self.address + f'chunks?x={pos_chunk_x}&z={pos_chunk_z}&dx={size_x}&dz={size_z}',
                            headers={'Accept': 'application/octet-stream'}).content

def treat_chunk_data(rq):
    data = list(map(lambda x: f"{int(x):063b}", rq[:-1]))
    data.append(f"{int(rq[-1]):036b}")
    bin_data = "".join(d for d in data)

    # disaster of code but order may be 'more' correct
    # invert sequence every 7 value
    h_map = []
    count = 0
    temp_list = []
    for val in get_packets(bin_data, 9):
        temp_list.append(int(val, 2))
        count += 1
        if count == 7:
            h_map += temp_list[::-1]
            temp_list = []
            count = 0

    h_map += temp_list[::-1]

    # beautiful code but order incorrect
    # h_map = [int(p, 2) for p in get_packets(bin_data, 9)]

    return h_map


def get_packets(data, size):
    i = 0
    outputs = len(data) // size
    while outputs > i:
        yield data[i * size: (i + 1) * size]
        i += 1


