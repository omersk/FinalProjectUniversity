import constants
import moviepy.editor as mp
import linecache
import timeUnion
import shutil
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import sys


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


if len(sys.argv) >= 2:
    plot_graph(sys.argv[1])

else:
    filename = "outputfilenew.txt"
    i = 1
    j = 1
    while True:
        if not linecache.getline(filename, i):
            break
        try:
            time = linecache.getline(filename, i).split(".")[1].lstrip().rstrip()
            name = linecache.getline(filename, i + 1).lstrip().rstrip()
            print time
            print name
            t = timeUnion.timeUnion(time)
            start_time = t.getInitialTimeInSec()
            end_time = t.getEndTimeInSec()
            clip = mp.VideoFileClip("Movie.mp4").subclip(start_time, end_time)
            clip.audio.write_audiofile(name + "_" + str(j) + ".wav")
            shutil.move(name + "_" + str(j) + ".wav", "Audios/s" + str(j) + ".wav")
            i += 4
            j += 1

        except IndexError:
            j += 1
            i += 3