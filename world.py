import time

import requests


class World:
    BUFFER_SIZE: int = 100
    MAX_REQUESTS_AMOUNT = 0

    def __init__(self, address='http://localhost:9000/'):
        self.address = address
        self.buffer = []

        # for stats purpose
        self.start = time.time()
        self.requests_amount = 0
        self.block_placed = 0

    def set_block(self, x: int, y: int, z: int, block: str) -> None:
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

    def get_chunk_height_map(self, x: int, z: int, dx: int, dz: int) -> list:
        rq = requests.get(self.address + f'chunks?x={x}&z={z}&dx={dx}&dz={dz}').text.split('MOTION_BLOCKING_NO_LEAVES:[L;')
        h_map = []
        for i in range(1, len(rq)):
            h_map += treat_chunk_data(rq[i].split(']')[0].replace('L', '').split(','))

        return h_map


def treat_chunk_data(rq):
    data = list(map(lambda x: f"{int(x):063b}", rq[:-1]))
    data.append(f"{int(rq[-1]):036b}")
    bin_data = "".join(d for d in data)
    h_map = [int(p, 2) for p in get_packets(bin_data, 9)]
    return h_map


def get_packets(data, size):
    i = 0
    outputs = len(data) // size
    while outputs > i:
        yield data[i * size: (i + 1) * size]
        i += 1
