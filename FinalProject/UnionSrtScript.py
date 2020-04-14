"""
This is an python 2 written code to union srt file and script file ( which are being used in the movie industry )
the code was created by Omer Sassoni and Ofek Poraz at April-2020 for the final project
on Bar-Ilan University.
"""
import constants
from os import listdir
import DropBoxDownloader
from ExtractData import DataExtractor
from difflib import SequenceMatcher
import scipy.stats
import timeUnion
from tqdm import tqdm
import numpy
import operator
import math
import sys
from os.path import isfile, join
unknown_line_massage = " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n"


def normal_dis_for_results(t):
    """
    Function of effective normal distribution with mean = 2, sigma = 8,
    where we decided to take less probability to negative values .
    :param t: the value which we will input to the function
    :return: the value of normal distribution when t is the parameter.
    """
    sigma = constants.sigma
    mean = constants.mean
    normal_distribution_value = 1.0 / math.sqrt(2.0 * numpy.pi * sigma * sigma) * math.exp(-((t - mean) * (t - mean)) /
                                                                                           (2.0 * sigma * sigma))
    factorized_normal_distribution_value = 0.9 * normal_distribution_value
    if t > 0:  # positive values gets a normal distribution
        return normal_distribution_value
    elif t < 0:  # negative values gets a factorized normal distribution
        return factorized_normal_distribution_value
    else:  # the value zero get zero probability
        return 0


