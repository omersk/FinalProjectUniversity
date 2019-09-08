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
        normal_dis_less_wide = scipy.stats.norm(1, 0.8).pdf
        cutoff_ratio = 0.05
        dict_lines = {

        }
        dict_lines_without_punc = {

        }
        bestTimeArr = []
        LastResultPredicted = 0
        LastResult = -1
        ArrayRatios = []
        num_was = []
        for lineScriptIndex in tqdm(range(len(self.rm.arr_words_script))):
            lineScript = self.rm.arr_words_script[lineScriptIndex]
            if "and I do yearn" in lineScript:
                pass
            if lineScriptIndex == 166:
                pass
            line_matrix = self.dict_word[lineScript.split(' ')[0]]
            for wordIndex in range(len(lineScript.split(' ')) - 1):
                if wordIndex == 0:
                    wordIndex += 1
                word = lineScript.split(' ')[wordIndex]
                line_matrix = numpy.row_stack((line_matrix, self.dict_word[word]))
            array_winners = numpy.dot(numpy.ones((1, len(lineScript.split(" ")))), line_matrix)
            array_winners = array_winners[0]
            array_distance = []
            for i in range(len(self.rm.arr_words_srt)):
                array_distance.append(normal_dis_less_wide(1.0 / (1 + abs(i - LastResult))))
            array_winners = numpy.multiply(numpy.transpose(array_winners), numpy.array((array_distance)))
            if max(array_winners) < cutoff_ratio:
                array_ratios = []
                for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                    lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis((1.0/(1 + abs((lineSrtIndex - LastResult))))))
                dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-")
                dict_lines_without_punc[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = self.rm.arr_words_srt[array_ratios.index(max(array_ratios))].rstrip().lstrip().lstrip("-")
                LastResultPredicted = array_ratios.index(max(array_ratios))
                bestTimeArr.append(timeUnion.timeUnion(self.rm.srt_time[LastResultPredicted]))
            else:
                indexed = list(enumerate(array_winners))
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
                    timeLine = timeUnion.timeUnion(self.rm.srt_time[xSorted[i]])
                    best_str = self.rm.arr_words_srt[xSorted[i]]
                    best_str_with_punc = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i]]].rstrip().lstrip().lstrip("-")
                    ki = -1
                    while ki + xSorted[i] in range(len(self.rm.arr_words_srt)) and SequenceMatcher(None, best_str,
                                                                                              lineScript).ratio() < SequenceMatcher(
                            None, self.rm.arr_words_srt[xSorted[i] + ki] + " " + best_str, lineScript).ratio():
                        best_str = self.rm.arr_words_srt[xSorted[i] + ki] + " " + best_str
                        best_str_with_punc = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-") + " " + best_str_with_punc
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(timeUnion.timeUnion(self.rm.srt_time[xSorted[i] + ki]))
                        ki -= 1
                    ki = 1
                    while ki + xSorted[i] in range(len(self.rm.arr_words_srt)) and SequenceMatcher(None, best_str, lineScript).ratio() < SequenceMatcher(None, best_str + " " + self.rm.arr_words_srt[xSorted[i] + ki], lineScript).ratio():
                        best_str = best_str + " " + self.rm.arr_words_srt[xSorted[i] + ki]
                        best_str_with_punc = best_str_with_punc + " " + self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-")
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(
                            timeUnion.timeUnion(self.rm.srt_time[xSorted[i] + ki]))
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
                    if the_best_distance < normal_dis_less_wide((1.0/(1 + abs((num[0] - LastResult)))))*ratio_str[numIndex] and num[0] not in num_was:
                        the_best_distance = normal_dis_less_wide((1.0/(1 + abs((num[0] - LastResult)))))*ratio_str[numIndex]
                        the_best_index = numIndex
                LastResultPredicted = t[the_best_index][0]
                dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = strings_with_punc[the_best_index]
                dict_lines_without_punc[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = strings[the_best_index]
                bestTimeArr.append(timeArr[the_best_index])
            lineScriptAfterPunc = self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip()
            lineSrtPredicted = dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]].rstrip().lstrip()
            lineSrtPredictedWithoutPunc = dict_lines_without_punc[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]].rstrip().lstrip()
            Customize_Ratio = max([SequenceMatcher(None, lineSrtPredictedWithoutPunc, lineScript).ratio(), SequenceMatcher(None, lineScript, lineSrtPredictedWithoutPunc).ratio()])
            Customize_Ratio = Customize_Ratio * 2 * normal_dis_less_wide(1.0/(1+abs(LastResultPredicted - LastResult)))
            if Customize_Ratio < 0.5 or LastResult == LastResultPredicted:
                array_ratios = []
                for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                    lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio()*normal_dis_less_wide(1.0/(1+abs(lineSrtIndex - LastResult))))
                max_ratio = max(array_ratios)
                max_ratio_index = array_ratios.index(max_ratio)
                if max_ratio > Customize_Ratio and max_ratio_index != LastResult:
                    if max_ratio > 0.4:
                        LastResultPredicted = max_ratio_index
                        file_new.write(str(lineScriptIndex + 1) + ". " + str(timeUnion.timeUnion(self.rm.srt_time[max_ratio_index])) + "\n" + self.rm.script_talkers[lineScriptIndex] + "\n" + self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip() + " - Script" + "\n" + self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-") + " - Srt" + "\n")
                        ArrayRatios.append(SequenceMatcher(None, self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip(), self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[max_ratio_index]].rstrip().lstrip().lstrip("-")).ratio())
                    else:
                        LastResultPredicted = LastResult
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")
                else:
                    LastResultPredicted = LastResult
                    file_new.write(
                        str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                            lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")

            else:
                file_new.write(str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" + self.rm.script_talkers[lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                ArrayRatios.append(Customize_Ratio)
            LastResult = LastResultPredicted
            num_was.append(LastResult)
        return sum(ArrayRatios)/len(ArrayRatios)

d = MannagerZvi("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.download_things(constants.url_script, constants.url_srt)
d.before_main_action(5)
print d.main_action()
