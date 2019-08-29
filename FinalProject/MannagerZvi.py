import DropBoxDownloader
import RegexMaker
from difflib import SequenceMatcher
import scipy.stats
import timeUnion
from tqdm import tqdm
import constants
import numpy
import heapq
import operator


class MannagerZvi:
    def __init__(self, script_file_path, regex_script, regex_srt, srt_file_path, access_token):
        self.script_file_path = script_file_path
        self.regex_script = regex_script
        self.regex_srt = regex_srt
        self.srt_file_path = srt_file_path
        self.access_token = access_token
        self.dict_position = {}

    def main_action(self, url_script, url_srt, num_of_lines, output_file):
        d = DropBoxDownloader.DropBoxDownloader(self.access_token)
        d.download_file(url_script, self.script_file_path)
        d.download_file(url_srt, self.srt_file_path)
        rm = RegexMaker.RegexMaker(self.script_file_path, self.regex_script, self.regex_srt, self.srt_file_path)
        rm.find_matches_script()
        rm.find_matches_srt()
        sumScript = sum(rm.dict_words_script.values())
        sumSrt = sum(rm.dict_words_srt.values())
        arr_lines = [(0,)]
        for lineScriptIndex in tqdm(range(len(rm.arr_words_script))):
            lineScript = rm.arr_words_script[lineScriptIndex]
            line_matrix = numpy.zeros((len(lineScript.split(" ")), len(rm.arr_words_srt)))
            for lineSrtIndex in range(len(rm.arr_words_srt)):
                lineSrt = rm.arr_words_srt[lineSrtIndex]
                for wordIndex in range(len(lineScript.split(' '))):
                    word = lineScript.split(' ')[wordIndex]
                    if word in lineSrt.split(' '):
                        line_matrix[wordIndex][lineSrtIndex] = float((sumSrt-rm.dict_words_srt[word]))/float(sumSrt) * float((sumScript-rm.dict_words_script[word]))/float(sumScript)
            array_winners = numpy.dot(numpy.ones((1, len(lineScript.split(" ")))), line_matrix)
            indexed = list(enumerate(array_winners[0]))
            top_10 = sorted(indexed, key=operator.itemgetter(1))[-10:]
            top_10 = sorted(list(reversed([i for i, v in top_10])))
            t = []
            distanceFromLastResult = []
            xSorted = sorted(top_10)
            t.append((xSorted[0],))
            j = 0
            for i in range(len(xSorted) - 1):
                if xSorted[i+1] - xSorted[i] != 1 or SequenceMatcher(None, lineScript, rm.arr_words_srt[xSorted[i]]).ratio() > SequenceMatcher(None, lineScript, rm.arr_words_srt[xSorted[i]] + rm.arr_words_srt[xSorted[i+1]]).ratio():
                    ki = 1
                    while xSorted[i] + ki in range(len(rm.arr_words_srt)) and SequenceMatcher(None, lineScript, rm.arr_words_srt[xSorted[i]]).ratio() < SequenceMatcher(None, lineScript, rm.arr_words_srt[xSorted[i]] + rm.arr_words_srt[xSorted[i] + ki]).ratio():
                        t[j] = t[j] + (xSorted[i] + ki,)
                        ki += 1
                    ki = -1
                    while t[j][0] + ki in range(len(rm.arr_words_srt)) and SequenceMatcher(None, lineScript, rm.arr_words_srt[t[j][0]]).ratio() < SequenceMatcher(None, lineScript, rm.arr_words_srt[t[j][0] + ki] + rm.arr_words_srt[t[j][0]]).ratio():
                        t[j] = t[j] + (t[j][0] + ki,)
                        ki += -1
                    t.append((xSorted[i+1],))
                    j += 1
                else:
                    t[j] = t[j] + (xSorted[i+1],)
            for num in t:
                sm = ""
                for k in range(len(num)):
                    sm = sm + rm.arr_words_srt[num[k]]
                distanceFromLastResult.append(SequenceMatcher(None, sm, lineScript).ratio()/(1 + abs(num[0] - arr_lines[len(arr_lines) - 1][len(arr_lines[len(arr_lines) - 1]) - 1])))
            arr_lines.append(t[distanceFromLastResult.index(max(distanceFromLastResult))])
        arr_lines = arr_lines[1::]
        dict_lines = {}
        for index_line in range(len(arr_lines)):
            t = arr_lines[index_line]
            t = sorted(t)
            for index_t in range(len(t)):
                if rm.arr_words_script[index_line] in dict_lines.keys():
                    dict_lines[rm.dict_without_punctuation_script[rm.arr_words_script[index_line]]] += rm.dict_without_punctuation_srt[rm.arr_words_srt[t[index_t]]]
                else:
                    dict_lines[rm.dict_without_punctuation_script[rm.arr_words_script[index_line]]] = rm.dict_without_punctuation_srt[rm.arr_words_srt[t[index_t]]]
        print dict_lines
        #        file_1 = open(output_file, 'w')
#        file_2 = open("outputfile2.txt", 'w')
#        for l in tqdm(sorted(self.dict_position.keys())):
#            file_1.write(str(self.dict_position[l]) + " : " + str((str(line_to_line[self.dict_position[l]][2]), str(line_to_line[self.dict_position[l]][1]))) + "\n")
#        index = 0
#        for l_d in tqdm(sorted(self.dict_position.keys())):
#            index += 1
#            file_2.writelines([str(index) + ". " + str(line_to_line[self.dict_position[l_d]][2]) + "\n", rm.script_talkers[rm.script_words[self.dict_position[l_d]]] + "\n", rm.dict_without_punctuation_script[str(self.dict_position[l_d])] + " - Script" + "\n", str(line_to_line[self.dict_position[l_d]][1]) + " - Srt" + "\n"])
#
d = MannagerZvi("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.main_action(constants.url_script, constants.url_srt, 50, "outputfile.txt")
