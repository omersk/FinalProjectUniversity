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
        file_new = open("outputfilenew.txt", 'w')
        d = DropBoxDownloader.DropBoxDownloader(self.access_token)
        d.download_file(url_script, self.script_file_path)
        d.download_file(url_srt, self.srt_file_path)
        rm = RegexMaker.RegexMaker(self.script_file_path, self.regex_script, self.regex_srt, self.srt_file_path)
        rm.find_matches_script()
        rm.find_matches_srt()
        normal_dis = scipy.stats.norm(1, 1.5).pdf
        sumScript = sum(rm.dict_words_script.values())
        sumSrt = sum(rm.dict_words_srt.values())
        arr_lines = [(0,)]
        dict_word = {

        }
        cutoff_ratio = 0.05
        dict_lines = {

        }
        LastResult = 0
        for lineScriptIndex in tqdm(range(len(rm.arr_words_script))):
            lineScript = rm.arr_words_script[lineScriptIndex]
            for wordIndex in range(len(lineScript.split(' '))):
                line_word_matrix = numpy.zeros((1, len(rm.arr_words_srt)))
                word = lineScript.split(' ')[wordIndex]
                if word in dict_word.keys():
                    pass
                else:
                    for lineSrtIndex in range(len(rm.arr_words_srt)):
                        lineSrt = rm.arr_words_srt[lineSrtIndex]
                        if word in lineSrt.split(' '):
                            if lineSrt and lineScript:
                                line_word_matrix[0][lineSrtIndex] = float((sumSrt - rm.dict_words_srt[word])) / float(
                                    sumSrt*len(lineSrt.split(' '))) * float((sumScript - rm.dict_words_script[word])) / float(sumScript*len(lineScript.split(' ')))
                    dict_word[word] = line_word_matrix
        for lineScriptIndex in tqdm(range(len(rm.arr_words_script))):
            if lineScriptIndex == len(rm.arr_words_script) - 1:
                pass
            lineScript = rm.arr_words_script[lineScriptIndex]
            if lineScript == "Byebye":
                pass
            if "appropriate in" in lineScript:
                pass

            line_matrix = dict_word[lineScript.split(' ')[0]]
            for wordIndex in range(len(lineScript.split(' ')) - 1):
                if wordIndex == 0:
                    wordIndex += 1
                word = lineScript.split(' ')[wordIndex]
                line_matrix = numpy.row_stack((line_matrix, dict_word[word]))
            array_winners = numpy.dot(numpy.ones((1, len(lineScript.split(" ")))), line_matrix)
            if max(array_winners[0]) < cutoff_ratio:
                array_ratios = []
                for lineSrtIndex in range(len(rm.arr_words_srt)):
                    lineSrt = rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis((1.0/(1 + abs((lineSrtIndex - LastResult))))))
                dict_lines[rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]]] = rm.dict_without_punctuation_srt[rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-")
                LastResult = array_ratios.index(max(array_ratios))
            else:
                indexed = list(enumerate(array_winners[0]))
                top_10 = sorted(indexed, key=operator.itemgetter(1))[-10:]
                top_10 = sorted(list(reversed([i for i, v in top_10])))
                t = []
                distanceFromLastResult = []
                xSorted = sorted(top_10)
                j = 0
                ratio_str = []
                strings = []
                strings_with_punc = []
                for i in range(len(xSorted) - 1):
                    t.append((xSorted[i],))
                    best_str = rm.arr_words_srt[xSorted[i]]
                    best_str_with_punc = rm.dict_without_punctuation_srt[rm.arr_words_srt[xSorted[i]]].rstrip().lstrip().lstrip("-")
                    ki = -1
                    while ki + xSorted[i] in range(len(rm.arr_words_srt)) and SequenceMatcher(None, best_str,
                                                                                              lineScript).ratio() < SequenceMatcher(
                            None, rm.arr_words_srt[xSorted[i] + ki] + " " + best_str, lineScript).ratio():
                        best_str = rm.arr_words_srt[xSorted[i] + ki] + " " + best_str
                        best_str_with_punc = rm.dict_without_punctuation_srt[rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-") + " " + best_str_with_punc
                        t[j] = t[j] + (xSorted[i] + ki,)
                        ki -= 1
                    ki = 1
                    while ki + xSorted[i] in range(len(rm.arr_words_srt)) and SequenceMatcher(None, best_str, lineScript).ratio() < SequenceMatcher(None, best_str + " " + rm.arr_words_srt[xSorted[i] + ki], lineScript).ratio():
                        best_str = best_str + " " + rm.arr_words_srt[xSorted[i] + ki]
                        best_str_with_punc = best_str_with_punc + " " + rm.dict_without_punctuation_srt[rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-")
                        t[j] = t[j] + (xSorted[i] + ki,)
                        ki += 1
                    j = j + 1
                    ratio_str.append(SequenceMatcher(None, best_str, lineScript).ratio())
                    strings.append(best_str)
                    strings_with_punc.append(best_str_with_punc)
                the_best_distance = 0
                the_best_index = -1
                for numIndex in range(len(t)):
                    num = t[numIndex]
                    if the_best_distance < normal_dis((1.0/(1 + abs((num[0] - LastResult)))))*ratio_str[numIndex]:
                        the_best_distance = normal_dis((1.0/(1 + abs((num[0] - LastResult)))))*ratio_str[numIndex]
                        the_best_index = numIndex
                LastResult = the_best_index
                dict_lines[rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]]] = strings_with_punc[the_best_index]
            file_new.write(str(lineScriptIndex) + ". " + "\n" + rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]].rstrip().lstrip() + " - SCRIPT" + "\n" + dict_lines[rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]]].rstrip().lstrip() + " - SRT" + "\n")


d = MannagerZvi("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.main_action(constants.url_script, constants.url_srt, 50, "outputfile.txt")
