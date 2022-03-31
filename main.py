import concurrent.futures

from typing import Tuple

import world
import time
from nice_plot import plot_chunk
from virtual_view import visualize_chunk_update, Pipeline
import random
import threading


def get_time(f):
    def modified(*args, **kwargs):
        start = time.time()
        results = f(*args, **kwargs)
        took = round(time.time() - start, 2)
        print(f'{f.__name__} Took {took}s')
        return results
    return modified


@get_time
def cube(_w: world.World, x: int, y: int, z: int, size: int, material: str) -> None:
    for i in range(x, size + x):
        for j in range(y, y + size):
            for k in range(z, z + size):
                _w.set_block(i, j, k, material)


def panel(_w: world.World, x: int, y: int, z: int, width: int, height: int, depth: int, material: str) -> None:
    for i in range(x, x + width):
        for j in range(y, y + height):
            for k in range(z, z + depth):
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


# Seems okay
def chunk_heigtmap_to_coordinate(chunk, offset):
    coords = []

    for x in range(16):
        for y in range(16):
            coords.append((offset[0] + x, chunk[x + (y * 16)], offset[1] + y))

    return coords


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


def build_simple_house(_w: world.World, start: Tuple[int, int, int], size: int):
    # Todo : finish the simple houses
    panel(_w, start[0], start[1], start[2], size, size, 1, "minecraft:oak_planks")



if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    build_size = 5

    h_map = w.get_chunk_height_map(0, 1, 1, 1)

    best = get_best_area(h_map, build_size, speed=1)
    print(best)


    # pipeline = Pipeline()
    #
    # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    #     executor.submit(producer, pipeline, w)
    #     executor.submit(visualize_chunk_update, pipeline)

    coords = chunk_heigtmap_to_coordinate(h_map, (0, 16))
    house_center = coords[best]
    print(house_center)

    shift = build_size // 2
    house_start = (house_center[0] - shift, house_center[1], house_center[2] - shift)

    build_simple_house(w, house_start, 5)

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
