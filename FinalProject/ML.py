from sklearn.neural_network import MLPClassifier
import python_speech_features
import scipy.io.wavfile as wav
from tqdm import tqdm

from os import listdir
from os.path import isfile, join
import sys


class NullWriter(object):
    def write(self, arg):
        pass

nullwrite = NullWriter()
oldstdout = sys.stdout

dict_file_mfcc = {}  # for every file it create the following dict : { mfcc_13_coeffs_of_file : speaker }
dict_file_output = {}  # for every speaker it create vector, example { penny: [1,0,0,0], leonard: [0,0,1,0] }

onlyfiles = [f for f in listdir("FinalAudios/") if isfile(join("FinalAudios/", f))]
#num = raw_input("Number Between 0 and " + str(len(onlyfiles)) + " : ")
i = 0
for num in tqdm(range(len(onlyfiles))):
    for f in onlyfiles:
        if f != onlyfiles[int(num)]:
            f_speaker = f.split("_")[0]
            (rate, sig) = wav.read("FinalAudios/" + f)
            try:
                mfcc_feat = python_speech_features.mfcc(sig, rate)  # mfcc coeffs
                dict_file_mfcc[tuple(mfcc_feat[0])] = f_speaker  # first 13 mfcc coeffs
            except IndexError:
                pass
    j = 0

    #print list(dict.fromkeys(dict_file_mfcc.values()))
    our_output_vector = [0] * len(list(dict.fromkeys(dict_file_mfcc.values())))  # zero array
    save_our_output_vector = [] + our_output_vector  # make it array with one in the speaker number position
    for name in list(dict.fromkeys(dict_file_mfcc.values())):
        our_output_vector = [] + save_our_output_vector
        our_output_vector[j] = 1
        dict_file_output[name] = our_output_vector  # output value for the speaker
        j += 1

    X = []
    Y = []
    for x in dict_file_mfcc.keys():
        X.append(list(x))
        Y.append(dict_file_output[dict_file_mfcc[x]])
    clf = MLPClassifier(solver='lbfgs', alpha=1e-2, hidden_layer_sizes=(5, 3), random_state=2)  # create the NN
    clf.fit(X, Y)  # Train it
    (rate, sig) = wav.read("FinalAudios/" + onlyfiles[int(num)])
    #print onlyfiles[int(num)].split("_")[0]
    mfcc_feat = python_speech_features.mfcc(sig, rate)
    #print dict_file_output
    winners = list(clf.predict_proba([list(mfcc_feat[0])]))
    #print winners
    dict_winner = {0: "Penny", 1: "Leonard", 2: "Sheldon", 3: "Receptionist"}
    winner = dict_winner[list(winners[0]).index(max(winners[0]))]
    print winner
    if winner == onlyfiles[int(num)].split("_")[0]:
        i += 1
        #print "WE WON!!!!!"
    else:
        pass
        #print "WE LOST!!!!!!"
    sys.stdout = oldstdout  # enable output

print i * 1.0 / len(onlyfiles)