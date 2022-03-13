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


def get_areas(heightmap, first_bloc_location):
    areas = {}
    for x in range(16):
        for y in range(16):
            index = x + y * 16
            current = heightmap[index]
            try:
                areas[current]
            except KeyError:
                areas[current] = [[(x, y)]]

            if index + 1 < 256 and current == heightmap[index + 1]:
                for area in areas[current]:
                    if (x, y) in area:
                        area.append((x + 1, y))
                        break
            if index + 16 < 256 and current == heightmap[index + 16]:
                for area in areas[current]:
                    if (x, y) in area:
                        area.append((x, y + 1))
                        break

    print(areas)


if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    h_map = w.get_chunk_height_map(0, 0, 1, 1)

    print(h_map)
    print(len(h_map))

    get_areas(h_map, (0, 0, 0))
    w.write_buffer()

    w.show_stats()
