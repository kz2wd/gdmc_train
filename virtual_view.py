import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import glBegin, GL_LINES, glVertex3fv, glEnd, glTranslatef, glClear, GL_COLOR_BUFFER_BIT, \
    GL_DEPTH_BUFFER_BIT, glRotatef
from OpenGL.GLU import gluPerspective

ratio = 10


def show_heightmap(heightmap, tile_length=1):  # improved :D

    center = [0, -1, 0]
    tile_number = len(heightmap)

    corner = [center[0] - (tile_number * tile_length/2), center[1], center[2] - (tile_number * tile_length)/2]

    vertices = []

    for i in range(tile_number):
        for j in range(tile_number):
            vertices.append([i * tile_length + corner[0], heightmap[i][j] / ratio, j * tile_length + corner[2]])

    edges = []  # not working

    for i in range(tile_number):
        for j in range(tile_number - 1):
            edges.append([j + i * tile_number, j + i * tile_number + 1])

    for i in range(len(vertices) - tile_number):
        edges.append([i, i + tile_number])

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

    edges, vertices = show_heightmap(heightmap, 1)

    print(len(vertices))
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
