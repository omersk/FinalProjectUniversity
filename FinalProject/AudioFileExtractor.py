import constants
import moviepy.editor as mp
import linecache
import timeUnion
import shutil
from scipy.io.wavfile import read, write
import os
import numpy as np


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
                            if t[len(t) - 1] - t[0] > 10000:
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
    filename = constants.outputfile.split(".txt")[0] + "_" + num + ".txt"
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
                    clip = mp.VideoFileClip("Movie_" + num + ".mp4").subclip(start_time, end_time)  # cutting the
                    # audio
                    clip.audio.write_audiofile(name + "_" + num + "_" + str(j) + ".wav")  # write it into new file
                    shutil.move(name + "_" + num + "_" + str(j) + ".wav", "Audios/" + name + "_" + num + "_" + str(j) + ".wav")  # move it to the # dir
                    # There Are Two Speakers
                    split_speakers(name + "_" + num + "_" + str(j), nameAfter + "_" + num + "_" + str(j+1))
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
        i += 4  # next speaker
        j += 1  # next speaker


if __name__ == '__main__':
    main_action()