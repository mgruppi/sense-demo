from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np


def plot_words(wv1, wv2, words, file="static/image/tmp.png"):
    """
    Given two (aligned) WordVectors, generate an image file
    containing the 2D PCA plots of the selected words
    """

    x1 = np.array([wv1[w] for w in words])
    x2 = np.array([wv2[w] for w in words])
    x = np.concatenate((x1,x2))
    x = PCA(n_components=2).fit_transform(x)

    x1 = x[:len(x1)]
    x2 = x[len(x1):]

    fig, ax = plt.subplots()

    ax.scatter(x1[:, 0], x1[:, 1], c="blue")
    ax.scatter(x2[:, 0], x2[:, 1], c="red")

    for i, w in enumerate(words):
        ax.annotate(w, (x1[i][0], x1[i][1]), color="blue")
        ax.annotate(w, (x2[i][0], x2[i][1]), color="red")

    fig.savefig(file, format="png")
    plt.close(fig)
