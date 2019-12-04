import python_speech_features
import scipy.io.wavfile as wav
import numpy as np
from os import listdir
import os
import shutil
from os.path import isfile, join
from random import shuffle
from matplotlib import pyplot
from tqdm import tqdm
from random import randint
import tensorflow as tf
from ast import literal_eval as str2arr
from tempfile import TemporaryFile
win_len = 0.04  # in seconds
step = win_len / 2
nfft = 2048
results = []
outfile_x = None
outfile_y = None
for TestNum in tqdm(range(40)):  # We check it several times
    if not outfile_x:  # if path not exist we create it
        X = []  # inputs
        Y = []  # outputs
        onlyfiles = [f for f in listdir("FinalAudios/") if isfile(join("FinalAudios/", f))]   # Files in dir
        names = []  # names of the speakers
        for file in onlyfiles:  # for each wav sound
            # UNESSECERY TO UNDERSTAND THE CODE
            if " " not in file.split("_")[0]:
                names.append(file.split("_")[0])
            else:
                names.append(file.split("_")[0].split(" ")[0])
        only_speakers = [] + names
        namesWithoutDuplicate = list(dict.fromkeys(names))
        namesWithoutDuplicateCopy = namesWithoutDuplicate[:]
        for name in namesWithoutDuplicateCopy:  # we remove low samples files
            if names.count(name) < 60:
                namesWithoutDuplicate.remove(name)
        names = namesWithoutDuplicate
        print(names)  # print it
        vector_names = []  # output for each name
        i = 0
        for name in names:
            vector_for_each_name = i
            vector_names.append(np.array(vector_for_each_name))
            i += 1
        for f in onlyfiles:  # for all the files
            if " " not in f.split("_")[0]:
                f_speaker = f.split("_")[0]
            else:
                f_speaker = f.split("_")[0].split(" ")[0]
            if f_speaker in namesWithoutDuplicate:
                fs, audio = wav.read("FinalAudios/" + f)  # read the file
                try:
                    # compute MFCC
                    mfcc_feat = python_speech_features.mfcc(audio, samplerate=fs, winlen=win_len,
                                                       winstep=step, nfft=nfft, appendEnergy=False)
                    flat_list = [item for sublist in mfcc_feat for item in sublist]
                    # Create output + inputs
                    X.append(np.array(flat_list))
                    Y.append(np.array(vector_names[names.index(f_speaker)]))
                except IndexError:
                    pass
            else:
                if not os.path.exists("TooLowSamples"):  # if path not exist we create it
                    os.makedirs("TooLowSamples")
                shutil.move("FinalAudios\\" + f, "TooLowSamples\\" + f)
        outfile_x = TemporaryFile()
        np.save(outfile_x, X)
        outfile_y = TemporaryFile()
        np.save(outfile_y, Y)



    # ------------------- RANDOMIZATION, UNNECESSARY TO UNDERSTAND THE CODE ------------------- #
    else:
        outfile_x.seek(0)
        X = np.load(outfile_x)
        outfile_y.seek(0)
        Y = np.load(outfile_y)
    Z = list(zip(X, Y))
    shuffle(Z)  # WE SHUFFLE X,Y TO PERFORM RANDOM ON THE TEST LEVEL
    X, Y = zip(*Z)
    X = list(X)
    Y = list(Y)
    lenX = len(X)
    # ------------------- RANDOMIZATION, UNNECESSARY TO UNDERSTAND THE CODE ------------------- #
    y_test = np.asarray(Y[:100])   # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_test = np.asarray(X[:100])   # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_train = np.asarray(X[100:])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    y_train = np.asarray(Y[100:])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_val = x_train[-100:]         # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    y_val = y_train[-100:]         # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    x_train = x_train[:-100]       # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    y_train = y_train[:-100]       # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    x_train = x_train.reshape(np.append(x_train.shape, 1))  # RESHAPE FOR INPUT
    x_test = x_test.reshape(np.append(x_test.shape, 1))     # RESHAPE FOR INPUT
    x_val = x_val.reshape(np.append(x_val.shape, 1))        # RESHAPE FOR INPUT

    # -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(len(names), activation='softmax'),
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    # -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #

    print("fitting")
    history = model.fit(x_train, y_train, epochs=2, validation_data=(x_val, y_val))
    print("testing")
    results.append(model.evaluate(x_test, y_test)[1])
    print(results)
    print(sum(results)/len(results))

    #]
    # if onlyfiles[randint(len(onlyfiles) - 1)] == onlyfiles[randint(len(onlyfiles) - 1)]
    #pyplot.plot(history.history['loss'], label='train')
    #pyplot.plot(history.history['val_loss'], label='test')                                          Q
    #pyplot.legend()
    #pyplot.show()
