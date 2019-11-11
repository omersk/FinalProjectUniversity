import constants
import moviepy.editor as mp
import linecache
import timeUnion
import shutil
from scipy.io.wavfile import read, write
import matplotlib.pyplot as plt
import os
import pygame
from constants import get_sec

a = raw_input("name : ")

def cut_audio(name, start_time, end_time):
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, ]
    if not os.path.exists("AfterCuttedAudios"):
        os.makedirs("AfterCuttedAudios")
    write("AfterCuttedAudios/" + name + ".wav", fs, audio[int(start_time*fs):int(end_time*fs)])


def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()



def remove_another_talker(name, words):
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, 0]

    minimum_cut_time = len(words.split(" ")) * 0.18 * fs
    print minimum_cut_time
    i = len(audio) - int(len(audio) * 0.3)
    print len(words.split(" "))
    while i + 6000 < len(audio):
        if i > minimum_cut_time:
            if max(abs(j) for j in audio[i:i+6000]) < 100:
                cut_audio(name, 0, i/fs)
                return float(len(audio))/fs - float(i)/fs
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
    print fs
    # plot the first 1024 samples
    plt.plot(list(frange(0.0, len(audio)*1.0/fs, 1.0/fs))[0:len(audio)], audio[:, 0])
    # label the axes
    plt.ylabel("Amplitude")
    plt.xlabel("Time")
    # set the title
    plt.title("Sample Wav")
    # display the plot
    plt.show()


if len(a) > 0:
    if len(a.split(" ")) < 2:
        plot_graph(a)
    elif len(a.split(" ")) == 3:
        cut_audio(a.split(" ")[0], float(a.split(" ")[1]), float(a.split(" ")[2]))
#if len(sys.argv) >= 2:
#    plot_graph(sys.argv[1])

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
            cutted_last = remove_another_talker("s" + str(j), words)
            i += 4
            j += 1

        except IndexError:
            j += 1
            i += 3