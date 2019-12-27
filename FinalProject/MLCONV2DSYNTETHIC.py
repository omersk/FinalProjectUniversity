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
import random
import tensorflow as tf
from ast import literal_eval as str2arr
from tempfile import TemporaryFile
from operator import add
import librosa
#from gtts import gTTS
#win_len = 0.04  # in seconds
#step = win_len / 2
#nfft = 2048
win_len = 0.15# in seconds
step = win_len/2
nfft = 2**13
results = []
outfile_x = None
outfile_y = None
winner = []
val_lose = None


def modelCreator(onlyfiles, name1, name2):
    X = []  # inputs
    Y = []  # outputs

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
        if names.count(name) < 1:
            namesWithoutDuplicate.remove(name)
    names = namesWithoutDuplicate
    vector_names = []  # output for each name
    i = 0
    print(names)
    for name in names:
        vector_for_each_name = i
        vector_names.append(np.array(vector_for_each_name))
        i += 1
    for f in onlyfiles:  # for all the files
        if " " not in f.split("_")[0]:
            f_speaker = f.split("_")[0]
        else:
            f_speaker = f.split("_")[0].split(" ")[0]
        if f_speaker in names:
            fs, audio = wav.read("FinalAudios2\\" + f)  # read the file
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
            pass
    outfile_x = TemporaryFile()
    np.save(outfile_x, X)
    outfile_y = TemporaryFile()
    np.save(outfile_y, Y)
    Z = list(zip(X, Y))
    shuffle(Z)  # WE SHUFFLE X,Y TO PERFORM RANDOM ON THE TEST LEVEL
    X, Y = zip(*Z)
    X = list(X)
    Y = list(Y)
    lenX = len(X)
    # ------------------- RANDOMIZATION, UNNECESSARY TO UNDERSTAND THE CODE ------------------- #
    y_test = np.asarray(Y[:1])   # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_test = np.asarray(X[:1])   # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_train = np.asarray(X[1:])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    y_train = np.asarray(Y[1:])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_val = x_train[-1:]         # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    y_val = y_train[-1:]         # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    x_train = x_train[:-1]       # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    y_train = y_train[:-1]       # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    x_train = x_train.reshape(np.append(x_train.shape, (1, 1)))  # RESHAPE FOR INPUT
    x_test = x_test.reshape(np.append(x_test.shape, (1, 1)))     # RESHAPE FOR INPUT
    x_val = x_val.reshape(np.append(x_val.shape, (1, 1)))  # RESHAPE FOR INPUT
    features_shape = x_val.shape

    # -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(name='inputs', shape=(13, 1, 1), dtype='float32'),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same', strides=1, name='block1_conv', input_shape=(13, 1, 1)),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block1_pool'),
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
        tf.keras.layers.Dense(64, activation='relu', name='dense'),
        tf.keras.layers.BatchNormalization(name='dense_norm'),
        tf.keras.layers.Dropout(0.2, name='dropout'),
        tf.keras.layers.Dense(3, activation='softmax', name='pred')

    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    # -------------- OUR TENSOR FLOW NEURAL NETWORK MODEL -------------- #
    print("fitting")
    history = model.fit(x_train, y_train, epochs=8, validation_data=(x_val, y_val))
    print("testing")
    results.append(model.evaluate(x_test, y_test)[1])
    print(results)
    print(sum(results)/len(results))
    return model, names, vector_names

onlyfiles = [f for f in listdir("FinalAudios2") if (isfile(join("FinalAudios2", f)))]   # Files in dir
shuffle(onlyfiles)
testFiles = onlyfiles[:100]
onlyfiles = onlyfiles[100:]
model1, names, vector_names = modelCreator(onlyfiles, 'Leonard', 'Sheldon')
num = []

testFilesCopy = [] + testFiles
for id in tqdm(range(len(testFiles))):
    fs, audio = wav.read("FinalAudios2\\" + testFiles[id])  # read the file
    if len(audio) < fs:
        testFilesCopy.remove(testFiles[id])

testFiles = [] + testFilesCopy
xTest = []
yTest = []
for id in tqdm(range(len(testFiles))):
    fs, audio = wav.read("FinalAudios2\\" + testFiles[id])  # read the file
    mfcc_feat = python_speech_features.mfcc(audio, samplerate=fs, winlen=win_len, winstep=step, nfft=nfft,
                                            appendEnergy=False)
    X_now = []
    for i in mfcc_feat:
        X_now.append(np.array(i))
    X_now = np.asarray(X_now)
    X_now = X_now.reshape(X_now.shape + (1, 1))
    a = 0
    b = 0
    c = 0
    for i in range(len(X_now) - 1):
        predict = model1.predict_proba(X_now[i:i + 1])[0]
        if predict[0] == np.max(predict):
            a = a + 1
        elif predict[1] == np.max(predict):
            b = b + 1
        elif predict[2] == np.max(predict):
            c = c + 1
    if max([a, b, c]) == a:
        decide = names[0]
    elif max([a, b, c]) == b:
        decide = names[1]
    elif max([a, b, c]) == c:
        decide = names[2]
    if testFiles[id].split("_")[0] == decide:
        num = num + [1]
    else:
        num = num + [0]
    print(sum(num) / len(num))