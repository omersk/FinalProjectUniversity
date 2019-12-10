import constants
import moviepy.editor as mp
import linecache
import timeUnion
import shutil
from scipy.io.wavfile import read, write
import matplotlib.pyplot as plt
import os
import sys
from os import listdir
from os.path import isfile, join
import numpy as np


def partition(alist, indices):
    return [alist[i:j] for i, j in zip([0]+indices, indices+[None])]


def cut_audio(name, start_time, end_time, folder_in="Audios", folder_out="SoloCutted"):
    """
    this is a function that came up to the world in order to cut audio into specific time
    :param name: name of file
    :param start_time: start time to cut
    :param end_time: end time to cut
    :param folder_in: folder we read the name ( folder + name == path )
    :param folder_out: folder we write the final version
    :return: nothing
    """
    try:
        input_data = read(folder_in + "/" + name + ".wav")  # input
    except IOError:
        # If the file is not in the folder in... than we take the file in audio
        # this is because we do -
        # endcut(file) : from Audios --> folder in
        # initialcut(file) : from folder in --> folder out
        # but sometimes we don't cut in the first function so we need to go to audios to find the file
        input_data = read("Audios" + "/" + name + ".wav")
    fs = input_data[0]  # the sample rate
    audio = input_data[1]  # the audio file
    try:
        audio = audio[:, 0]  # no mono audio file --> mono audio file
    except IndexError:
        # if it's already mono
        pass
    if not os.path.exists(folder_out):  # if path not exist we create it
        os.makedirs(folder_out)
    write(folder_out + "/" + name + ".wav", fs, audio[int(start_time*fs):int(end_time*fs)])  # we write the new file



