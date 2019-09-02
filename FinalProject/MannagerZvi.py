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
        dict_word = {

        }
        cutoff_ratio = 0.05
        dict_lines = {

        }
        bestTimeArr = []
        LastResult = 0
        ArrayRatios = []
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
                            if word == "I":
                                pass
                            if lineSrt and lineScript:
                                line_word_matrix[0][lineSrtIndex] = float((sumSrt - 5*rm.dict_words_srt[word])) / float(
                                    sumSrt) * float((sumScript - 5*rm.dict_words_script[word])) / float(sumScript*len(lineScript.split(' ')))
                    dict_word[word] = line_word_matrix
        for lineScriptIndex in tqdm(range(len(rm.arr_words_script))):
            lineScript = rm.arr_words_script[lineScriptIndex]
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
                bestTimeArr.append(timeUnion.timeUnion(rm.srt_time[rm.srt_words[rm.arr_words_srt[array_ratios.index(max(array_ratios))]]]))
            else:
                indexed = list(enumerate(array_winners[0]))
                sorted_indexed = sorted(indexed, key=operator.itemgetter(1))
                top_10 = sorted_indexed[-10:]
                copy_top_10 = sorted_indexed[-10:]
                for i, v in copy_top_10:
                    if v < cutoff_ratio:
                        top_10.remove((i, v))
                top_10 = sorted(list(reversed([i for i, v in top_10])))
                t = []
                xSorted = sorted(top_10)
                j = 0
                ratio_str = []
                strings = []
                timeArr = []
                strings_with_punc = []
                for i in range(len(xSorted)):
                    t.append((xSorted[i],))
                    timeLine = timeUnion.timeUnion(rm.srt_time[rm.srt_words[rm.arr_words_srt[xSorted[i]]]])
                    best_str = rm.arr_words_srt[xSorted[i]]
                    best_str_with_punc = rm.dict_without_punctuation_srt[rm.arr_words_srt[xSorted[i]]].rstrip().lstrip().lstrip("-")
                    ki = -1
                    while ki + xSorted[i] in range(len(rm.arr_words_srt)) and SequenceMatcher(None, best_str,
                                                                                              lineScript).ratio() < SequenceMatcher(
                            None, rm.arr_words_srt[xSorted[i] + ki] + " " + best_str, lineScript).ratio():
                        best_str = rm.arr_words_srt[xSorted[i] + ki] + " " + best_str
                        best_str_with_punc = rm.dict_without_punctuation_srt[rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-") + " " + best_str_with_punc
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(timeUnion.timeUnion(rm.srt_time[rm.srt_words[rm.arr_words_srt[xSorted[i] + ki]]]))
                        ki -= 1
                    ki = 1
                    while ki + xSorted[i] in range(len(rm.arr_words_srt)) and SequenceMatcher(None, best_str, lineScript).ratio() < SequenceMatcher(None, best_str + " " + rm.arr_words_srt[xSorted[i] + ki], lineScript).ratio():
                        best_str = best_str + " " + rm.arr_words_srt[xSorted[i] + ki]
                        best_str_with_punc = best_str_with_punc + " " + rm.dict_without_punctuation_srt[rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-")
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(
                            timeUnion.timeUnion(rm.srt_time[rm.srt_words[rm.arr_words_srt[xSorted[i] + ki]]]))
                        ki += 1
                    j = j + 1
                    ratio_str.append(SequenceMatcher(None, best_str, lineScript).ratio())
                    strings.append(best_str)
                    timeArr.append(str(timeLine))
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
                bestTimeArr.append(timeArr[the_best_index])
            lineScriptAfterPunc = rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]].rstrip().lstrip()
            lineSrtPredicted = dict_lines[rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]]].rstrip().lstrip()
            Customize_Ratio = max([SequenceMatcher(None, lineScriptAfterPunc, lineSrtPredicted).ratio(), SequenceMatcher(None, lineSrtPredicted, lineScriptAfterPunc).ratio()])
            if Customize_Ratio < 0.85:
                array_ratios = []
                for lineSrtIndex in range(len(rm.arr_words_srt)):
                    lineSrt = rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis((1.0/(1 + abs((lineSrtIndex - LastResult))))))
                if SequenceMatcher(None, rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]].rstrip().lstrip(), rm.dict_without_punctuation_srt[rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-")).ratio() > Customize_Ratio:
                    file_new.write(str(lineScriptIndex + 1) + ". " + str(timeUnion.timeUnion(rm.srt_time[rm.srt_words[rm.arr_words_srt[array_ratios.index(max(array_ratios))]]])) + "\n" + rm.script_talkers[lineScriptIndex] + "\n" + rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]].rstrip().lstrip() + " - Script" + "\n" + rm.dict_without_punctuation_srt[rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-") + " - Srt" + "\n")
                    ArrayRatios.append(SequenceMatcher(None, rm.dict_without_punctuation_script[rm.arr_words_script[lineScriptIndex]].rstrip().lstrip(), rm.dict_without_punctuation_srt[rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-")).ratio())
                else:
                    file_new.write(
                        str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" + rm.script_talkers[
                            lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                    ArrayRatios.append(Customize_Ratio)
            else:
                file_new.write(str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" + rm.script_talkers[lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                ArrayRatios.append(Customize_Ratio)

        print sum(ArrayRatios)/len(ArrayRatios)

d = MannagerZvi("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.main_action(constants.url_script, constants.url_srt, 50, "outputfile.txt")
