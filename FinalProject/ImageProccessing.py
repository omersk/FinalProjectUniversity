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
import cv2
from skimage.measure import compare_ssim
import time
def main_action():
    """
    cut movie into specific audio files with 0.2 sec
    by the script and srt files. And remove laugh + silent audios.
    :return:
    """
    if not os.path.exists("data"):  # if the dir doesn't exist we create one
        os.makedirs("data")
    num = str(input("espiode number : "))
    filename = "outputfilenew_" + num + ".txt"
    i = 1
    j = 1
    cutted_last = 0  # how much we cut last file
    while True:
        if not linecache.getline(filename, i + 4):  # end of file
            break
        time = linecache.getline(filename, i).split(".")[1].lstrip().rstrip()  # time of the specific line
        last_image = 1
        if not time == "00:00:00,000 --> 00:00:00,000":  # if it's in the srt
            try:
                name = linecache.getline(filename, i + 1).lstrip().rstrip()  # name of the speaker
                words = linecache.getline(filename, i + 3).lstrip().rstrip()  # what he said
                print(time)
                print(name)
                t = timeUnion.timeUnion(time)
                start_time = t.getInitialTimeInSec()  # start time
                end_time = t.getEndTimeInSec()  # end time
                if time == linecache.getline(filename, i + 4).split(".")[1].lstrip().rstrip():  # if there is 2
                    i += 4  # next speaker
                    j += 1  # next speaker
                else:
                    if end_time - start_time < 15:
                        breaked = False
                        # PreCheck
                        vidcap = cv2.VideoCapture('Movie_' + str(num) + '.mp4')
                        for second in np.arange(start_time + 0.2, end_time - 0.2, 0.01):
                            vidcap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # just cue to 20 sec. position
                            success, image = vidcap.read()
                            if success:
                                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                if type(last_image) == int:
                                    last_image = gray
                                (score, diff) = compare_ssim(gray, last_image, full=True)
                                #                        print("SSIM: {}".format(score))
                                if score < 0.4:
                                    breaked = True
                                    print(name, int(second * 1000))
                                    print("------------------- BREAKED -------------------")
                                    break
                        if not breaked:
                            face_crop = []
                            if linecache.getline(filename, i + 5).lstrip().rstrip() == name:
                                timeAfter = linecache.getline(filename, i + 4).split(".")[
                                    1].lstrip().rstrip()  # time of the specific line
                                tAfter = timeUnion.timeUnion(timeAfter)
                                start_time_after = tAfter.getInitialTimeInSec()  # start time
                                end_time_after = tAfter.getEndTimeInSec()  # end time
                                for second in np.arange(start_time + 0.2, end_time - 0.2, 0.01):
                                    #                        print(name, int(second * 1000))
                                    vidcap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # just cue to 20 sec. position
                                    success, image = vidcap.read()
                                    if success:
                                        face_cascade = cv2.CascadeClassifier(
                                            "haarcascade_profileface.xml")
                                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                        gray = gray[0:380, 0:2400]
                                        image = image[0:380, 0:2400]
                                        fliped = cv2.flip(gray, 1)
                                        fliped_image = cv2.flip(image, 1)
                                        faces1 = face_cascade.detectMultiScale(gray, 1.3, 5)
                                        faces2 = face_cascade.detectMultiScale(fliped, 1.3, 5)
                                        if type(last_image) == int:
                                            last_image = gray
                                        for f in faces1:
                                            x, y, w, h = [v for v in f]
                                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
                                            # Define the region of interest in the image
                                            face_crop.append(image[y:y + h, x:x + w])
                                        for f in faces2:
                                            x, y, w, h = [v for v in f]
                                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
                                            # Define the region of interest in the image
                                            face_crop.append(cv2.flip(fliped_image[y:y + h, x:x + w], 1))
                                for second in np.arange(start_time_after + 0.2, end_time_after - 0.2, 0.01):
                                    #                        print(name, int(second * 1000))
                                    vidcap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # just cue to 20 sec. position
                                    success, image = vidcap.read()
                                    if success:
                                        face_cascade = cv2.CascadeClassifier(
                                            "haarcascade_profileface.xml")
                                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                        gray = gray[0:380, 0:2400]
                                        image = image[0:380, 0:2400]
                                        fliped = cv2.flip(gray, 1)
                                        fliped_image = cv2.flip(image, 1)
                                        faces1 = face_cascade.detectMultiScale(gray, 1.3, 5)
                                        faces2 = face_cascade.detectMultiScale(fliped, 1.3, 5)
                                        if type(last_image) == int:
                                            last_image = gray
                                        for f in faces1:
                                            x, y, w, h = [v for v in f]
                                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
                                            # Define the region of interest in the image
                                            face_crop.append(image[y:y + h, x:x + w])
                                        for f in faces2:
                                            x, y, w, h = [v for v in f]
                                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
                                            # Define the region of interest in the image
                                            face_crop.append(cv2.flip(fliped_image[y:y + h, x:x + w], 1))
                            else:
                                for second in np.arange(start_time + 0.2, end_time - 0.2, 0.01):
                                    #                        print(name, int(second * 1000))
                                    vidcap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)  # just cue to 20 sec. position
                                    success, image = vidcap.read()
                                    if success:
                                        face_cascade = cv2.CascadeClassifier(
                                            "haarcascade_profileface.xml")
                                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                        gray = gray[0:380, 0:2400]
                                        image = image[0:380, 0:2400]
                                        fliped = cv2.flip(gray, 1)
                                        fliped_image = cv2.flip(image, 1)
                                        faces1 = face_cascade.detectMultiScale(gray, 1.3, 5)
                                        faces2 = face_cascade.detectMultiScale(fliped, 1.3, 5)
                                        if type(last_image) == int:
                                            last_image = gray
                                        for f in faces1:
                                            x, y, w, h = [v for v in f]
                                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
                                            # Define the region of interest in the image
                                            face_crop.append(image[y:y + h, x:x + w])
                                        for f in faces2:
                                            x, y, w, h = [v for v in f]
                                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
                                            # Define the region of interest in the image
                                            face_crop.append(cv2.flip(fliped_image[y:y + h, x:x + w], 1))

                            print(len(face_crop))
                            wasBreaked = False
                            min_1, min_2 = (500, 500)
                            for face in face_crop:
                                if face.shape[0] < min_1:
                                    min_1 = face.shape[0]
                                if face.shape[1] < min_2:
                                    min_2 = face.shape[1]
                            minScore = 1
                            for face_i in range(0, len(face_crop) - 1):
                                face = face_crop[face_i]
                                face_next = face_crop[face_i + 1]
                                (score, diff) = compare_ssim(face[int((face.shape[0] - min_1)/2):int((face.shape[0] + min_1)/2), int((face.shape[1] - min_2)/2):int((face.shape[1] + min_2)/2)], face_next[int((face_next.shape[0] - min_1)/2):int((face_next.shape[0] + min_1)/2), int((face_next.shape[1] - min_2)/2):int((face_next.shape[1] + min_2)/2)], full=True,
                                                             multichannel=True)
                                if minScore > score:
                                    minScore = score
                                if score < 0.4:
                                    print(score)
                                    wasBreaked = True
                                    break
                            if not wasBreaked:
                                print("MinScore :")
                                print(minScore)
                                a = 0
                                for face in face_crop:
                                    w, h, z = face.shape
                                    if w > 65 and h > 65:
                                        a = a + 1
                                        cv2.imwrite(
                                            "data\\" + name + "_" + str(num) + "_" + str(j) + "_" + str(a) + ".jpg",
                                            face)  # save frame as JPEG file
            except:
                pass
        i += 4  # next speaker
        j += 1  # next speaker


if __name__ == '__main__':
    main_action()
