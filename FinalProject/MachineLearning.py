import constants
import moviepy.editor as mp
import linecache
import timeUnion
import shutil
from scipy.io.wavfile import read, write
import matplotlib.pyplot as plt
import os
import sys


def cut_audio(name, start_time, end_time, folder_in="Audios", folder_out="SoloCutted"):
    try:
        input_data = read(folder_in + "/" + name + ".wav")
    except IOError:
        input_data = read("Audios" + "/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, ]
    if not os.path.exists(folder_out):
        os.makedirs(folder_out)
    write(folder_out + "/" + name + ".wav", fs, audio[int(start_time*fs):int(end_time*fs)])


def initial_cut(name, words):
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, 0]
    i = 1
    doescutted = False
    if max(abs(j) for j in audio[0:i]) < 100:
        i = i + 10000
        while max(abs(j) for j in audio[i-10000:i]) < 100:
            i = i + 10000
        cut_audio(name, float(i)/fs, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")
        doescutted = True
    if doescutted == True:
        input_data = read("AfterInitialCuttedAudios/" + name + ".wav")
        fs = input_data[0]
        audio = input_data[1]
        audio = audio[:, 0]
    i = 10000
    print list(abs(j) < 400 for j in audio[0:i]).count(True)
    if list(abs(j) < 400 for j in audio[0:i]).count(True) < 6800:
        i = i + 10000
        while list(abs(j) < 400 for j in audio[i-5000:i]).count(True) < 4000:
            i = i + 5000
        cut_audio(name, float(i)/fs, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")
        doescutted = True
    if not doescutted:
        cut_audio(name,0,len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")

def end_cut(name, words):
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, 0]

    minimum_cut_time = len(words.split(" ")) * 0.18 * fs
    i = len(audio) - int(len(audio) * 0.3)
    if len(audio)/fs > 8:
        i = len(audio) - int(2 * fs)
    while i + 6000 < len(audio):
        if i > minimum_cut_time:
            if max(abs(j) for j in audio[i:i+6000]) < 200:
                # --> works less good, see s7, need improvements:
                # cut_audio(name, 0, i/fs + 0.2, "Audios", "AfterCuttedAudios")
                cut_audio(name, 0, i / fs, "Audios", "AfterCuttedAudios")
                print 'ballasdlasldalsdldsaldsal'
                print i
                return float(len(audio))/fs - float(i)/fs

            elif list(abs(j) < 400 for j in audio[i:i+10000]).count(True) < 4500:
                # --> works less good, see s7, need improvements:
                #cut_audio(name, 0, i/fs + 0.2, "Audios", "AfterCuttedAudios")
                print 'asddsadas'
                print i
                cut_audio(name, 0, float(i) / fs, "Audios", "AfterCuttedAudios")
                return 0

        i = i + 1000
    return 0


def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


def plot_graph(name):
    # read audio samples
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    # plot the first 1024 samples
    fs = 1
    plt.plot(list(frange(0.0, len(audio)*1.0/fs, 1.0/fs))[0:len(audio)], audio[:, 0])
    # label the axes
    plt.ylabel("Amplitude")
    plt.xlabel("Time")
    # set the title
    plt.title("Sample Wav")
    # display the plot
    plt.show()


if len(sys.argv) == 2:
    plot_graph(sys.argv[1])
elif len(sys.argv) == 4:
    cut_audio(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
else:
    filename = constants.outputfile
    i = 1
    j = 1
    cutted_last = 0
    while True:
        if not linecache.getline(filename, i):
            break
        try:
            time = linecache.getline(filename, i).split(".")[1].lstrip().rstrip()
            name = linecache.getline(filename, i + 1).lstrip().rstrip()
            words = linecache.getline(filename, i + 3).lstrip().rstrip()
            print time
            print name
            t = timeUnion.timeUnion(time)
            start_time = t.getInitialTimeInSec()
            end_time = t.getEndTimeInSec()
            clip = mp.VideoFileClip("Movie.mp4").subclip(start_time - cutted_last, end_time)
            clip.audio.write_audiofile(name + "_" + str(j) + ".wav")
            if not os.path.exists("Audios"):
                os.makedirs("Audios")
            shutil.move(name + "_" + str(j) + ".wav", "Audios/s" + str(j) + ".wav")
            cutted_last = end_cut("s" + str(j), words)
            initial_cut("s" + str(j), words)
            i += 4
            j += 1

        except IndexError:
            j += 1
            i += 3