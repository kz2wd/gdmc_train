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


def get_level_batch(heightmap, occupied_coord=None):
    if occupied_coord is None:
        occupied_coord = []
    batchs: list[list[tuple[int, int]]] = []
    for coord, height in heightmap:
        current_batch = get_current_batch(batchs, coord)
        # Todo : fill the batchs but without the occupied spots


def get_current_batch(batchs: list[list[tuple[int, int]]], coord: tuple[int, int]):
    for batch in batchs:
        if coord in batch:
            return batch
    new_batch = [coord]
    batchs.append(new_batch)
    return new_batch


def get_best_area(heightmap, occupied_coord, size, speed=4, roof=200):


    batchs = get_level_batch(heightmap, occupied_coord)

    # try to get the best size possible with the batch
    for batch in batchs:
        # Idea : center 'mass' of the batch : No
        """
        Ok So here is the idea :
            I should stop thinking about it like : find a location, put a batiment, repeat
            
            because I will lose the link between building, I need a way to create the city as a city and not a bunch of structures
            
            So we need to establish what we should have :
            
            First, we could start with a 'settlement center'
        
        """
        get_batch_center(batch)



    return best_coord


def get_batch_center(batch):
    x, y = 0, 0
    for coord in batch:
        x += coord[0]
        y += coord[1]



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

    # Door
    _w.set_block(start[0] + size[0] // 2, start[1] + 1, start[2], "minecraft:oak_door")
    _w.set_block(start[0] + size[0] // 2, start[1] + 2, start[2], "minecraft:oak_door[half=upper]")



if __name__ == "__main__":
    w = world.World()
    # cube(w, 50, 210, 50, 50, 'minecraft:jungle_leaves')

    bounding_box = [(0, 0), (100, 100)]

    # Always include the adjacente chunk
    val_to_chunk_val = lambda val: int(val // 16 + math.copysign(1, val))

    chunks_area = [(val_to_chunk_val(bounding_box[0][0]), val_to_chunk_val(bounding_box[0][1])),
                    (val_to_chunk_val(bounding_box[1][0]), val_to_chunk_val(bounding_box[1][1]))]

    chunk_range = int(abs(chunks_area[1][0] - chunks_area[0][0])), int(abs(chunks_area[1][1] - chunks_area[0][1]))

    occupied_spot = []

    for i in range(50):
        build_size = random.randint(5, 20), random.randint(4, 15), random.randint(5, 20)
        h_map = w.get_chunk_height_map(int(chunks_area[0][0]), int(chunks_area[0][1]), max(chunk_range[0], chunk_range[1]))

        best = get_best_area(h_map, max(build_size[0], build_size[2]), speed=5)

        if best is None:
            continue
        print(best)
        print(len(h_map))


        print(f"len coords : {len(coords)}")
        house_center = coords[best]
        print(house_center)

        house_start = (house_center[0] - build_size[0] // 2, house_center[1], house_center[2] - build_size[2] // 2)

        build_simple_house(w, house_start, build_size)

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
