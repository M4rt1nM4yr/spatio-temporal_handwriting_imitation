import numpy as np
from sklearn import mixture


def find_scaling_errors(database):
    stdDevs = []

    for strokes in database.samples:
        # Filter out movements that were done during a pen-up time
        nonJumpStrokes = strokes[strokes[:, 2] < 0.5, :]

        # Compute the standard deviation of the strokes. If squashed, should be smaller in one direction than the other.
        strokesStdDev = nonJumpStrokes.std(axis=0)[:2]
        stdDevs.append(strokesStdDev)

    stdDevs = np.array(stdDevs)
    angles = np.arctan2(stdDevs[:, 1], stdDevs[:, 0])
    # angles = np.array(angles)
    # print(stdDevs[:, 0])
    # plt.plot(stdDevs[:, 0], stdDevs[:, 1], 'ro')
    # plt.show()
    # print(stdDevs)
    # print(stdDevs[0], angles[0])
    # print(stdDevs[12], angles[12])

    #print('hist:', np.histogram(angles, bins=20))
    # print(scipy.cluster.vq.kmeans(angles, 2))

    numMixtureComponents = 2
    gmm = mixture.GaussianMixture(n_components=numMixtureComponents)
    gmm.fit(angles.reshape(-1, 1))
    labels = gmm.predict(angles.reshape(-1, 1))

    noPreprocessingLabel = np.argmin(gmm.means_)
    resultLabels = (labels == noPreprocessingLabel)

    #for i in range(20):
    #    print(i, angles[i], labels[i], resultLabels[i])

    ## Plot the GaussianMixtureModel on which the decision boundary is based on
    if False:
        histResult = plt.hist(angles, bins='auto', alpha=0.7, rwidth=0.85)
        x = np.linspace(min(angles), max(angles), 100)
        dx = histResult[1][1] - histResult[1][0]
        scale = len(angles) * dx

        for i in range(numMixtureComponents):
            plt.plot(x, gmm.weights_[i] * (
                        scipy.stats.norm.pdf(x, gmm.means_[i], np.sqrt(gmm.covariances_[i])) * scale).reshape(-1))
        plt.show()

    return resultLabels


def fix_scaling_error(sample, scalingMax, scalingMin):
    scaling = scalingMax - scalingMin
    rescaling = np.array([1.0, scaling[0] / scaling[1], 1.0])

    rescaledSample = sample * rescaling
    return rescaledSample
