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


def initial_cut(name, should_I_wanna_cut=True):
    """
    cut audio file in the beginning of them ( from silent + laugh )
    :param name: name of file
    :param words: what the man said
    :return: nothing
    """
    input_data = read("Audios/" + name + ".wav")  # read the file
    fs = input_data[0]  # sample rate
    audio = input_data[1]  # audio file
    try:
        audio = audio[:, 0]  # stereo --> mono
    except IndexError:
        # if it's already mono
        pass
    if should_I_wanna_cut:
        i = 1000
        doescutted = False  # boolean variable that indicates if we cut
        # ------- SILENT'S CUTTING -------
        if max(abs(j) for j in audio[0:i]) < 100:  # if the max absolute value of the next 1000 elements is silent
            i = i + 10000  # check the next 10000
            while max(abs(j) for j in audio[i-10000:i]) < 100:  # while there is silent
                i = i + 10000
            cut_audio(name, float(i)/fs, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")  # we cut
            # the silent
            doescutted = True
        # ------- SILENT'S CUTTING -------

        # if there was silent, we modify our audio file into the new audio file after cutting the silent, and than we
        # go into cutting laugh
        if doescutted == True:  # if we cut, we try to now cut the f
            input_data = read("AfterInitialCuttedAudios/" + name + ".wav")
            fs = input_data[0]
            audio = input_data[1]
            try:
                audio = audio[:, 0]
            except IndexError:
                pass
        i = 10000
        # ------- LAUGH CUTTING -------
        if list(abs(j) < 400 for j in audio[0:i]).count(True) < 6800:
            # laugh characterize with small number of zero's; therefore we count the number of zero's and check if there
            # were a few or a lot
            i = i + 10000
            while list(abs(j) < 400 for j in audio[i-5000:i]).count(True) < 4000 and i < len(audio):  # while there is laugh
                i = i + 5000
            cut_audio(name, float(i)/fs, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")

            doescutted = True
        # ------- LAUGH CUTTING -------
        if not doescutted:  # if there is no needing to cut, we just write the file as he now
            cut_audio(name, 0, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")
    else:
        cut_audio(name, 0, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")


def middle_cut(name, next_name):
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
        audio = audio[:, 0]  # stereo --> mono
    except IndexError:
        # if it's already mono
        pass
    arrCut = []  # the array we will work with
    for i in range(0, len(audio), 3000):  # we run on i in the following - 0, 3000, 6000, ...., len(audio)
        if max(abs(j) for j in audio[i:i+6000]) < 200:  # if there is silent
            arrCut.append(i)  # we append it to the array
    BiggestDiff = max(arrCut[j+1] - arrCut[j] for j in range(len(arrCut) - 1))  # we check where was the longest silent
    i = 0
    while i < len(arrCut) - 1:  # check which index is the biggest difference, than we take audio[i] + BiggestDiff/2
        if arrCut[i+1] - arrCut[i] == BiggestDiff:
            break
        i = i + 1
    write("Audios/" + name + ".wav", fs, audio[0:int(arrCut[i] + BiggestDiff/2)])
    write("Audios/" + next_name + ".wav", fs, audio[int(arrCut[i] + BiggestDiff/2) + 1: len(audio) - 1])

def end_cut(name, words):
    """
    cut audio file in the end of them ( from silent + laugh )
    :param name: name of file
    :param words: what the talker said
    :return: how much seconds we cutted
    """
    # -------- SAME IDEA OF FUNCTION LIKE THE INITIAL CUT --------
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    try:
        audio = audio[:, 0]
    except IndexError:
        pass
    minimum_cut_time = len(words.split(" ")) * 0.18 * fs
    i = len(audio) - int(len(audio) * 0.3)
    if len(audio)/fs > 8:
        i = len(audio) - int(2 * fs)
    while i + 6000 < len(audio):
        if i > minimum_cut_time:
            if max(abs(j) for j in audio[i:i+6000]) < 200:
                if i < fs:
                    i = float(i)
                cut_audio(name, 0, i / fs, "Audios", "AfterCuttedAudios")

                return float(len(audio))/fs - float(i)/fs

            elif list(abs(j) < 400 for j in audio[i:i+10000]).count(True) < 4500:
                cut_audio(name, 0, float(i) / fs, "Audios", "AfterCuttedAudios")
                return 0
        i = i + 1000
    return 0


def frange(x, y, jump):
    """
    range for float numbers
    :param x:
    :param y:
    :param jump:
    :return: same as range for float numbers
    """
    while x < y:
        yield x
        x += jump

def two_seconds_every_file():
    onlyfiles = [f for f in listdir("AfterInitialCuttedAudios/") if isfile(join("AfterInitialCuttedAudios/", f))]
    if not os.path.exists("FinalAudios"):  # if the dir doesn't exist we create one
        os.makedirs("FinalAudios")
    for f in onlyfiles:
        input_data = read("AfterInitialCuttedAudios/" + f)  # read the file
        fs = input_data[0]  # sample rate
        audio = input_data[1]  # audio file
        try:
            audio = audio[:, 0]  # stereo --> mono
        except IndexError:
            # if it's already mono
            pass
        t = fs/5
        j = 0
        while t < len(audio):
            write("FinalAudios/" + f.split(".")[0] + "_" + str(j) + ".wav", fs, audio[t-fs/5:t-1])
            t += fs/5
            j += 1


def cut_laugh_and_silent():
    onlyfiles = [f for f in listdir("FinalAudios/") if isfile(join("FinalAudios/", f))]
    if not os.path.exists("LaughOrSilent"):  # if the dir doesn't exist we create one
        os.makedirs("LaughOrSilent")
    for f in onlyfiles:
        input_data = read("FinalAudios/" + f)  # read the file
        fs = input_data[0]  # sample rate
        audio = input_data[1]  # audio file
        if list(abs(j) < 400 for j in audio[0:len(audio) - 1]).count(True) < 600 or max(abs(j) for j in audio[0:len(audio) - 1]) < 400:
            shutil.move("FinalAudios/" + f, "LaughOrSilent/" + f)
def plot_graph(name):
    """
    plot the sound file
    :param name: name of the file
    :return: nothing
    """
    # read audio samples
    input_data = read("FinalAudios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    # plot the first 1024 samples
    fs = 1
    try:
        audio = audio[:, 0]
    except IndexError:
        pass
    plt.plot(list(frange(0.0, len(audio)*1.0/fs, 1.0/fs))[0:len(audio)], audio)
    # label the axes
    plt.ylabel("Amplitude")
    plt.xlabel("Time")
    # set the title
    plt.title("Sample Wav")
    # display the plot
    plt.show()

if len(sys.argv) == 2:
    plot_graph(sys.argv[1])
elif len(sys.argv) == 3:
    two_seconds_every_file()
elif len(sys.argv) == 4:
    cut_audio(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
elif len(sys.argv) == 5:
    cut_laugh_and_silent()
else:
    filename = constants.outputfile
    i = 1
    j = 1
    cutted_last = 0  # how much we cut last file
    while True:
        if not linecache.getline(filename, i):  # end of file
            break
        time = linecache.getline(filename, i).split(".")[1].lstrip().rstrip()  # time of the specific line
        if not time == "00:00:00,000 --> 00:00:00,000":  # if it's in the srt
            name = linecache.getline(filename, i + 1).lstrip().rstrip()  # name of the speaker
            words = linecache.getline(filename, i + 3).lstrip().rstrip()  # what he said
            print time
            print name
            t = timeUnion.timeUnion(time)
            start_time = t.getInitialTimeInSec()  # start time
            end_time = t.getEndTimeInSec()  # end time
            if time == linecache.getline(filename, i + 4).split(".")[1].lstrip().rstrip():  # if there is 2
                try:
                    # speakers in one line
                    nameAfter = linecache.getline(filename, i + 5).lstrip().rstrip()  # name of the speaker
                    wordsAfter = linecache.getline(filename, i + 7).lstrip().rstrip()  # what the second speaker said
                    clip = mp.VideoFileClip("Movie.mp4").subclip(start_time - cutted_last - 0.5, end_time)  # cutting the
                    # audio
                    clip.audio.write_audiofile(name + "_" + str(j) + ".wav")  # write it into new file
                    if not os.path.exists("Audios"):  # if the dir doesn't exist we create one
                        os.makedirs("Audios")
                    shutil.move(name + "_" + str(j) + ".wav", "Audios/" + name + "_" + str(j) + ".wav")  # move it to the # dir
                    # There Are Two Speakers
                    middle_cut(name + "_" + str(j), nameAfter + "_" + str(j+1))  # 2 speakers; 1 file --> 1 speaker; 2 files
                    initial_cut(name + "_" + str(j))  # initial cut to the first speaker
                    cutted_last = end_cut(nameAfter + "_" + str(j+1), wordsAfter)  # end cut to the second speaker
                    initial_cut(nameAfter + "_" + str(j+1), False)
                    i += 4  # next speaker
                    j += 1  # next speaker
                except Exception as e:
                    # if there is an exception; we move to the next element...
                    print e.__doc__
                    print e.message
                    i += 4  # next speaker
                    j += 1  # next speaker
            else:
                try:
                    clip = mp.VideoFileClip("Movie.mp4").subclip(start_time - cutted_last, end_time)  # cutting the
                    # audio
                    clip.audio.write_audiofile(name + "_" + str(j) + ".wav")  # write it into new file
                    if not os.path.exists("Audios"):  # if the dir doesn't exist we create one
                        os.makedirs("Audios")
                    shutil.move(name + "_" + str(j) + ".wav", "Audios/" + name + "_" + str(j) + ".wav")  # move it to the dir
                    # There Are Two Speakers
                    cutted_last = end_cut(name + "_" + str(j), words)  # end cut to the speaker
                    initial_cut(name + "_" + str(j))  # initial cut to the first speaker
                except Exception as e:
                    # if there is an exception; we move to the next element...
                    print e.__doc__
                    print e.message
        i += 4  # next speaker
        j += 1  # next speaker