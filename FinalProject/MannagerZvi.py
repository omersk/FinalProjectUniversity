import constants
import DropBoxDownloader
import RegexMakerZvi
from difflib import SequenceMatcher
import scipy.stats
import timeUnion
from tqdm import tqdm
import numpy
import operator
import math


def normal_dis_for_results(t):
    sigma = 8
    mean = 2
    if t > 0:
        return 1.0 / math.sqrt(2.0 * numpy.pi * sigma*sigma) * math.exp(-((t - mean) * (t - mean)) / (2.0 * sigma*sigma))
    elif t < 0:
        return 0.9 / math.sqrt(2.0 * numpy.pi * sigma * sigma) * math.exp(
            -((t - mean) * (t - mean)) / (2.0 * sigma * sigma))
    else:
        return 0


class MannagerZvi:
    def __init__(self, script_file_path, regex_script, regex_srt, srt_file_path, access_token):
        """
        :param script_file_path: the script file path we download from dropbox
        :param regex_script: the regex we used to the script file
        :param regex_srt: the regex we used to the srt file
        :param srt_file_path: the path to the srt file that there we download from dropbox
        :param access_token: access token for access the dropbox
        """
        self.script_file_path = script_file_path
        self.regex_script = regex_script
        self.regex_srt = regex_srt
        self.srt_file_path = srt_file_path
        self.access_token = access_token
        self.dict_position = {}
        self.rm = None
        self.word_to_srt_line_match = {
        }

    def download_things(self, url_script, url_srt):
        """
        :param url_script: the url to the script
        :param url_srt: the url to the srt
        :return: download from dropbox to the script_file_path and srt_file_path
        """
        d = DropBoxDownloader.DropBoxDownloader(self.access_token)
        d.download_file(url_script, self.script_file_path)
        d.download_file(url_srt, self.srt_file_path)
        self.rm = RegexMakerZvi.RegexMakerZvi(self.script_file_path, self.regex_script, self.regex_srt, self.srt_file_path)
        self.rm.find_matches_script()
        self.rm.find_matches_srt()

    def before_main_action(self):
        """
        :return: make a dictionary with the matching ratio of every word to every line in srt
        """
        sumScript = sum(self.rm.dict_words_script.values())
        sumSrt = sum(self.rm.dict_words_srt.values())
        for lineScriptIndex in tqdm(range(len(self.rm.arr_words_script))):
            lineScript = self.rm.arr_words_script[lineScriptIndex]
            for wordIndex in range(len(lineScript.split(' '))):
                line_word_matrix = numpy.zeros((1, len(self.rm.arr_words_srt)))
                word = lineScript.split(' ')[wordIndex]
                if word in self.word_to_srt_line_match.keys():
                    pass
                else:
                    for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                        lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                        if word in lineSrt.split(' '):
                            if lineSrt and lineScript:
                                line_word_matrix[0][lineSrtIndex] = float((sumSrt - 5*self.rm.dict_words_srt[word])) / float(
                                    sumSrt) * float((sumScript - 5*self.rm.dict_words_script[word])) / float(sumScript*len(lineScript.split(' ')))
                    self.word_to_srt_line_match[word] = line_word_matrix

    def main_action(self):
        """
        :return: text file with the union of the script and the srt
        """
        file_new = open(constants.outputfile, 'w')  # the file path that will be the union between the srt and script
        normal_dis = scipy.stats.norm(0.5, 1.5).pdf  # normal distribution pdf
        cutoff_ratio = 0.05  # cutoff that ratio below that will not be written in the union file
        dict_lines = {

        }  # dict of the matches between the lines
        CutOffAlmostSurely = 0.85
        CutOffNotSure = 0.4
        bestTimeArr = []  # the time array
        LastResult = -1  # the last index of the script line that the srt line was customized
        ArrayRatios = []  # array with the matching ratios
        RowOfNotFound = 0
        for lineScriptIndex in tqdm(range(len(self.rm.arr_words_script))):
            """
            We run like that : 
            for every line_script in script we check the most similar line in srt both in contents and time
            """
            lineScript = self.rm.arr_words_script[lineScriptIndex]  # the string of the line
            line_matrix = self.word_to_srt_line_match[lineScript.split(' ')[0]]  # this will be matrix of the each word and his ratio to line in srt
            for wordIndex in range(len(lineScript.split(' ')) - 1):
                """
                we build a matrix that her rows will be the words of the script and the columns will be ratios of each
                line in srt
                """
                if wordIndex == 0:
                    wordIndex += 1
                word = lineScript.split(' ')[wordIndex]
                line_matrix = numpy.row_stack((line_matrix, self.word_to_srt_line_match[word]))
            array_winners = numpy.dot(numpy.ones((1, len(lineScript.split(" ")))), line_matrix)
            if max(array_winners[0]) < cutoff_ratio:  # if we didn't get line that have good ratio
                """
                we check which line have the best matching in term of distance and words by a more longer process.
                """
                array_ratios = []
                for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                    lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis((1.0/(1 + abs((lineSrtIndex - LastResult))))))
                dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-")
                bestTimeArr.append(timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]], key=lambda t: abs(t-LastResult))]))
            else:
                """
                we found at least one line with good ratio
                """
                indexed = list(enumerate(array_winners[0]))
                sorted_indexed = sorted(indexed, key=operator.itemgetter(1))
                top_10 = sorted_indexed[-10:]  # we take the top ten
                copy_top_10 = sorted_indexed[-10:]
                for i, v in copy_top_10:  # we remove from the top ten those who dont have good ratio
                    if v < cutoff_ratio:
                        top_10.remove((i, v))
                top_10 = sorted(list(reversed([i for i, v in top_10])))  # we sort it
                t = []
                xSorted = sorted(top_10)
                j = 0
                ratio_str = []
                strings = []
                timeArr = []
                strings_with_punc = []
                for i in range(len(xSorted)):
                    """
                    for each line in the top ten we check if his neighbors are also lines that custom to our line
                    """
                    t.append((xSorted[i],))  # this will be tupple that hold each line neighbors that also custom
                    timeLine = timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[xSorted[i]]], key=lambda x: abs(x-LastResult))])
                    best_str = self.rm.arr_words_srt[xSorted[i]]
                    best_str_with_punc = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i]]].rstrip().lstrip().lstrip("-")
                    ki = -1  # first we check for those who come before the top ten line
                    while ki + xSorted[i] in range(len(self.rm.arr_words_srt)) and SequenceMatcher(None, best_str,
                                                                                              lineScript).ratio() < SequenceMatcher(
                            None, self.rm.arr_words_srt[xSorted[i] + ki] + " " + best_str, lineScript).ratio():
                        best_str = self.rm.arr_words_srt[xSorted[i] + ki] + " " + best_str
                        best_str_with_punc = self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-") + " " + best_str_with_punc
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[xSorted[i] + ki]], key=lambda x:abs(x-LastResult))]))
                        ki -= 1
                    ki = 1  # than we check for those who come after the top ten line
                    while ki + xSorted[i] in range(len(self.rm.arr_words_srt)) and SequenceMatcher(None, best_str, lineScript).ratio() < SequenceMatcher(None, best_str + " " + self.rm.arr_words_srt[xSorted[i] + ki], lineScript).ratio():
                        best_str = best_str + " " + self.rm.arr_words_srt[xSorted[i] + ki]
                        best_str_with_punc = best_str_with_punc + " " + self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[xSorted[i] + ki]].rstrip().lstrip().lstrip("-")
                        t[j] = t[j] + (xSorted[i] + ki,)
                        timeLine = timeLine.union(
                            timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[xSorted[i] + ki]], key=lambda x:abs(x-LastResult))]))
                        ki += 1
                    j = j + 1
                    ratio_str.append(SequenceMatcher(None, best_str, lineScript).ratio())  # we add the final ratio ( with neighbors )
                    strings.append(best_str)
                    timeArr.append(str(timeLine))  # we add the time of the final
                    strings_with_punc.append(best_str_with_punc)
                the_best_distance = 0
                the_best_index = -1
                for numIndex in range(len(t)):
                    """
                    now we check which one had the highest results
                    """
                    num = t[numIndex]
                    if the_best_distance < normal_dis((1.0/(1 + abs((num[0] - LastResult)))))*ratio_str[numIndex]:
                        the_best_distance = normal_dis((1.0/(1 + abs((num[0] - LastResult)))))*ratio_str[numIndex]
                        the_best_index = numIndex
                dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]] = strings_with_punc[the_best_index]
                bestTimeArr.append(timeArr[the_best_index])
            lineScriptAfterPunc = self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip()
            lineSrtPredicted = dict_lines[self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]]].rstrip().lstrip()
            Customize_Ratio = max([SequenceMatcher(None, lineScriptAfterPunc, lineSrtPredicted).ratio(), SequenceMatcher(None, lineSrtPredicted, lineScriptAfterPunc).ratio()])
            index_of_customize_ratio = self.rm.initial_time.index(
                str(bestTimeArr[lineScriptIndex]).split(" --> ")[0])
            if Customize_Ratio < CutOffAlmostSurely:
                """
                the matching ratio not good enough, so therefore we do some things
                """
                array_ratios = []
                for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                    """
                    here we check the maximum ratio by using different matching type
                    """
                    lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                    array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis_for_results(((lineSrtIndex - LastResult))))
                max_ratio = max(array_ratios)
                max_ratio_index = array_ratios.index(max_ratio)
                max_ratio = max_ratio * (1/(normal_dis_for_results(1)))
                if max_ratio > (Customize_Ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(((index_of_customize_ratio - LastResult)))):
                    """
                    check if the result we got here is better than what we got at the other time
                    if it does, we use this result
                    """
                    if max_ratio > CutOffNotSure or RowOfNotFound > 2:
                        """
                        we didn't get bad result but we are not sure is good enough, we will still take it 
                        """
                        time = str(timeUnion.timeUnion(self.rm.srt_time[min(self.rm.srt_words[self.rm.arr_words_srt[max_ratio_index]], key=lambda t: abs(t-LastResult))]))
                        file_new.write(str(lineScriptIndex + 1) + ". " + time + "\n" + self.rm.script_talkers[lineScriptIndex] + "\n" + self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip() + " - Script" + "\n" + self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip("-") + " - Srt" + "\n")
                        ArrayRatios.append(SequenceMatcher(None, self.rm.dict_without_punctuation_script[self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip(), self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[max_ratio_index]].rstrip().lstrip().lstrip("-")).ratio())
                        RowOfNotFound = 0
                    else:
                        """
                        the matching ratio were too low, therefore we decided that it's not in the srt
                        """
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")
                        RowOfNotFound = RowOfNotFound + 1
                else:
                    """
                    the try to find new ratio discovered as unsuccessful
                    """
                    if (Customize_Ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(((index_of_customize_ratio - LastResult)))) > CutOffNotSure or RowOfNotFound > 2:
                        """
                        not bad result, but not good, still we decided to take it
                        """
                        LastResult = index_of_customize_ratio
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                        ArrayRatios.append(Customize_Ratio)
                        RowOfNotFound = 0
                    else:
                        """
                        the matching ratio were too low, therefore we decided that it's not in the srt
                        """
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")
                        RowOfNotFound = RowOfNotFound + 1

            else:
                """
                the ratio of the words is good but we also want to check the distance between last word
                """
                if (Customize_Ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                        ((index_of_customize_ratio - LastResult)))) > CutOffNotSure  or RowOfNotFound > 2:
                    """
                    its were above our cutoff therefore we took it
                    """
                    LastResult = index_of_customize_ratio
                    file_new.write(
                        str(lineScriptIndex + 1) + ". " + str(bestTimeArr[lineScriptIndex]) + "\n" +
                        self.rm.script_talkers[
                            lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + lineSrtPredicted + " - Srt" + "\n")
                    ArrayRatios.append(Customize_Ratio)
                    RowOfNotFound = 0
                else:
                    """
                    it weren't good after the distance check so we check for new line by using different method
                    """
                    array_ratios = []
                    for lineSrtIndex in range(len(self.rm.arr_words_srt)):
                        lineSrt = self.rm.arr_words_srt[lineSrtIndex]
                        array_ratios.append(SequenceMatcher(None, lineSrt, lineScript).ratio() * normal_dis_for_results(
                            ((lineSrtIndex - LastResult))))
                    max_ratio = max(array_ratios)
                    max_ratio_index = array_ratios.index(max_ratio)
                    max_ratio = max_ratio * (1 / (normal_dis_for_results(1)))
                    if max_ratio > CutOffNotSure  or RowOfNotFound > 2:
                        """
                        check if the new ratio worked
                        """
                        LastResult = max_ratio_index
                        file_new.write(str(lineScriptIndex + 1) + ". " + str(timeUnion.timeUnion(self.rm.srt_time[
                                                                                                     min(
                                                                                                         self.rm.srt_words[
                                                                                                             self.rm.arr_words_srt[
                                                                                                                 max_ratio_index]],
                                                                                                         key=lambda
                                                                                                             t: abs(
                                                                                                             t - LastResult))])) + "\n" +
                                       self.rm.script_talkers[lineScriptIndex] + "\n" +
                                       self.rm.dict_without_punctuation_script[self.rm.arr_words_script[
                                           lineScriptIndex]].rstrip().lstrip() + " - Script" + "\n" +
                                       self.rm.dict_without_punctuation_srt[self.rm.arr_words_srt[
                                           array_ratios.index(max(array_ratios))]].rstrip().lstrip().lstrip(
                                           "-") + " - Srt" + "\n")
                        ArrayRatios.append(SequenceMatcher(None, self.rm.dict_without_punctuation_script[
                            self.rm.arr_words_script[lineScriptIndex]].rstrip().lstrip(),
                                                           self.rm.dict_without_punctuation_srt[
                                                               self.rm.arr_words_srt[
                                                                   max_ratio_index]].rstrip().lstrip().lstrip(
                                                               "-")).ratio())
                        RowOfNotFound = 0
                    else:
                        """
                        the new ratio didn't work ( low ratio ) therefore we decided that the line is no in the srt
                        """
                        file_new.write(
                            str(lineScriptIndex + 1) + ". " + "\n" + self.rm.script_talkers[
                                lineScriptIndex] + "\n" + lineScriptAfterPunc + " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n")
                        RowOfNotFound = RowOfNotFound + 1

        return sum(ArrayRatios)/len(ArrayRatios)  # our confidence in repentance

d = MannagerZvi("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.download_things(constants.url_script, constants.url_srt)
d.before_main_action()
print d.main_action()