def end_cut(name, words):
    """
    cut audio file in the end of them ( from silent + laugh )
    :param name: name of file
    :param words: what the talker said
    :return: how much seconds we cutted
    """
    # -------- SAME IDEA OF FUNCTION LIKE THE INITIAL CUT --------
    input_data = read("FinalAudios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    try:
        audio = audio[:, 0]
    except IndexError:
        pass
    minimum_cut_time = len(words.split(" ")) * 0.18 * fs
    if len(audio) > 2*fs:
        i = len(audio) - int(len(audio) * 0.3)
        if len(audio) / fs > 8:
            i = len(audio) - int(2 * fs)
        while i + 6000 < len(audio):
            if i > minimum_cut_time:
                if list(abs(j) > 200 for j in audio[i:i+10000]).count(True) < 500:
                    if i < fs:
                        i = float(i)
                    cut_audio(name, 0, i / fs, "FinalAudios", "FinalAudios")

                    return float(len(audio))/fs - float(i)/fs
            i = i + 1000
        return 0
    else:
        i = len(audio) - int(len(audio) * 0.6)
        while i + 6000 < len(audio):
            if list(abs(j) > 200 for j in audio[i:i+10000]).count(True) < 500:
                if i < fs:
                    i = float(i)
                cut_audio(name, 0, i / fs, "FinalAudios", "FinalAudios")

                return float(len(audio))/fs - float(i)/fs
            i = i + 1000
        return 0



def cutLaughSilent(path):
    input_data = read(path)
    fs = input_data[0]
    finalArray_0 = np.ndarray(0, dtype=np.int16)
    finalArray_1 = np.ndarray(0, dtype=np.int16)
    try:
        x = int(131072 / 2)
        if len(input_data[1][:, 0]) > x:
            index = x
            while index < len(input_data[1][:, 0]):
                try:
                    laughArrayIndexes = np.fft.ifft(np.fft.fft(input_data[1][index - x: index, 1]) - np.fft.fft(input_data[1][index - x: index, 0]))
                    laughArrayIndexes = [i for i, v in enumerate(laughArrayIndexes) if abs(v) > 100]
                    differenceBetweenElements = [j-i for i, j in zip(laughArrayIndexes[:-1], laughArrayIndexes[1:])]
                    splittingLaugh = [laughArrayIndexes[i] for i, v in enumerate(differenceBetweenElements) if v > 500]
                    t = ()
                    series = []
                    for element in laughArrayIndexes:
                        t = t + (element, )
                        if element in splittingLaugh:
                            if t[len(t) - 1] - t[0] > 10000-:
                                series = series + list(range(t[0], t[len(t) - 1]))
                            t = ()
                    if t and t[len(t) - 1] - t[0] > 10000:
                        series = series + list(range(t[0], t[len(t) - 1]))
                    finalArray_0 = np.concatenate((finalArray_0, np.delete(input_data[1][index - x: index, 0], series)), axis=None)
                    finalArray_1 = np.concatenate((finalArray_1, np.delete(input_data[1][index - x: index, 1], series)), axis=None)
                except IndexError:
                    pass
                index += x
            index = index - x
            try:
                laughArrayIndexes = np.fft.ifft(
                    np.fft.fft(input_data[1][index: len(input_data[1][:, 0]) - 1, 1]) - np.fft.fft(input_data[1][index: len(input_data[1][:, 0]) - 1, 0]))
                laughArrayIndexes = [i for i, v in enumerate(laughArrayIndexes) if abs(v) > 100]
                differenceBetweenElements = [j - i for i, j in zip(laughArrayIndexes[:-1], laughArrayIndexes[1:])]
                splittingLaugh = [laughArrayIndexes[i] for i, v in enumerate(differenceBetweenElements) if v > 500]
                t = ()
                series = []
                for element in laughArrayIndexes:
                    t = t + (element,)
                    if element in splittingLaugh:
                        series = series + list(range(t[0], t[len(t) - 1]))
                        t = ()
                if t:
                    series = series + list(range(t[0], t[len(t) - 1]))
                finalArray_0 = np.concatenate((finalArray_0, np.delete(input_data[1][index: len(input_data[1][:, 0]) - 1, 0], series)),
                                              axis=None)
                finalArray_1 = np.concatenate((finalArray_1, np.delete(input_data[1][index: len(input_data[1][:, 0]) - 1, 1], series)),
                                              axis=None)
            except IndexError:
                pass
            finalArray = np.zeros((len(finalArray_0), 2), dtype=np.int16)
            finalArray[:, 0] = finalArray_0
            finalArray[:, 1] = finalArray_1
            write('FinalAudios/' + path.split('/')[1], fs, finalArray)
        else:
            laughArrayIndexes = np.fft.ifft(
                np.fft.fft(input_data[1][:, 1]) - np.fft.fft(input_data[1][:, 0]))
            laughArrayIndexes = [i for i, v in enumerate(laughArrayIndexes) if abs(v) > 100]
            differenceBetweenElements = [j - i for i, j in zip(laughArrayIndexes[:-1], laughArrayIndexes[1:])]
            splittingLaugh = [laughArrayIndexes[i] for i, v in enumerate(differenceBetweenElements) if v > 500]
            t = ()
            series = []
            for element in laughArrayIndexes:
                t = t + (element,)
                if element in splittingLaugh:
                    if t[len(t) - 1] - t[0] > 10000:
                        series = series + list(range(t[0], t[len(t) - 1]))
                    t = ()
            if t and t[len(t) - 1] - t[0] > 10000:
                series = series + list(range(t[0], t[len(t) - 1]))
            finalArray_0 = np.concatenate((finalArray_0, np.delete(input_data[1][:, 0], series)),
                                          axis=None)
            finalArray_1 = np.concatenate((finalArray_1, np.delete(input_data[1][:, 1], series)),
                                          axis=None)
            finalArray = np.zeros((len(finalArray_0), 2), dtype=np.int16)
            finalArray[:, 0] = finalArray_0
            finalArray[:, 1] = finalArray_1
            write('FinalAudios/' + path.split('/')[1], fs, finalArray)

    except IndexError:
        pass


def split_speakers(name, next_name):
    """
    cut file at his middle ( in order to make 2 talkers into 2 files )
    :param name: name of file
    :param next_name: the name of the second speaker
    :return: nothing
    """
    input_data = read("Audios/" + name + ".wav")  # read the file
    fs = input_data[0]  # sample rate
    audio = input_data[1]  # audio file
    try:
        audioMono = audio[:, 0]  # stereo --> mono
    except IndexError:
        # if it's already mono
        pass
    arrCut = []  # the array we will work with
    for i in range(0, len(audioMono), 3000):  # we run on i in the following - 0, 3000, 6000, ...., len(audio)
        if max(abs(j) for j in audioMono[i:i + 6000]) < 200:  # if there is silent
            arrCut.append(i)  # we append it to the array
    BiggestDiff = max(
        arrCut[j + 1] - arrCut[j] for j in range(len(arrCut) - 1))  # we check where was the longest silent
    i = 0
    while i < len(arrCut) - 1:  # check which index is the biggest difference, than we take audio[i] + BiggestDiff/2
        if arrCut[i + 1] - arrCut[i] == BiggestDiff:
            break
        i = i + 1
    write("Audios/" + name + ".wav", fs, audio[0:int(arrCut[i] + BiggestDiff / 2), :])
    cutLaughSilent("Audios/" + name + ".wav")
    write("Audios/" + next_name + ".wav", fs, audio[int(arrCut[i] + BiggestDiff / 2) + 1: len(audio) - 1, :])
    cutLaughSilent("Audios/" + next_name + ".wav")


def main_action():
    """
    cut movie into specific audio files with 0.2 sec
    by the script and srt files. And remove laugh + silent audios.
    :return:
    """
    if not os.path.exists("Audios"):  # if the dir doesn't exist we create one
        os.makedirs("Audios")
    if not os.path.exists("FinalAudios"):  # if the dir doesn't exist we create one
        os.makedirs("FinalAudios")
    num = str(input("espiode number : "))
    filename = constants.outputfile
    i = 1
    j = 1
    cutted_last = 0  # how much we cut last file
    while True:
        if not linecache.getline(filename, i + 4):  # end of file
            break
        time = linecache.getline(filename, i).split(".")[1].lstrip().rstrip()  # time of the specific line
        if not time == "00:00:00,000 --> 00:00:00,000":  # if it's in the srt
            name = linecache.getline(filename, i + 1).lstrip().rstrip()  # name of the speaker
            words = linecache.getline(filename, i + 3).lstrip().rstrip()  # what he said
            print(time)
            print(name)
            t = timeUnion.timeUnion(time)
            start_time = t.getInitialTimeInSec()  # start time
            end_time = t.getEndTimeInSec()  # end time
            if time == linecache.getline(filename, i + 4).split(".")[1].lstrip().rstrip():  # if there is 2
                try:
                    # speakers in one line
                    nameAfter = linecache.getline(filename, i + 5).lstrip().rstrip()  # name of the speaker
                    wordsAfter = linecache.getline(filename, i + 7).lstrip().rstrip()  # what the second speaker said
                    clip = mp.VideoFileClip("Movie_" + num + ".mp4").subclip(start_time - cutted_last - 0.5, end_time)  # cutting the
                    # audio
                    clip.audio.write_audiofile(name + "_" + num + "_" + str(j) + ".wav")  # write it into new file
                    shutil.move(name + "_" + num + "_" + str(j) + ".wav", "Audios/" + name + "_" + num + "_" + str(j) + ".wav")  # move it to the # dir
                    # There Are Two Speakers
                    split_speakers(name + "_" + num + "_" + str(j), nameAfter + "_" + num + "_" + str(j+1))
                    cutted_last = end_cut(nameAfter + "_" + str(num) + "_" + str(j+1), wordsAfter)  # end cut to the second speaker
                    i += 4  # next speaker
                    j += 1  # next speaker
                except Exception as e:
                    # if there is an exception; we move to the next element...
                    print(e.__doc__)
                    cutted_last = 0
                    i += 4  # next speaker
                    j += 1  # next speaker
            else:
                clip = mp.VideoFileClip("Movie_" + num + ".mp4").subclip(start_time - cutted_last,
                                                                         end_time)  # cutting the
                # audio
                clip.audio.write_audiofile(name + "_" + num + "_" + str(j) + ".wav")  # write it into new file
                shutil.move(name + "_" + num + "_" + str(j) + ".wav",
                            "Audios/" + name + "_" + num + "_" + str(j) + ".wav")  # move it to the dir
                cutLaughSilent("Audios/" + name + "_" + num + "_" + str(j) + ".wav")
                cutted_last = end_cut(name + "_" + str(num) + "_" + str(j), words)  # end cut to the second speaker
        i += 4  # next speaker
        j += 1  # next speaker


if __name__ == '__main__':
    main_action()