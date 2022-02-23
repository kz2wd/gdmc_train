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


if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    # Remove unused bit
    data = map(lambda x: int(x[:-1]), w.get_height_map())

    # Must be wrong somewhere ?
    # Check : https://minecraft.fandom.com/wiki/Chunk_format
    data = map(bin, data)

    h_map = []
    for d in data:
        h_map.append(d[0: 6])

    h_map = map(lambda x: int(x, 2), h_map)
    print(list(h_map))

    w.write_buffer()

    w.show_stats()
