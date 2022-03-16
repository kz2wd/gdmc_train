import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import glBegin, GL_LINES, glVertex3fv, glEnd, glTranslatef, glClear, GL_COLOR_BUFFER_BIT, \
    GL_DEPTH_BUFFER_BIT, glRotatef
from OpenGL.GLU import gluPerspective

ratio = 50


def show_heightmap(heightmap, tile_length=.5):

    # Not perfect but good enough !

    center = [0, -1, 0]

    tile_number = len(heightmap)

    corner = [center[0] - (tile_number * tile_length/2), center[1], center[2] - (tile_number * tile_length)/2]

    vertices = []
    half_tile = tile_length / 2

    for i in range(tile_number):
        for j in range(tile_number):
            vertices.append([i * tile_length + corner[0] + half_tile, heightmap[i][j] / ratio, j * tile_length + corner[2] + half_tile])
            vertices.append([i * tile_length + corner[0] - half_tile, heightmap[i][j] / ratio, j * tile_length + corner[2] + half_tile])
            vertices.append([i * tile_length + corner[0] - half_tile, heightmap[i][j] / ratio, j * tile_length + corner[2] - half_tile])
            vertices.append([i * tile_length + corner[0] + half_tile, heightmap[i][j] / ratio, j * tile_length + corner[2] - half_tile])

    edges = []

    for i in range(0, tile_number * 4, 4):
        for j in range(0, tile_number * 4, 4):

            # Bloc face
            edges.append([j + i * tile_number, j + i * tile_number + 1])
            edges.append([j + i * tile_number, j + i * tile_number + 3])
            edges.append([j + i * tile_number + 2, j + i * tile_number + 1])
            edges.append([j + i * tile_number + 2, j + i * tile_number + 3])

    for i in range(0, (tile_number - 1) * 4, 4):
        for j in range(0, (tile_number - 1) * 4, 4):
            # Connection to next bloc
            edges.append([j + i * tile_number, j + i * tile_number + 7])
            edges.append([j + i * tile_number + 1, j + i * tile_number + 6])

            edges.append([j + i * tile_number, j + i * tile_number + tile_number * 4 + 1])
            edges.append([j + i * tile_number + 3, j + i * tile_number + tile_number * 4 + 2])

    return edges, vertices


def display_structure(edges, vertices):

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


def visualize_chunk(chunk):
    pygame.init()
    display = (1080, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    y = max(chunk) / ratio
    heightmap = [chunk[i * 16:16 * (i + 1)] for i in range(16)]

    edges, vertices = show_heightmap(heightmap)

    print(len(vertices))
    print(len(edges))
    gluPerspective(45, (display[0] / display[1]), 0.1, 200.0)

    glTranslatef(0.0, -y * 1.1, -15)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        display_structure(edges, vertices)
        glRotatef(1, 0, 1, 0)
        pygame.display.flip()
        pygame.time.wait(10)