class UnionScriptSrt:
    """
    A class that came up to the world in order to union 2 files - srt file and script file
    which commonly used in the movie industry
    ...
        Methods
        -------
        __init__(self, script_file_path, regex_script, regex_srt, srt_file_path, access_token)
            The constructor for the class
        download_from_dropbox(self, url_script, url_srt)
            Download from dropbox the srt file and the script file.
        create_probability_matrix_for_each_word(self)
            make a dictionary with the matching ratio of every word to every line in srt
        union_files(self, outputfilename)
            Union an srt file and a script file into one file and write it in the outputfilename
            string that the function gets as input

    ...
    """

    def __init__(self, script_file_path, regex_script, regex_srt, srt_file_path, access_token):
        """
        This function is the constructor for the class.
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
        self.ex = None
        self.word_to_srt_line_match = {
        }

    def download_from_dropbox(self, url_script, url_srt):
        """
        Download from dropbox the srt file and the script file.
        :param url_script: the url to the script
        :param url_srt: the url to the srt
        :return: download from dropbox to the script_file_path and srt_file_path
        """
        d1 = DropBoxDownloader.DropBoxDownloader(self.access_token)
        d1.download_file(url_script, self.script_file_path)
        d1.download_file(url_srt, self.srt_file_path)

    def create_probability_matrix_for_each_word(self):
        """
        make a dictionary with the matching ratio of every word to every line in srt
        example - if the word "hi" appears only one time in the first line, two times in the third line
        and zero times at all the other lines, than the matrix for the word "hi" will be something like that:
                            hiMatrix = [someRatio, 0, someRatio * 2, 0 ... ]
        Note: it can look a bit different.
        """
        self.ex = DataExtractor(self.script_file_path, self.regex_script, self.regex_srt,
                                self.srt_file_path)  # this class extract data from srt, script files
        self.ex.find_matches_script()  # the method that extract data from script file
        self.ex.find_matches_srt()  # the method that extract data from srt file
        sum_script = sum(self.ex.word_to_number_appearances_script.values())  # number of total appearance
        # of words in the script file
        sum_srt = sum(self.ex.word_to_number_appearances_srt.values())  # number of total appearance
        # of words in the srt file
        for line_script_index in tqdm(range(len(self.ex.array_of_script_lines))):  # we run on every index of line
            # in the script
            line_script = self.ex.array_of_script_lines[line_script_index]  # the line of this iteration
            for wordIndex in range(len(line_script.split(' '))):  # for every index of word in this line
                line_word_matrix = numpy.zeros((1, len(self.ex.array_of_srt_lines)))  # this will be ur matrix for
                # this word
                word = line_script.split(' ')[wordIndex]  # the word of this iteration
                if word not in self.word_to_srt_line_match.keys():  # if we already computed the matrix we no need again
                    for line_srt_index in range(len(self.ex.array_of_srt_lines)):  # run on indexes of lines in srt file
                        line_srt = self.ex.array_of_srt_lines[line_srt_index]  # the line in the specific iteration
                        if word in line_srt.split(' '):  # for every word in this line
                            if line_srt and line_script:  # if both of lines are not empty
                                line_word_matrix[0][line_srt_index] = float(
                                    (sum_srt - 5 * self.ex.word_to_number_appearances_srt[word])) / float(
                                    sum_srt) * float((sum_script - 5 *
                                                      self.ex.word_to_number_appearances_script[word]))\
                                                                      / float(sum_script * len(line_script.split(' ')))
                                # factorized probability of word in line
                    self.word_to_srt_line_match[word] = line_word_matrix  # add to a dictionary

    def union_files(self, outputfilename):
        """
        Union an srt file and a script file into one file and write it in the outputfilename
        string that the function gets as input
        :param outputfilename: the outputfilename which there will be written the union file
        """
        file_new = open(outputfilename, 'w')  # the file path that will be the union between the srt and script
        normal_dis = scipy.stats.norm(0.5, 1.5).pdf  # normal distribution pdf
        cutoff_ratio = constants.cutoff_ratio  # cutoff that ratio below that will not be written in the union file
        dict_lines = {

        }  # dict of the matches between the lines
        cut_off_almost_surely = constants.cut_off_almost_surely
        cut_off_not_sure = constants.cut_off_not_sure
        best_time_arr = []  # the time array
        last_result = -1  # the last index of the script line that the srt line was customized
        matching_probs_of_each_line = []  # array with the matching ratios
        row_not_found = 0  # how much rows we didn't find from the last found
        for line_script_index in tqdm(range(len(self.ex.array_of_script_lines))):
            #  We run like that :
            #  for every line_script in script we check the most similar line in srt both in contents and time
            line_script = self.ex.array_of_script_lines[line_script_index]  # the string of the line
            line_matrix = self.word_to_srt_line_match[
                line_script.split(' ')[0]]  # this will be matrix of the each word and his ratio to line in srt
            for wordIndex in range(len(line_script.split(' ')) - 1):
                #  we build a matrix that her rows will be the words
                #  of the script and the columns will be ratios of each line in srt
                if wordIndex == 0:
                    wordIndex += 1
                word = line_script.split(' ')[wordIndex]
                line_matrix = numpy.row_stack((line_matrix, self.word_to_srt_line_match[word]))
            array_winners = numpy.dot(numpy.ones((1, len(line_script.split(" ")))), line_matrix)
            if max(array_winners[0]) < cutoff_ratio:  # if we didn't get line that have good ratio
                #  we check which line have the best matching in term of distance and words by a more longer process.
                matching_probs_of_each_line = []
                for line_srt_index in range(len(self.ex.array_of_srt_lines)):
                    line_srt = self.ex.array_of_srt_lines[line_srt_index]
                    matching_probs_of_each_line.append(SequenceMatcher(None, line_srt, line_script).ratio() *
                                                       normal_dis((1.0 / (1 + abs((line_srt_index - last_result))))))
                dict_lines[self.ex.dict_without_punctuation_script[
                    self.ex.array_of_script_lines[line_script_index]]] = self.ex.dict_without_punctuation_srt[
                        self.ex.array_of_srt_lines[matching_probs_of_each_line.index(
                            max(matching_probs_of_each_line))]].rstrip().lstrip().lstrip("-")
                # now we take the srt line with the maximum matching prob ( lets say for example - "I know it's weird" )
                # than we check where doe's this line appeared, with self.ex.line_to_appearances_srt ( let's say it
                # appeared in the indexes 6,10 ie the sixth line is "I know it's weird" as well as the tenth line.
                # than we take the time of the line that appeared closer to our last result ie if for example our last
                # result was 5, than we will take the time of the sixth line, and appeand it into the array.
                # and in lines....
                best_matching_prob = max(matching_probs_of_each_line)
                best_matching_prob_index = matching_probs_of_each_line.index(best_matching_prob)
                best_line = self.ex.array_of_srt_lines[best_matching_prob_index]
                appearances_of_the_best_line = self.ex.line_to_appearances_srt[best_line]
                closest_appearance = min(appearances_of_the_best_line,
                                         key=lambda appearance: abs(appearance - last_result))
                time_of_closest_appearance = self.ex.line_index_to_line_time_srt[closest_appearance]
                best_time_arr.append(timeUnion.timeUnion(time_of_closest_appearance))

            else:
                #  we found at least one line with good ratio
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
                time_arr = []
                strings_with_punc = []
                for i in range(len(xSorted)):
                    #  for each line in the top ten we check if his neighbors are also lines that custom to our line
                    t.append((xSorted[i],))  # this will be tupple that hold each line neighbors that also custom
                    # as we did above, we take here the time of the closest appearnce of the line xSorted[i]
                    time_line = timeUnion.timeUnion(self.ex.line_index_to_line_time_srt[
                                                       min(self.ex.line_to_appearances_srt[self.ex.array_of_srt_lines[
                                                           xSorted[i]]], key=lambda appearance:
                                                           abs(appearance - last_result))])
                    best_str = self.ex.array_of_srt_lines[xSorted[i]]
                    best_str_punced = self.ex.dict_without_punctuation_srt[
                        self.ex.array_of_srt_lines[xSorted[i]]].rstrip().lstrip().lstrip("-")
                    ki = -1  # first we check for those who come before the top ten line
                    we_run_on_correct_values = ki + xSorted[i] in range(len(self.ex.array_of_srt_lines))
                    try:
                        last_best_ratio = SequenceMatcher(None, best_str, line_script).ratio()
                        curr_best_ratio = SequenceMatcher(None, self.ex.array_of_srt_lines[xSorted[i] + ki] +
                                                          " " + best_str, line_script).ratio()
                    except IndexError:
                        last_best_ratio = 0
                        curr_best_ratio = 0
                    while we_run_on_correct_values and last_best_ratio < curr_best_ratio:
                        best_str = self.ex.array_of_srt_lines[xSorted[i] + ki] + " " + best_str  # update best str
                        additional_str_punced = self.ex.dict_without_punctuation_srt[
                            self.ex.array_of_srt_lines[xSorted[i] + ki]]
                        best_str_punced = additional_str_punced.rstrip().lstrip().lstrip("-") + " " + \
                                          best_str_punced  # update the best str after punctuation
                        t[j] = t[j] + (xSorted[i] + ki,)  # the indexes of the lines that appears in the building
                        # as we did above, we take here the time of the closest appearnce of the line xSorted[i] + ki
                        time_line = time_line.union(timeUnion.timeUnion(self.ex.line_index_to_line_time_srt[min(
                            self.ex.line_to_appearances_srt[self.ex.array_of_srt_lines[xSorted[i] + ki]],
                            key=lambda appearance: abs(appearance - last_result))]))
                        ki -= 1
                        we_run_on_correct_values = ki + xSorted[i] in range(len(self.ex.array_of_srt_lines))
                        try:
                            last_best_ratio = SequenceMatcher(None, best_str, line_script).ratio()
                            curr_best_ratio = SequenceMatcher(None, self.ex.array_of_srt_lines[xSorted[i] + ki] +
                                                              " " + best_str, line_script).ratio()
                        except IndexError:
                            last_best_ratio = 0
                            curr_best_ratio = 0

                    ki = 1  # than we check for those who come after the top ten line
                    we_run_on_correct_values = ki + xSorted[i] in range(len(self.ex.array_of_srt_lines))
                    try:
                        last_best_ratio = SequenceMatcher(None, best_str, line_script).ratio()
                        curr_best_ratio = SequenceMatcher(None,
                                                          best_str + " " + self.ex.array_of_srt_lines[xSorted[i] + ki],
                                                          line_script).ratio()
                    except IndexError:
                        last_best_ratio = 0
                        curr_best_ratio = 0
                    while we_run_on_correct_values and last_best_ratio < curr_best_ratio:
                        best_str = best_str + " " + self.ex.array_of_srt_lines[xSorted[i] + ki]
                        best_str_punced = best_str_punced + " " + self.ex.dict_without_punctuation_srt[
                            self.ex.array_of_srt_lines[xSorted[i] + ki]].rstrip().lstrip().lstrip("-")
                        t[j] = t[j] + (xSorted[i] + ki,)
                        # as we did above, we take here the time of the closest appearnce of the line xSorted[i] + ki
                        time_line = time_line.union(
                            timeUnion.timeUnion(self.ex.line_index_to_line_time_srt[
                                                    min(self.ex.line_to_appearances_srt[self.ex.array_of_srt_lines[
                                                        xSorted[i] + ki]],
                                                        key=lambda appearance: abs(appearance - last_result))]))
                        ki += 1
                        we_run_on_correct_values = ki + xSorted[i] in range(len(self.ex.array_of_srt_lines))
                        try:
                            last_best_ratio = SequenceMatcher(None, best_str, line_script).ratio()
                            curr_best_ratio = SequenceMatcher(None,
                                                              best_str + " " + self.ex.array_of_srt_lines[
                                                                  xSorted[i] + ki],
                                                              line_script).ratio()
                        except IndexError:
                            last_best_ratio = 0
                            curr_best_ratio = 0
                    j = j + 1
                    ratio_str.append(SequenceMatcher(None, best_str,
                                                     line_script).ratio())  # we add the final ratio ( with neighbors )
                    strings.append(best_str)
                    time_arr.append(str(time_line))  # we add the time of the final
                    strings_with_punc.append(best_str_punced)
                the_best_distance = 0
                the_best_index = -1
                for numIndex in range(len(t)):
                    #  now we check which one had the highest results
                    num = t[numIndex]
                    if the_best_distance < normal_dis((1.0 / (1 + abs((num[0] - last_result))))) * ratio_str[numIndex]:
                        the_best_distance = normal_dis((1.0 / (1 + abs((num[0] - last_result))))) * ratio_str[numIndex]
                        the_best_index = numIndex
                dict_lines[self.ex.dict_without_punctuation_script[
                    self.ex.array_of_script_lines[line_script_index]]] = strings_with_punc[the_best_index]
                best_time_arr.append(time_arr[the_best_index])
            line_script_after_punc = self.ex.dict_without_punctuation_script[
                self.ex.array_of_script_lines[line_script_index]].rstrip().lstrip()
            line_srt_predicted = dict_lines[
                self.ex.dict_without_punctuation_script[
                    self.ex.array_of_script_lines[line_script_index]]].rstrip().lstrip()
            customize_ratio = max([SequenceMatcher(None, line_script_after_punc, line_srt_predicted).ratio(),
                                   SequenceMatcher(None, line_srt_predicted, line_script_after_punc).ratio()])
            index_of_customize_ratio = self.ex.initial_time.index(
                str(best_time_arr[line_script_index]).split(" --> ")[0])
            if customize_ratio < cut_off_almost_surely:
                #  the matching ratio not good enough, so therefore we do some things
                matching_probs_of_each_line = []
                for line_srt_index in range(len(self.ex.array_of_srt_lines)):
                    #  here we check the maximum ratio by using different matching type
                    line_srt = self.ex.array_of_srt_lines[line_srt_index]
                    matching_probs_of_each_line.append(SequenceMatcher(None, line_srt, line_script).ratio() *
                                                       normal_dis_for_results(line_srt_index - last_result))
                max_ratio = max(matching_probs_of_each_line)
                max_ratio_index = matching_probs_of_each_line.index(max_ratio)
                max_ratio = max_ratio * (1 / (normal_dis_for_results(1)))
                if max_ratio > (customize_ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                        index_of_customize_ratio - last_result)):
                    #  check if the result we got here is better than what we got at the other time
                    #  if it does, we use this result
                    if max_ratio > cut_off_not_sure or row_not_found > 2:
                        #  we didn't get bad result but we are not sure is good enough, we will still take it
                        # as we did above, we take here the time of the closest appearnce of the line with max ratio
                        time = str(timeUnion.timeUnion(self.ex.line_index_to_line_time_srt[min(
                            self.ex.line_to_appearances_srt[self.ex.array_of_srt_lines[max_ratio_index]],
                            key=lambda appearance: abs(appearance - last_result))]))
                        file_new.write(str(line_script_index + 1) + ". " + time + "\n" +
                                       self.ex.index_to_speaker_script[line_script_index] + "\n" +
                                       self.ex.dict_without_punctuation_script[
                                           self.ex.array_of_script_lines[line_script_index]].rstrip().lstrip() +
                                       " - Script" + "\n" +
                                       self.ex.dict_without_punctuation_srt[self.ex.array_of_srt_lines[
                                           matching_probs_of_each_line.index(
                                               max(matching_probs_of_each_line))]].rstrip().lstrip().lstrip(
                                           "-") + " - Srt" + "\n")
                        matching_probs_of_each_line.append(SequenceMatcher(None,
                                                                           self.ex.dict_without_punctuation_script[
                                                                               self.ex.array_of_script_lines[
                                                                                   line_script_index]].
                                                                           rstrip().lstrip(),
                                                                           self.ex.dict_without_punctuation_srt[
                                                                               self.ex.array_of_srt_lines[
                                                                                   max_ratio_index]].rstrip().lstrip().
                                                                           lstrip("-")).ratio())
                        row_not_found = 0
                    else:
                        #  the matching ratio were too low, therefore we decided that it's not in the srt
                        file_new.write(
                            str(line_script_index + 1) + ". 00:00:00,000 --> 00:00:00,000" + "\n" +
                            self.ex.index_to_speaker_script[
                                line_script_index] + "\n" + line_script_after_punc + unknown_line_massage)
                        row_not_found = row_not_found + 1
                else:
                    #  the try to find new ratio discovered as unsuccessful
                    if (customize_ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                            index_of_customize_ratio - last_result)) > cut_off_not_sure or row_not_found > 2:
                        #  not bad result, but not good, still we decided to take it
                        last_result = index_of_customize_ratio
                        file_new.write(
                            str(line_script_index + 1) + ". " + str(best_time_arr[line_script_index]) + "\n" +
                            self.ex.index_to_speaker_script[
                                line_script_index] + "\n" + line_script_after_punc +
                            " - Script" + "\n" + line_srt_predicted + " - Srt" + "\n")
                        matching_probs_of_each_line.append(customize_ratio)
                        row_not_found = 0
                    else:
                        #  the matching ratio were too low, therefore we decided that it's not in the srt
                        file_new.write(
                            str(line_script_index + 1) + ". 00:00:00,000 --> 00:00:00,000" + "\n" +
                            self.ex.index_to_speaker_script[
                                line_script_index] + "\n" + line_script_after_punc + unknown_line_massage)
                        row_not_found = row_not_found + 1

            else:
                #  the ratio of the words is good but we also want to check the distance between last word
                if (customize_ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                        ((index_of_customize_ratio - last_result)))) > cut_off_not_sure or row_not_found > 2:
                    #  its were above our cutoff therefore we took it
                    last_result = index_of_customize_ratio
                    file_new.write(
                        str(line_script_index + 1) + ". " + str(best_time_arr[line_script_index]) + "\n" +
                        self.ex.index_to_speaker_script[
                            line_script_index] + "\n" + line_script_after_punc +
                        " - Script" + "\n" + line_srt_predicted + " - Srt" + "\n")
                    matching_probs_of_each_line.append(customize_ratio)
                    row_not_found = 0
                else:
                    #  it weren't good after the distance check so we check for new line by using different method
                    matching_probs_of_each_line = []
                    for line_srt_index in range(len(self.ex.array_of_srt_lines)):
                        line_srt = self.ex.array_of_srt_lines[line_srt_index]
                        matching_probs_of_each_line.append(SequenceMatcher(None, line_srt, line_script).ratio() *
                                            normal_dis_for_results(line_srt_index - last_result))
                    max_ratio = max(matching_probs_of_each_line)
                    max_ratio_index = matching_probs_of_each_line.index(max_ratio)
                    max_ratio = max_ratio * (1 / (normal_dis_for_results(1)))
                    if max_ratio > cut_off_not_sure or row_not_found > 2:
                        #  check if the new ratio worked
                        last_result = max_ratio_index
                        # as we did above, we take here the time of the closest appearnce of the line with max ratio
                        time_specific_line = str(timeUnion.timeUnion(
                            self.ex.line_index_to_line_time_srt[min(
                                self.ex.line_to_appearances_srt[self.ex.array_of_srt_lines[max_ratio_index]],
                                key=lambda appearance: abs(appearance - last_result))]))
                        file_new.write(str(line_script_index + 1) + ". " + time_specific_line + "\n" +
                                       self.ex.index_to_speaker_script[line_script_index] + "\n" +
                                       self.ex.dict_without_punctuation_script[self.ex.array_of_script_lines[
                                           line_script_index]].rstrip().lstrip() + " - Script" + "\n" +
                                       self.ex.dict_without_punctuation_srt[self.ex.array_of_srt_lines[
                                           matching_probs_of_each_line.index(
                                               max(matching_probs_of_each_line))]].rstrip().lstrip().lstrip(
                                           "-") + " - Srt" + "\n")
                        matching_probs_of_each_line.append(
                            SequenceMatcher(None, self.ex.dict_without_punctuation_script[self.
                                            ex.array_of_script_lines[line_script_index]].rstrip().lstrip(),
                                            self.ex.dict_without_punctuation_srt[self.ex.array_of_srt_lines[
                                                                   max_ratio_index]].rstrip().lstrip().lstrip(
                                                               "-")).ratio())
                        row_not_found = 0
                    else:
                        #  the new ratio didn't work ( low ratio ) therefore we decided that the line is no in the srt
                        file_new.write(
                            str(line_script_index + 1) + ". 00:00:00,000 --> 00:00:00,000" + "\n" +
                            self.ex.index_to_speaker_script[
                                line_script_index] + "\n" + line_script_after_punc + unknown_line_massage)
                        row_not_found = row_not_found + 1

        return sum(matching_probs_of_each_line) / len(matching_probs_of_each_line)  # our confidence in repentance


if len(sys.argv) == 1:
    d = UnionScriptSrt("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt", constants.access_token)
    d.download_from_dropbox(constants.url_script, constants.url_srt)
    d.create_probability_matrix_for_each_word()
    print(d.union_files(constants.outputfile))
elif len(sys.argv) == 2:
    srtFilesPath = 'C:\\Users\\omer\\PycharmProjects\\MainProject\\FinalProject\\srt-scrip\\srt-all\\The_Big_Bang_Theory - season 1.en'
    srtFiles = [f for f in listdir(srtFilesPath) if isfile(join(srtFilesPath, f))]  # Files in dir
    scriptFilesPath = 'C:\\Users\\omer\\PycharmProjects\\MainProject\\FinalProject\\srt-scrip\\scripts'
    scriptFiles = [f for f in listdir(scriptFilesPath) if isfile(join(scriptFilesPath, f))]  # Files in dir
    for i in range(0, len(srtFiles)):
        d = UnionScriptSrt("script.txt", r"(.*):(.*)", r"\d\n\n(.*?)\n\n(.*?)\n\n\n\n", "srt.txt",
                           constants.access_token)
        srtFiles = [x for x in srtFiles if " HDTV.CTU.en.srt" in x or " HDTV.YesTV.en.srt" in x]
        scriptFiles.sort(key=lambda f: int(filter(str.isdigit, f)))
        srtFiles.sort(key=lambda f: int(filter(str.isdigit, f)))
        print(srtFiles)
        print(scriptFiles)
        fsrtdrop = open(srtFilesPath + "\\" + srtFiles[int(i)], 'r')  # , encoding="utf8")
        fsrt = open('srt.txt', 'w')
        for line in fsrtdrop.readlines():
            fsrt.write(line)
            fsrt.write("\n")
        fscriptdrop = open(scriptFilesPath + "\\" + scriptFiles[i], 'r')  # , encoding="utf8")
        fscript = open('script.txt', 'w')
        lines = fscriptdrop.readlines()
        for line in lines:
            fscript.write(line)
            fscript.write("\n")
        d.create_probability_matrix_for_each_word()
        print(d.union_files('outputfilenew_' + str(i + 1) + '.txt'))

else:
    d = UnionScriptSrt("script.txt", r"(.*):(.*)", r"\d\n(.*?)\n(.*?)\n\n", "srt.txt", constants.access_token)
    d.create_probability_matrix_for_each_word()
    print(d.union_files('outputfilenew' + '.txt'))