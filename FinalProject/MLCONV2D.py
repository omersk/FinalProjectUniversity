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
#win_len = 0.04  # in seconds
#step = win_len / 2
#nfft = 2048
win_len = 0.05  # in seconds
step = win_len
nfft = 16384
results = []
outfile_x = None
outfile_y = None
winner = []

for TestNum in tqdm(range(40)):  # We check it several times
    if not outfile_x:  # if path not exist we create it
        X = []  # inputs
        Y = []  # outputs
        onlyfiles = [f for f in listdir("FinalAudios") if isfile(join("FinalAudios", f))]   # Files in dir
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
            if names.count(name) < 2:
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
                fs, audio = wav.read("FinalAudios\\" + f)  # read the file
                try:
                    # compute MFCC
                    mfcc_feat = python_speech_features.mfcc(audio, samplerate=fs, winlen=win_len, winstep=step, nfft=nfft, appendEnergy=False)
                    #flat_list = [item for sublist in mfcc_feat for item in sublist]
                    # Create output + inputs
                    for i in mfcc_feat:
                        X.append(np.array(i))
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
    x_train = x_train.reshape(np.append(x_train.shape, (1, 1)))  # RESHAPE FOR INPUT
    x_test = x_test.reshape(np.append(x_test.shape, (1, 1)))     # RESHAPE FOR INPUT
    x_val = x_val.reshape(np.append(x_val.shape, (1, 1)))  # RESHAPE FOR INPUT
    features_shape = x_val.shape

    # -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(name='inputs', shape=(13, 1, 1), dtype='float32'),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', strides=1, name='block1_conv', input_shape=(13, 1, 1)),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2,2), padding='same', name='block1_pool'),
        tf.keras.layers.BatchNormalization(name='block1_norm'),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', strides=1, name='block2_conv',
                               input_shape=(13, 1, 1)),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block2_pool'),
        tf.keras.layers.BatchNormalization(name='block2_norm'),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', strides=1, name='block3_conv',
                               input_shape=(13, 1, 1)),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block3_pool'),
        tf.keras.layers.BatchNormalization(name='block3_norm'),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='softmax', name='dense'),
        tf.keras.layers.BatchNormalization(name='dense_norm'),
        tf.keras.layers.Dropout(0.2, name='dropout'),
        tf.keras.layers.Dense(10, activation='softmax', name='pred')

    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    # -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #

    print("fitting")
    history = model.fit(x_train, y_train, epochs=6, validation_data=(x_val, y_val))
    print("testing")
    results.append(model.evaluate(x_test, y_test)[1])
    print(results)
    print(sum(results)/len(results))
    for i in range(10000):
        f_1 = only_speakers[randint(0, len(only_speakers) - 1)]
        f_2 = only_speakers[randint(0, len(only_speakers) - 1)]
        if " " not in f_1.split("_")[0]:
            f_speaker_1 = f_1.split("_")[0]
        else:
            f_speaker_1 =f_1.split("_")[0].split(" ")[0]
        if " " not in f_2.split("_")[0]:
            f_speaker_2 = f_2.split("_")[0]
        else:
            f_speaker_2 =f_2.split("_")[0].split(" ")[0]
        if f_speaker_2 == f_speaker_1:
            winner.append(1)
        else:
            winner.append(0)
    print(sum(winner)/len(winner))
    #]
    # if onlyfiles[randint(len(onlyfiles) - 1)] == onlyfiles[randint(len(onlyfiles) - 1)]
    #pyplot.plot(history.history['loss'], label='train')
    #pyplot.plot(history.history['val_loss'], label='test')                                          Q
    #pyplot.legend()
    #pyplot.show()
