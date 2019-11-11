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

def cut_audio(name, start_time, end_time, folder_in, folder_out):
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


def playSound(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()



def initial_cut(name, words):
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, 0]
    audioSaver = []
    for i in audio:
        audioSaver.append(i)
    i = 1
    if max(abs(j) for j in audio[0:i]) < 100:
        i = i + 10000
        while max(abs(j) for j in audio[i-10000:i]) < 100:
            i = i + 10000
        cut_audio(name, float(i)/fs, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")
    audio = audioSaver
    i = 1
    if list(abs(j) < 400 for j in audio[0:i]).count(True) < i/2 + 1000:
        i = i + 10000
        while list(abs(j) < 400 for j in audio[i-10000:i]).count(True) < 5000:
            i = i + 10000
        cut_audio(name, float(i)/fs, len(audio) - 1, "AfterCuttedAudios", "AfterInitialCuttedAudios")



def end_cut(name, words):
    input_data = read("Audios/" + name + ".wav")
    fs = input_data[0]
    audio = input_data[1]
    audio = audio[:, 0]

    minimum_cut_time = len(words.split(" ")) * 0.18 * fs
    print minimum_cut_time
    i = len(audio) - int(len(audio) * 0.3)
    if len(audio)/fs > 8:
        i = len(audio) - int(2 * fs)
    print len(words.split(" "))
    while i + 6000 < len(audio):
        if i > minimum_cut_time:
            if max(abs(j) for j in audio[i:i+6000]) < 100:
                # --> works less good, see s7, need improvements:
                # cut_audio(name, 0, i/fs + 0.2, "Audios", "AfterCuttedAudios")
                cut_audio(name, 0, i / fs, "Audios", "AfterCuttedAudios")
                print i / fs
                print i / fs + 0.2
                return float(len(audio))/fs - float(i)/fs
            elif list(abs(j) < 400 for j in audio[i:i+10000]).count(True) < 4500:
                print i / fs
                print i / fs + 0.2
                # --> works less good, see s7, need improvements:
                #cut_audio(name, 0, i/fs + 0.2, "Audios", "AfterCuttedAudios")
                cut_audio(name, 0, i / fs, "Audios", "AfterCuttedAudios")
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
            cutted_last = end_cut("s" + str(j), words)
            initial_cut("s" + str(j), words)
            i += 4
            j += 1

        except IndexError:
            j += 1
            i += 3