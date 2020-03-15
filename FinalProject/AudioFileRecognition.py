#!/usr/bin/python
# -*- coding: utf-8 -*-
import python_speech_features
import scipy.io.wavfile as wav
import numpy as np
from os import listdir
from os.path import isfile, join
from random import shuffle
from tqdm import tqdm
import tensorflow as tf
win_len = 0.15  # in seconds
step = win_len / 2
nfft = 2 ** 13
results = []
outfile_x = None
outfile_y = None
winner = []
val_lose = None


def machine_learning_model():
    """
    Function that create a tensor-flow neural network model
    of recognizing speaker
    format:
        1.  Layer (type)                 Output Shape              Param #
        2.  block1_conv (Conv2D)         (None, 13, 1, 32)         320
        3.  block1_pool (MaxPooling2D)   (None, 7, 1, 32)          0
        4.  block1_norm (BatchNormalizat (None, 7, 1, 32)          128
        5.  block1_norm (BatchNormalizat (None, 7, 1, 32)          128
        6.  block2_pool (MaxPooling2D)   (None, 4, 1, 32)          0
        7.  block2_norm (BatchNormalizat (None, 4, 1, 32)          128
        8.  block3_conv (Conv2D)         (None, 4, 1, 32)          9248
        9.  block3_pool (MaxPooling2D)   (None, 2, 1, 32)          0
        10. block3_norm (BatchNormalizat (None, 2, 1, 32)          128
        11. flatten_5 (Flatten)          (None, 64)                0
        12. dense (Dense)                (None, 64)                4160
        13. dense_norm (BatchNormalizati (None, 64)                256
        14. dropout (Dropout)            (None, 64)                0
        15. pred (Dense)                 (None, 3)                 195
    :return: tensor-flow recognizing speaker neural network model
    """
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(name='inputs', shape=(13, 1, 1),
                              dtype='float32'),
        tf.keras.layers.Conv2D(
            32,
            (3, 3),
            activation='relu',
            padding='same',
            strides=1,
            name='block1_conv',
            input_shape=(13, 1, 1),
            ),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2),
                padding='same', name='block1_pool'),
        tf.keras.layers.BatchNormalization(name='block1_norm'),
        tf.keras.layers.Conv2D(
            32,
            (3, 3),
            activation='relu',
            padding='same',
            strides=1,
            name='block2_conv',
            input_shape=(13, 1, 1),
            ),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2),
                padding='same', name='block2_pool'),
        tf.keras.layers.BatchNormalization(name='block2_norm'),
        tf.keras.layers.Conv2D(
            32,
            (3, 3),
            activation='relu',
            padding='same',
            strides=1,
            name='block3_conv',
            input_shape=(13, 1, 1),
            ),
        tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2),
                padding='same', name='block3_pool'),
        tf.keras.layers.BatchNormalization(name='block3_norm'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu', name='dense'),
        tf.keras.layers.BatchNormalization(name='dense_norm'),
        tf.keras.layers.Dropout(0.2, name='dropout'),
        tf.keras.layers.Dense(3, activation='softmax', name='pred'),
        ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def conver_to_mfcc(vector_names, names, f, inputs, outputs):
    """
    take sound_file, and a vector that indicates each possibility speaker
    and slice it into pieces of 13 mfcc ( mel coeffs ) that indicates each
    slice of the sound file, than enter those pieces to "inputs" array and
    a number that indicates the speaker into "outputs" array
    :param vector_names: vector that indicates each possibility speaker with numbe
    :param names: names of the possibilty speakers
    :param f: sound file
    :param inputs: where the mfcc of the sound file will extend
    :param outputs: the speaker number will extend to here
    :return: the inputs and outputs arrays
    """
    if ' ' not in f.split('_')[0]:
        f_speaker = f.split('_')[0]
    else:
        f_speaker = f.split('_')[0].split(' ')[0]
    if f_speaker in names:
        (fs, audio) = wav.read('FinalAudios2\\' + f)  # read the file
        try:
            mfcc_feat = python_speech_features.mfcc(
                audio,
                samplerate=fs,
                winlen=win_len,
                winstep=step,
                nfft=nfft,
                appendEnergy=False,
            )
            for i in mfcc_feat:
                inputs.append(np.array(i))
                outputs.append(np.array(vector_names[names.index(f_speaker)]))
        except IndexError:
            pass
    else:
        pass
    return inputs, outputs


def model_creator(trainFiles, valFiles):
    """
    Create a model of machine learning in order to recognize
    the speaker of wav files in the trainFiles
    :param trainFiles: wav files path
    :return: model of tensorFlow
    """

    trainInputs = []  # inputs
    trainOutputs = []  # outputs
    valInputs = []
    valOutputs = []
    names = []  # names of the speakers
    for file in trainFiles:  # for each wav sound

        # UNESSECERY Outputs TO UNDERSTAND THE CODE

        if ' ' not in file.split('_')[0]:
            names.append(file.split('_')[0])
        else:
            names.append(file.split('_')[0].split(' ')[0])
    namesWithoutDuplicate = list(dict.fromkeys(names))
    namesWithoutDuplicateCopy = namesWithoutDuplicate[:]
    for name in namesWithoutDuplicateCopy:  # we remove low samples files
        if names.count(name) < 1:
            namesWithoutDuplicate.remove(name)
    names = namesWithoutDuplicate
    vector_names = []  # output for each name
    print(names)
    for i in range(len(names)):
        vector_for_each_name = i
        vector_names.append(np.array(vector_for_each_name))
    for f in trainFiles:  # for all the files
        trainInputs, trainOutputs = conver_to_mfcc(vector_names, names, f, trainInputs, trainOutputs)
    for f in valFiles:
        valInputs, valOutputs = conver_to_mfcc(vector_names, names, f, valInputs, valOutputs)

    Z = list(zip(trainInputs, trainOutputs))
    shuffle(Z)  # WE SHUFFLE trainInputs,trainOutputs TO PERFORM RANDOM ON THE TEST LEVEL
    (trainInputs, trainOutputs) = zip(*Z)
    trainInputs = list(trainInputs)
    trainOutputs = list(trainOutputs)
    valInputs = list(valInputs)
    valOutputs = list(valOutputs)
    # ------------------- RANDOMIZATION, UNNECESSARY Outputs TO UNDERSTAND THE CODE ------------------- #

    y_test = np.asarray(trainOutputs[:1])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_test = np.asarray(trainInputs[:1])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_train = np.asarray(trainInputs[1:])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    y_train = np.asarray(trainOutputs[1:])  # CHOOSE 100 FOR TEST, OTHERS FOR TRAIN
    x_val = np.asarray(valInputs[:])  # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    y_val = np.asarray(valOutputs[:])  # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    x_train = x_train[:]  # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    y_train = y_train[:]  # FROM THE TRAIN CHOOSE 100 FOR VALIDATION
    x_train = x_train.reshape(np.append(x_train.shape, (1, 1)))  # RESHAPE FOR INPUT
    x_test = x_test.reshape(np.append(x_test.shape, (1, 1)))  # RESHAPE FOR INPUT
    x_val = x_val.reshape(np.append(x_val.shape, (1, 1)))  # RESHAPE FOR INPUT

    model = machine_learning_model()

    print('fitting')
    history = model.fit(x_train, y_train, epochs=10,
                        validation_data=(x_val, y_val))
    print('testing')
    results.append(model.evaluate(x_test, y_test)[1])
    print(results)
    print(sum(results) / len(results))
    best_epochs = np.argmin(history.history['val_loss']) + 1
    model1 = machine_learning_model()
    model1.fit(x_train, y_train, epochs = best_epochs)
    return model1, names, vector_names


if __name__ == '__main__':
    trainFiles = [f for f in listdir('FinalAudios2')
                 if isfile(join('FinalAudios2', f))]  # Files in dir
    shuffle(trainFiles)
    testFiles = trainFiles[:100]
    trainFiles = trainFiles[100:]
    valFiles = []
    num = []

    testFilesCopy = [] + testFiles
    for id in tqdm(range(len(testFiles))):
        (fs, audio) = wav.read('FinalAudios2\\' + testFiles[id])  # read the file
        if len(audio) < 3 * fs:
            valFiles = valFiles + [testFiles[id]]
            testFilesCopy.remove(testFiles[id])
    (model1, names, vector_names) = model_creator(trainFiles, valFiles)
    testFiles = [] + testFilesCopy
    xTest = []
    yTest = []
    for id in tqdm(range(len(testFiles))):
        (fs, audio) = wav.read('FinalAudios2\\' + testFiles[id])  # read the file
        mfcc_feat = python_speech_features.mfcc(
            audio,
            samplerate=fs,
            winlen=win_len,
            winstep=step,
            nfft=nfft,
            appendEnergy=False,
            )
        trainInputs_now = []
        for i in mfcc_feat:
            trainInputs_now.append(np.array(i))
        trainInputs_now = np.asarray(trainInputs_now)
        trainInputs_now = trainInputs_now.reshape(trainInputs_now.shape + (1, 1))
        a = 0
        b = 0
        c = 0
        for i in range(len(trainInputs_now) - 1):
            predict = model1.predict_proba(trainInputs_now[i:i + 1])[0]
            if predict[0] == np.max(predict):
                a = a + 1
            elif predict[1] == np.max(predict):
                b = b + 1
            elif predict[2] == np.max(predict):
                c = c + 1
        decide = None
        if max([a, b, c]) == a:
            decide = names[0]
        elif max([a, b, c]) == b:
            decide = names[1]
        elif max([a, b, c]) == c:
            decide = names[2]
        if testFiles[id].split('_')[0] == decide:
            num = num + [1]
        else:
            num = num + [0]
        print(sum(num) / len(num))
