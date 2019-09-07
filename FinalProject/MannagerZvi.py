import DropBoxDownloader
import RegexMakerZvi
from difflib import SequenceMatcher
import scipy.stats
import timeUnion
from tqdm import tqdm
import constants
import numpy
import operator


class MannagerZvi:
    def __init__(self, script_file_path, regex_script, regex_srt, srt_file_path, access_token):
        self.script_file_path = script_file_path
        self.regex_script = regex_script
        self.regex_srt = regex_srt
        self.srt_file_path = srt_file_path
        self.access_token = access_token
        self.dict_position = {}
        self.rm = None
        self.dict_word = {
        }

    def download_things(self, url_script, url_srt):
        d = DropBoxDownloader.DropBoxDownloader(self.access_token)
        d.download_file(url_script, self.script_file_path)
        d.download_file(url_srt, self.srt_file_path)
        self.rm = RegexMakerZvi.RegexMakerZvi(self.script_file_path, self.regex_script, self.regex_srt, self.srt_file_path)
        self.rm.find_matches_script()
        self.rm.find_matches_srt()

    def before_main_action(self, a):
        sumScript = sum(self.rm.dict_words_script.values())
        sumSrt = sum(self.rm.dict_words_srt.values())
        for lineScriptIndex in tqdm(range(len(self.rm.arr_words_script))):
            lineScript = self.rm.arr_words_script[lineScriptIndex]
            for wordIndex in range(len(lineScript.split(' '))):
                line_word_matrix = numpy.zeros((1, len(self.rm.arr_words_srt)))
                word = lineScript.split(' ')[wordIndex]
                if word in self.dict_word.keys():
                    pass
                else:
                    for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                        lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                        if word in lineSrt.split(' '):
                            if word == "I":
                                pass
                            if lineSrt and lineScript:
                                line_word_matrix[0][lineSrtIndex] = float((sumSrt - a*self.rm.dict_words_srt[word])) / float(
                                    sumSrt) * float((sumScript - a*self.rm.dict_words_script[word])) / float(sumScript*len(lineScript.split(' ')))
                    self.dict_word[word] = line_word_matrix

    def main_action(self):
        file_new = open("outputfilenew.txt", 'w')
        normal_dis = scipy.stats.norm(1, 1.5).pdf
        cutoff_ratio = 0.05
        dict_lines = {

        }
        bestTimeArr = []
        LastResult = 0
        ArrayRatios = []
        for lineScriptIndex in tqdm(range(len(self.rm.arr_words_script))):
            lineScript = self.rm.arr_words_script[lineScriptIndex]
            if "Okay" in lineScript:
                pass
            line_matrix = self.dict_word[lineScript.split(' ')[0]]
            for wordIndex in range(len(lineScript.split(' ')) - 1):
                if wordIndex == 0:
                    wordIndex += 1
                word = lineScript.split(' ')[wordIndex]
                line_matrix = numpy.row_stack((line_matrix, self.dict_word[word]))
            array_winners = numpy.dot(numpy.ones((1, len(lineScript.split(" ")))), line_matrix)
            if max(array_winners[0]) < cutoff_ratio:
                array_ratios = []
                for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                    lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis((1.0/(1 + abs((lineSrtIndex - LastResult))))))
                dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-")
                LastResult = array_ratios.index(max(array_ratios))
                bestTimeArr.append(timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]], key=lambda t: abs(t-LastResult))]))
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
                    timeLine = timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[xSorted[i]]], key=lambda t: abs(t-LastResult))])
                    best_str = self.rm.arr_words_srt[xSorted[i]]
                    best_str_with_punc = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i]]].rstrip().lstrip().lstrip("-")
                    ki = -1
                    while ki + xSorted[i] in range(len(self.rm.arr_words_srt)) and SequenceMatcher(None, best_str,
                                                                                              lineScript).ratio() < SequenceMatcher(
                            None, self.rm.arr_words_srt[xSorted[i] + ki] + " " + best_str, lineScript).ratio():
                        best_str = self.rm.arr_words_srt[xSorted[i] + ki] + " " + best_str
                        best_str_with_punc = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-") + " " + best_str_with_punc
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[xSorted[i] + ki]], key=lambda t:abs(t-LastResult))]))
                        ki -= 1
                    ki = 1
                    while ki + xSorted[i] in range(len(self.rm.arr_words_srt)) and SequenceMatcher(None, best_str, lineScript).ratio() < SequenceMatcher(None, best_str + " " + self.rm.arr_words_srt[xSorted[i] + ki], lineScript).ratio():
                        best_str = best_str + " " + self.rm.arr_words_srt[xSorted[i] + ki]
                        best_str_with_punc = best_str_with_punc + " " + self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-")
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(
                            timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[xSorted[i] + ki]], key=lambda t:abs(t-LastResult))]))
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
                dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = strings_with_punc[the_best_index]
                bestTimeArr.append(timeArr[the_best_index])
            lineScriptAfterPunc = self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip()
            lineSrtPredicted = dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]].rstrip().lstrip()
            Customize_Ratio = max([SequenceMatcher(None, lineScriptAfterPunc, lineSrtPredicted).ratio(), SequenceMatcher(None, lineSrtPredicted, lineScriptAfterPunc).ratio()])
            if Customize_Ratio < 0.85:
                array_ratios = []
                for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                    lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio())
                max_ratio = max(array_ratios)
                max_ratio_index = array_ratios.index(max_ratio)
                if max_ratio > Customize_Ratio:
                    if max_ratio > 0.5:
                        file_new.write(str(lineScriptIndex + 1) + ". " + str(timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[max_ratio_index]], key=lambda t: abs(t-LastResult))])) + "\n" + self.rm.script_talkers[lineScriptIndex] + "\n" + self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip() + " - Script" + "\n" + self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-") + " - Srt" + "\n")
                        ArrayRatios.append(SequenceMatcher(None, self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip(), self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[max_ratio_index]].rstrip().lstrip().lstrip("-")).ratio())
                    else:
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")
                else:
                    if Customize_Ratio > 0.5:
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                        ArrayRatios.append(Customize_Ratio)
                    else:
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")


            else:
                file_new.write(str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" + self.rm.script_talkers[lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                ArrayRatios.append(Customize_Ratio)

        return sum(ArrayRatios)/len(ArrayRatios)

d = MannagerZvi("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.download_things(constants.url_script, constants.url_srt)
d.before_main_action(5)
print d.main_action()
