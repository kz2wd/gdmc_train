
import matplotlib.pyplot as plt


def nice_plot(X, Y, Z, *angles):
    if angles is None or not angles:
        angles = [(20, 10), (60, 35)]
    fig = plt.figure()
    fig.tight_layout(pad=0.3, rect=[0, 0, 0.9, 0.9])

    for i, angle in enumerate(angles):
        ax = fig.add_subplot(1, 2, i + 1, projection='3d')
        ax.scatter(X, Y, Z)

        ax.set_xlabel('data amount')
        ax.set_zlabel('loss')
        ax.set_ylabel('batch size')

        ax.view_init(*angle)

    plt.show()


def plot_chunk(chunk, *angles):
    Z = []
    X = []
    Y = []
    for i, v in enumerate(chunk):
        X.append(i)
        Z.append(v)
        Y.append(i % 16)

    if angles is None or not angles:
        angles = [(20, 10), (60, 35)]
    fig = plt.figure()
    fig.tight_layout(pad=0.3, rect=[0, 0, 0.9, 0.9])

    for i, angle in enumerate(angles):
        ax = fig.add_subplot(1, 2, i + 1, projection='3d')
        ax.scatter(X, Y, Z)

        ax.set_xlabel('x')
        ax.set_zlabel('height')
        ax.set_ylabel('y')

        ax.view_init(*angle)

    plt.show()

