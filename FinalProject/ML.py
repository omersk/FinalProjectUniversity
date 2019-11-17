from sklearn.neural_network import MLPClassifier
import python_speech_features
import scipy.io.wavfile as wav
from tqdm import tqdm
import numpy as np
from os import listdir
from os.path import isfile, join
import sys
from random import shuffle
import matplotlib.pyplot as plt

winner = []
for testNum in range(20):
    X = []
    Y = []
    onlyfiles = [f for f in listdir("FinalAudios/") if isfile(join("FinalAudios/", f))]
    shuffle(onlyfiles)
    names = []
    for file in onlyfiles:
        if " " not in file.split("_")[0]:
            names.append(file.split("_")[0])
        else:
            names.append(file.split("_")[0].split(" ")[0])
    names = list(dict.fromkeys(names))
    vector_names = []
    i = 0
    vector_for_each_name = [0] * len(names)
    for name in names:
        vector_for_each_name[i] += 1
        vector_names.append(np.array(vector_for_each_name))
        vector_for_each_name[i] -= 1
        i += 1
    for f in onlyfiles:
        if " " not in f.split("_")[0]:
            f_speaker = f.split("_")[0]
        else:
            f_speaker = f.split("_")[0].split(" ")[0]
        (rate, sig) = wav.read("FinalAudios/" + f)
        try:
            mfcc_feat = python_speech_features.mfcc(sig, rate, winlen=0.2)  # mfcc coeffs
            for index in range(len(mfcc_feat)):
                X.append(np.array(mfcc_feat[index]))
                Y.append(np.array(vector_names[names.index(f_speaker)]))
        except IndexError:
            pass
    X = np.asarray(X)
    Y = np.asarray(Y)
    Y_test = Y[:50]
    X_test = X[:50]
    X = X[50:]
    Y = Y[50:]

    clf = MLPClassifier(solver='lbfgs', alpha=1e-2, hidden_layer_sizes=(5, 3), random_state=2)  # create the NN
    clf.fit(X, Y)  # Train it

    for sample in range(len(X_test)):
        if list(clf.predict([X[sample]])[0]) == list(Y_test[sample]):
            winner.append(1)
        else:
            winner.append(0)

plot_x = []
plot_y = []
for i in range(1, len(winner)):
    plot_y.append(sum(winner[0:i])*1.0/len(winner[0:i]))
    plot_x.append(i)
plt.plot(plot_x, plot_y)
plt.xlabel('x - axis')
# naming the y axis
plt.ylabel('y - axis')

# giving a title to my graph
plt.title('My first graph!')

# function to show the plot
plt.show()
