import concurrent.futures

from typing import Tuple

import world
import time
from nice_plot import plot_chunk
from virtual_view import visualize_chunk_update, Pipeline
import random
import threading
import math


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



# Seems okay
def chunk_heigtmap_to_coordinate(chunk, offset):
    coords = []

    for x in range(16):
        for y in range(16):
            coords.append((int(offset[0] + x), int(chunk[x + (y * 16)]), int(offset[1] + y)))

    return coords




def get_best_area(heightmap, center, occupied_coord, size, speed=4, roof=200):

    # Init best score, the lower the better, so we put it quite big at the start (normal scores should stay lower than 1000)
    best_score = 100_000_000
    dict_keys = list(heightmap.keys())
    best_coord = dict_keys[0]

    # Speed factor will make it only iterate over "len(heightmap) / speed" coords
    for coord in dict_keys[::speed]:
        score = get_score(coord, center, heightmap, occupied_coord, size, roof)

        if score < best_score:
            best_score = score
            best_coord = coord

        #     print(f"better score : {best_score} at {best_coord}")
        # else:
        #     print(f"score : {score} at {coord}")

    return best_coord


def get_score(coord, center, heightmap, occupied_coord, size, roof):
    height, width = size
    x, z = coord
    coord_high = heightmap[coord]

    # We don't want to be too high in the sky
    if coord_high > roof:
        return 100_000_000

    # apply bonus to score depending on the distance to the 'center'
    score = distance(coord, center) * .1
    # Score = sum of difference between the first point's altitude and the other
    for i in range(height):
        for j in range(width):
            try:
                current = (x + i, z + j)
                if current in occupied_coord:
                    # Bad luck I guess :3
                    return 100_000_000
                score += abs(coord_high - heightmap[current])
            except KeyError:
                pass

    return score


# Manhattan, you can tweak it later if you want
def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def nice_print(chunk):
    info = "\n".join(" | ".join(f"{val:^3}" for val in chunk[row * 16:(row + 1) * 16:1]) for row in range(16))
    print(info)


def producer(pipe: Pipeline, wor: world.World):
    while True:
        pipe.set_content(wor.get_chunk_height_map(0, 1, 1, 1))
        print("getting hmap")
        time.sleep(.1)

    # To use it, put this in main :
    # pipeline = Pipeline()
    #
    # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    #     executor.submit(producer, pipeline, w)
    #     executor.submit(visualize_chunk_update, pipeline)


def build_simple_house(_w: world.World, start: Tuple[int, int, int], size: Tuple[int, int, int]):
    # Todo : finish the simple houses
    # Walls
    panel(_w, start[0], start[1], start[2], size[0], size[1], 1, "minecraft:oak_planks")
    panel(_w, start[0], start[1], start[2] + size[2] - 1, size[0], size[1], 1, "minecraft:oak_planks")
    panel(_w, start[0], start[1], start[2], 1, size[1], size[2], "minecraft:oak_planks")
    panel(_w, start[0] + size[0] - 1, start[1], start[2], 1, size[1], size[2], "minecraft:oak_planks")

    # Ground
    panel(_w, start[0], start[1], start[2], size[0], 1, size[2], "minecraft:oak_planks")

    # Floor
    panel(_w, start[0], start[1] + size[1] - 1, start[2], size[0], 1, size[2], "minecraft:oak_planks")

    # Todo : add direction
    # Door
    _w.set_block(start[0] + size[0] // 2, start[1] + 1, start[2], "minecraft:oak_door")
    _w.set_block(start[0] + size[0] // 2, start[1] + 2, start[2], "minecraft:oak_door[half=upper]")



def check_heightmap(heightmap, world: world.World):
    for coord in heightmap:
        x, z = coord
        world.set_block(x, heightmap[coord], z, "minecraft:orange_stained_glass")
    world.write_buffer()
    input("Enter to erase")
    for coord in heightmap:
        x, z = coord
        world.set_block(x, heightmap[coord], z, "minecraft:air")


if __name__ == "__main__":
    bounding_box = [(0, 0), (100, 100)]
    w = world.World(bounding_box)
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')


    val_to_chunk_val = lambda val: val // 16

    chunks_area = [(val_to_chunk_val(bounding_box[0][0]) - 1, val_to_chunk_val(bounding_box[0][1]) - 1),
                    (val_to_chunk_val(bounding_box[1][0]) + 1, val_to_chunk_val(bounding_box[1][1]) + 1)]

    print(f"chunks_area : {chunks_area}")
    chunk_range = int(abs(chunks_area[1][0] - chunks_area[0][0])), int(abs(chunks_area[1][1] - chunks_area[0][1]))
    print(f"chunks range : {chunk_range}")
    center = (bounding_box[1][0] - bounding_box[0][0]) // 2 + bounding_box[0][0], (bounding_box[1][1] - bounding_box[0][1]) // 2 + bounding_box[0][1]
    print(f"center : {center}")
    occupied_spots = []

    h_map = w.get_chunk_height_map(int(chunks_area[0][0]), int(chunks_area[0][1]), chunk_range[0], chunk_range[1])
    print("got height map")
    for i in range(20):
        iter_start = time.time()
        build_size = random.randint(5, 10), random.randint(4, 15), random.randint(5, 10)

        speed_factor = max(build_size) // 5
        best = get_best_area(h_map, center, occupied_spots, (build_size[0], build_size[2]), speed=speed_factor)


        house_start = (best[0], h_map[best], best[1])

        for x in range(build_size[0]):
            for z in range(build_size[2]):
                occupied_spots.append((house_start[0] + x, house_start[2] + z))

        build_simple_house(w, house_start, build_size)
        w.write_buffer()
        print(f"Placed house of size {build_size} at {best} in {time.time() - iter_start:.2f}s with speed {speed_factor}")

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
