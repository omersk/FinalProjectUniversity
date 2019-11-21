from sklearn.neural_network import MLPClassifier
import python_speech_features
import scipy.io.wavfile as wav
import numpy as np
from os import listdir
from os.path import isfile, join
from random import shuffle
import matplotlib.pyplot as plt
from tqdm import tqdm
from random import randint
import random
winner = []  # this array count how much Bingo we had when we test the NN
random_winner = []
win_len = 0.04  # in seconds
step = win_len / 2
nfft = 2048
for TestNum in tqdm(range(20)):  # in every round we build NN with X,Y that out of them we check 50 after we build the NN
    X = []
    Y = []
    onlyfiles = [f for f in listdir("FinalAudios/") if isfile(join("FinalAudios/", f))]   # Files in dir
    names = []  # names of the speakers
    for file in onlyfiles:  # for each wav sound
        # UNESSECERY TO UNDERSTAND THE CODE
        if " " not in file.split("_")[0]:
            names.append(file.split("_")[0])
        else:
            names.append(file.split("_")[0].split(" ")[0])
    only_speakers = [] + names
    #print only_speakers
    names = list(dict.fromkeys(names))  # names of speakers
    print names
    vector_names = []  # vector for each name
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
        fs, audio = wav.read("FinalAudios/" + f)  # read the file
        try:
            mfcc_feat = python_speech_features.mfcc(audio, samplerate=fs, winlen=win_len,
                                               winstep=step, nfft=nfft, appendEnergy=False)
            flat_list = [item for sublist in mfcc_feat for item in sublist]
            X.append(np.array(flat_list))
            Y.append(np.array(vector_names[names.index(f_speaker)]))
        except IndexError:
            pass
    Z = list(zip(X, Y))

    shuffle(Z)  # WE SHUFFLE X,Y TO PERFORM RANDOM ON THE TEST LEVEL

    X, Y = zip(*Z)
    X = list(X)
    Y = list(Y)
    X = np.asarray(X)
    Y = np.asarray(Y)

    Y_test = Y[:50]  # CHOOSE 50 FOR TEST, OTHERS FOR TRAIN
    X_test = X[:50]
    X = X[50:]
    Y = Y[50:]
    print len(X)
    clf = MLPClassifier(solver='lbfgs', alpha=3e-2, hidden_layer_sizes=(50, 20), random_state=2)  # create the NN
    clf.fit(X, Y)  # Train it
    print list(clf.predict_proba([X[0]])[0])
    print list(Y_test[0])
    for sample in range(len(X_test)):  # add 1 to winner array if we correct and 0 if not, than in the end it plot it
        arr = list(clf.predict([X_test[sample]])[0])
        if arr.index(max(arr)) == list(Y_test[sample]).index(1):
            winner.append(1)
        else:
            winner.append(0)
        if only_speakers[randint(0, len(only_speakers) - 1)] == only_speakers[randint(0, len(only_speakers) - 1)]:
            random_winner.append(1)
        else:
            random_winner.append(0)

# plot winner
plot_x = []
plot_y = []
for i in range(1, len(winner)):
    plot_y.append(sum(winner[0:i])*1.0/len(winner[0:i]))
    plot_x.append(i)
plot_random_x = []
plot_random_y = []
for i in range(1, len(random_winner)):
    plot_random_y.append(sum(random_winner[0:i])*1.0/len(random_winner[0:i]))
    plot_random_x.append(i)
plt.plot(plot_x, plot_y, 'r', label='machine learning')
plt.plot(plot_random_x, plot_random_y, 'b', label='random')
plt.xlabel('Number Of Samples')
# naming the y axis
plt.ylabel('Success Rate')

# giving a title to my graph
plt.title('Success Rate : Random Vs ML!')

# function to show the plot
plt.show()
