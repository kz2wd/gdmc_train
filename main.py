import concurrent.futures

import world
import time
from nice_plot import plot_chunk
from virtual_view import visualize_chunk_update, Pipeline
import random
import threading


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


def chunk_around_shifts(radius):
    if radius < 1:
        return []
    shifts = []
    for i in range(1, radius + 1):
        shifts.append(i)
        shifts.append(i * 16)
        for value in range(1, i + 1):
            shifts.append(16 * i - value)
            shifts.append(16 * i + value)
    return shifts


def get_around(actual, max_index, radius, do_inverted_too=False):
    shifts = chunk_around_shifts(radius)
    for shift in shifts:
        val = actual + shift
        if 0 <= val < max_index:
            yield val
    if do_inverted_too:
        for shift in shifts:
            val = actual - shift
            if 0 <= val < max_index:
                yield val


def compute_steep(heightmap):
    steeps = []
    len_heightmap = len(heightmap)
    for i in range(len_heightmap):
        steep = 0
        for j in get_around(i, len_heightmap, 1, do_inverted_too=True):
            steep += abs(heightmap[i] - heightmap[j])
        steeps.append(steep)
    return steeps


def get_best_area(heightmap, size, speed=4):
    steep = compute_steep(heightmap)
    len_hmap = len(heightmap)
    min_score = 100_000_000
    best_coord = None
    for i in range(0, len_hmap, speed):
        coord = heightmap[i]
        score = 0
        for neighbor in get_around(coord, len_hmap, size, do_inverted_too=True):
            score += steep[neighbor]
        if score < min_score:
            print(f'found new score {score} at {coord}')
            best_coord = coord
            min_score = score
    return best_coord


def get_best_area_rng(heightmap, size, dots=4):
    steep = compute_steep(heightmap)
    max_coord = len(heightmap)
    min_score = 100_000_000
    best_coord = None
    for i in range(dots):
        coord = random.randint(0, max_coord)
        score = 0
        for neighbor in get_around(coord, max_coord, size, do_inverted_too=True):
            score += steep[neighbor]
        if score < min_score:
            best_coord = coord
            min_score = score
    return best_coord


def nice_print(chunk):
    info = "\n".join(" | ".join(f"{val:^3}" for val in chunk[row * 16:(row + 1) * 16:1]) for row in range(16))
    print(info)


def producer(pipe: Pipeline, wor: world.World):
    while True:
        pipe.set_content(wor.get_chunk_height_map(0, 1, 1, 1))
        print("getting hmap")
        time.sleep(.1)


if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    # h_map = w.get_chunk_height_map(0, 1, 1, 1)

    # best = get_best_area(h_map, 5, speed=1)
    # print(best)
    #
    # h_map[best] = -10

    pipeline = Pipeline()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline, w)
        executor.submit(visualize_chunk_update, pipeline)







    # print("Chunk")
    # nice_print(h_map)
    # plot_chunk(h_map)
    #
    # steep1 = compute_steep(h_map)
    # print("Steep 1")
    # nice_print(steep1)
    # plot_chunk(steep1)
    #
    # print("Steep 2")
    # nice_print(steep2)
    # plot_chunk(steep2)

    w.write_buffer()

    w.show_stats()
