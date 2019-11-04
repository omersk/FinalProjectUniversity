import moviepy.editor as mp
import linecache
import timeUnion
import shutil


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

