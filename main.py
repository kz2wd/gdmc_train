import world
import time


def get_time(f):
    def modified(*args, **kwargs):
        start = time.time()
        f(*args, **kwargs)
        took = round(time.time() - start, 2)
        print(f'{f.__name__} Took {took}s')
    return modified


@get_time
def cube(_w: world.World, x: int, y: int, z: int, size: int, material: str) -> None:
    for i in range(x, size + x):
        for j in range(y, y + size):
            for k in range(z, z + size):
                _w.set_block(i, j, k, material)


def get_packets(data, size):
    i = 0
    outputs = len(data) // size
    while outputs > i:
        yield data[i * size: (i + 1) * size]
        i += 1


if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    # https://minecraft.fandom.com/wiki/Chunk_format
    # WRONG !!!
    raw_data = w.get_height_map()
    data = list(map(lambda x: bin(int(x)), raw_data))
    print(raw_data)
    print(data)
    bin_data = "".join(d[2:] for d in data)
    h_map = [int(p, 2) for p in get_packets(bin_data, 8)]

    print(bin_data)
    print(len(bin_data))
    print(h_map)
    print(len(h_map))
    w.write_buffer()

    w.show_stats()
