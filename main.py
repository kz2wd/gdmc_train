import world
import time
from nice_plot import plot_chunk
from virtual_view import visualize_chunk


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


def neighbors_indexes(actual, max_index):
    if actual - 1 >= 0:
        yield actual - 1
    if actual - 16 >= 0:
        yield actual - 16
    if actual + 1 < max_index:
        yield actual + 1
    if actual + 16 < max_index:
        yield actual + 16


def compute_steep(heightmap):
    steeps = []
    len_heightmap = len(heightmap)
    for i in range(len_heightmap):
        steep = 0
        for j in neighbors_indexes(i, len_heightmap):
            steep += abs(heightmap[i] - heightmap[j])
        steeps.append(steep)
    return steeps


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


def nice_print(chunk):
    info = "\n".join(" | ".join(f"{val:^3}" for val in chunk[row * 16:(row + 1) * 16:1]) for row in range(16))
    print(info)


if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    h_map = w.get_chunk_height_map(0, 0, 1, 1)

    steep1 = compute_steep(h_map)
    steep2 = compute_steep(steep1)

    # visualize_chunk(h_map)

    # print("Chunk")
    # nice_print(h_map)
    # plot_chunk(h_map)
    #
    # print("Steep 1")
    # nice_print(steep1)
    # plot_chunk(steep1)
    #
    # print("Steep 2")
    # nice_print(steep2)
    # plot_chunk(steep2)

    w.write_buffer()

    w.show_stats()
