"""
This is an python 2 written code to union srt file and script file ( which are being used in the movie industry )
The code was created by Omer Sassoni and Ofek Poraz at April-2020 for the final project
on Bar-Ilan University.
"""
import numpy
import operator
import math
import sys
import constants
import DropBoxDownloader
import scipy.stats
import TimeUnion
from os import listdir
from shutil import copyfile
from ExtractData import DataExtractor
from difflib import SequenceMatcher
from tqdm import tqdm
from os.path import isfile, join

MAX_FAULTS_IN_ROW = 5

unknown_line_massage = " - Script" + "\n" + "NO IN SRT!!!!" + " - Srt" + "\n"
normal_distribution = scipy.stats.norm(0.5, 1.5).pdf  # normal distribution pdf


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

    def __init__(self, script__file_path, script__match_pattern, srt__file_path, srt__match_pattern, access_token):
        """
        This function is the constructor for the class.
        :param script__file_path: the script file path we download from dropbox
        :param script__match_pattern: the regex we used to the script file
        :param srt__file_path: the path to the srt file that there we download from dropbox
        :param srt__match_pattern: the regex we used to the srt file
        :param access_token: access token for access the dropbox
        """
        self.script__file_path = script__file_path
        self.script__match_pattern = script__match_pattern
        self.srt__match_pattern = srt__match_pattern
        self.srt__file_path = srt__file_path
        self.access_token = access_token
        self.data = None
        self.srt__line_matching_probability_by_word = {
        }
        self.union__lines = {}  # the matches between the lines
        self.matched_times = []

    def download_from_dropbox(self, url_script, url_srt):
        """
        Download from dropbox the srt file and the script file.
        :param url_script: the url to the script
        :param url_srt: the url to the srt
        :return: download from dropbox to the script_file_path and srt_file_path
        """
        dropbox_downloader = DropBoxDownloader.DropBoxDownloader(self.access_token)
        dropbox_downloader.download_file(url_script, self.script__file_path)
        dropbox_downloader.download_file(url_srt, self.srt__file_path)

    def _match_probability_word_equals_to_line(self, srt__total_occurrences, word, script__total_occurrences,
                                               srt__line):
        """
        The function should calculate the probability of <word> equals to <srt__line>.
        :param srt__total_occurrences: Srt file total occurrences of words.
        :param word: The word we wish to check is probability to <srt__line>
        :param script__total_occurrences: The script total occurrences of words.
        :param srt__line: The srt line we wish to check the probability that <word> is in her.
        :return: The probability.
        """
        srt__word_occurrences = self.data.srt__occurrences_number_by_word[word]
        script__word_occurrences = self.data.script__occurrences_number_by_word[word]
        srt__number_of_words_in_line = len(srt__line.split(' '))

        return (srt__total_occurrences - 5 * srt__word_occurrences) / float(srt__total_occurrences) * float(
            (script__total_occurrences - 5 * script__word_occurrences)) / float(
            script__total_occurrences * srt__number_of_words_in_line)

    def _make_word_to_line_matching_matrix(self, word, script__line, srt__total_occurrences, script__total_occurrences):
        """
        The function should append to self.srt__line_matching_probability_by_word the matrix that indicates
        the probability for each line that the word is equal to this line.
        :param word: The word we wish to create a matrix for.
        :param script__line: The script line where we took the word.
        :param srt__total_occurrences: The srt total occurrences of words.
        :param script__total_occurrences: The script total occurrences of words.
        """
        line_word_matrix = numpy.zeros((1, len(self.data.srt__lines)))  # this will be our matrix
        # for this word
        is_matrix_have_calculated = word in self.srt__line_matching_probability_by_word.keys()
        if not is_matrix_have_calculated:
            # if we already computed the matrix we don't need again
            for srt__line_index in range(len(self.data.srt__lines)):
                srt__line = self.data.srt__lines[srt__line_index]
                srt__line_words = srt__line.split(' ')
                if word in srt__line_words and srt__line and script__line:
                    srt__line_probability = self._match_probability_word_equals_to_line(srt__total_occurrences, word,
                                                                                        script__total_occurrences,
                                                                                        script__line)
                    line_word_matrix[0][srt__line_index] = srt__line_probability
                    # factorized probability of word in line
        self.srt__line_matching_probability_by_word[word] = line_word_matrix  # add to a dictionary

    def create_probability_matrix_for_each_word(self):
        """
        make a dictionary with the matching ratio of every word to every line in srt
        example - if the word "hi" appears only one time in the first line, two times in the third line
        and zero times at all the other lines, than the matrix for the word "hi" will be something like that:
                            hiMatrix = [someRatio, 0, someRatio * 2, 0 ... ]
        Note: it can look a bit different.
        """
        self.data = DataExtractor(self.script__file_path, self.script__match_pattern, self.srt__match_pattern,
                                  self.srt__file_path)  # this class extract data from srt, script files
        self.data.find_matches_script()  # the method that extract data from script file
        self.data.find_matches_srt()  # the method that extract data from srt file
        script__total_occurrences = sum(self.data.script__occurrences_number_by_word.values())
        srt__total_occurrences = sum(self.data.srt__occurrences_number_by_word.values())

        for script__line_index in tqdm(range(len(self.data.script__lines))):
            script__line = self.data.script__lines[script__line_index]  # the line of this iteration
            script__line_words = script__line.split(' ')
            for word in script__line_words:
                self._make_word_to_line_matching_matrix(word, script__line, srt__total_occurrences,
                                                        script__total_occurrences)

    def _create_probability_matrix_for_line(self, script__line):
        """
        The function should create a line matching matrix for each word ( meaning includes the probability to match to
        each line in srt file for every word in the line )
        :param script__line: The script line we wish to create the matrix for.
        :return: The matrix.
        """

        script__line_words = script__line.split(' ')
        # this will be matrix of the each word and his ratio to line in srt
        script__line_per_word_matching_matrix = self.srt__line_matching_probability_by_word[script__line_words[0]]
        for word in script__line_words[1:]:
            #  we build a matrix that her rows will be the words
            #  of the script and the columns will be ratios of each line in srt
            script__line_per_word_matching_matrix = numpy.row_stack((script__line_per_word_matching_matrix,
                                                                     self.srt__line_matching_probability_by_word[word]))
        return script__line_per_word_matching_matrix

    def _match_probability_lines(self, script__line, srt__line, last_result_line_index):
        """
        The function computes the matching probability between <srt__line> to <script__line>.
        :param script__line: The script line we wish to compare to <srt__line>
        :param srt__line: The srt line we wish to compare to <script__line>
        :param last_result_line_index: The last match index of line matched to a script line.
        :return: The probability of the matching between both lines
        """

        content_matching = SequenceMatcher(None, srt__line, script__line).ratio()
        distance_matching = normal_distribution(
            (1.0 / (1 + abs((self.data.srt__lines.index(srt__line) - last_result_line_index)))))
        return content_matching * distance_matching

    def find_match_in_case_no_clear_match(self, script__line_index, last_result_line_index):
        """
        The function should find match to script__line in index - <script__line_index> when there is no clear match
        using sequence matcher.
        :param script__line_index: The script line index.
        :param last_result_line_index: The last found index.
        """

        script__line = self.data.script__lines[script__line_index]
        # if we didn't get line that have good ratio we check which line have the best matching in term
        # of distance and words by a more longer process.
        lines_matching_probability = []
        for srt__line in self.data.srt__lines:
            lines_matching_probability.append(
                self._match_probability_lines(script__line, srt__line, last_result_line_index))
        srt__matched_line = self.data.srt__lines[lines_matching_probability.index(
            max(lines_matching_probability))]
        srt__matched_line_without_punctuation = self.data.srt__lines_without_punctuations[
            srt__matched_line].rstrip().lstrip().lstrip("-")
        script__matched_line_without_punctuation = self.data.script__lines_without_punctuations[
            self.data.script__lines[script__line_index]]

        self.union__lines[script__matched_line_without_punctuation] = srt__matched_line_without_punctuation
        # There are some lines that are identical so we take the line with the closest distance to our last result
        occurrences_of_matched_line = self.data.srt__line_occurrences_by_line[srt__matched_line]
        closest_occurrence = min(occurrences_of_matched_line,
                                 key=lambda appearance: abs(appearance - last_result_line_index))
        matched_occurrence_time = self.data.srt__line_time_by_line_index[closest_occurrence]
        self.matched_times.append(TimeUnion.TimeUnion(matched_occurrence_time))

    def find_neighbors_matches(self, optional_matched_line_index, script__line, last_result_line_index):
        """
        This function check if there is a lines that are neighbors of the <optional_matched_line_index>
        and can be addition to the line in order to build a new line that will be more identical to the <script__line>
        :param optional_matched_line_index: The line that optionally match to <script__line>.
        :param script__line: The line that we search for matches in srt__lines.
        :param last_result_line_index: The last srt line index that found for the previous script__line.
        :return: final_matched_line, match_time, final_matched_line_without_punctuations, script__line_total_matches
        when script__line_total_matches is the neighbors that also match to script__line.
        """

        script__line_total_matches = (optional_matched_line_index,)
        optional_matched_line = self.data.srt__lines[optional_matched_line_index]
        # There are some lines that are identical so we take the closest match.
        closest_line_index = min(self.data.srt__line_occurrences_by_line[optional_matched_line],
                                 key=lambda appearance: abs(appearance - last_result_line_index))
        match_time = TimeUnion.TimeUnion(self.data.srt__line_time_by_line_index[closest_line_index])
        final_matched_line = optional_matched_line
        final_matched_line_without_punctuations = self.data.srt__lines_without_punctuations[
            optional_matched_line].rstrip().lstrip().lstrip("-")

        # if a line is matched probably his neighbors also matched
        neighbor_relative_index = -1
        we_run_on_correct_values = neighbor_relative_index + optional_matched_line_index in range(
            len(self.data.srt__lines))
        if we_run_on_correct_values:
            last_best_ratio = SequenceMatcher(None, final_matched_line, script__line).ratio()
            curr_best_ratio = SequenceMatcher(None, self.data.srt__lines[
                optional_matched_line_index + neighbor_relative_index] + " " + final_matched_line, script__line).ratio()
        else:
            last_best_ratio = 0
            curr_best_ratio = 0
        while last_best_ratio < curr_best_ratio:
            final_matched_line = self.data.srt__lines[
                                     optional_matched_line_index + neighbor_relative_index] + " " + final_matched_line
            current_neighbor_line_without_punctuation = self.data.srt__lines_without_punctuations[
                self.data.srt__lines[optional_matched_line_index + neighbor_relative_index]]
            final_matched_line_without_punctuations = current_neighbor_line_without_punctuation.rstrip().lstrip().lstrip(
                "-") + " " + final_matched_line_without_punctuations
            script__line_total_matches = script__line_total_matches + (
                optional_matched_line_index + neighbor_relative_index,)
            match_time = match_time.union(TimeUnion.TimeUnion(self.data.srt__line_time_by_line_index[min(
                self.data.srt__line_occurrences_by_line[
                    self.data.srt__lines[optional_matched_line_index + neighbor_relative_index]],
                key=lambda appearance: abs(appearance - last_result_line_index))]))
            neighbor_relative_index -= 1
            we_run_on_correct_values = neighbor_relative_index + optional_matched_line_index in range(
                len(self.data.srt__lines))
            if we_run_on_correct_values:
                last_best_ratio = SequenceMatcher(None, final_matched_line, script__line).ratio()
                curr_best_ratio = SequenceMatcher(None, self.data.srt__lines[
                    optional_matched_line_index + neighbor_relative_index] +
                                                  " " + final_matched_line, script__line).ratio()
            else:
                break

        neighbor_relative_index = 1  # than we check for those who come after the top ten line
        we_run_on_correct_values = neighbor_relative_index + optional_matched_line_index in range(
            len(self.data.srt__lines))
        if we_run_on_correct_values:
            last_best_ratio = SequenceMatcher(None, final_matched_line, script__line).ratio()
            curr_best_ratio = SequenceMatcher(None,
                                              final_matched_line + " " + self.data.srt__lines[
                                                  optional_matched_line_index + neighbor_relative_index],
                                              script__line).ratio()
        else:
            last_best_ratio = 0
            curr_best_ratio = 0
        while last_best_ratio < curr_best_ratio:
            final_matched_line = final_matched_line + " " + self.data.srt__lines[
                optional_matched_line_index + neighbor_relative_index]
            final_matched_line_without_punctuations = final_matched_line_without_punctuations + " " + \
                                                      self.data.srt__lines_without_punctuations[
                                                          self.data.srt__lines[
                                                              optional_matched_line_index + neighbor_relative_index]].rstrip().lstrip().lstrip(
                                                          "-")
            script__line_total_matches = script__line_total_matches + (
                optional_matched_line_index + neighbor_relative_index,)
            match_time = match_time.union(
                TimeUnion.TimeUnion(self.data.srt__line_time_by_line_index[
                                        min(self.data.srt__line_occurrences_by_line[
                                                self.data.srt__lines[
                                                    optional_matched_line_index + neighbor_relative_index]],
                                            key=lambda appearance: abs(
                                                appearance - last_result_line_index))]))
            neighbor_relative_index += 1
            we_run_on_correct_values = neighbor_relative_index + optional_matched_line_index in range(
                len(self.data.srt__lines))
            if we_run_on_correct_values:
                last_best_ratio = SequenceMatcher(None, final_matched_line, script__line).ratio()
                curr_best_ratio = SequenceMatcher(None,
                                                  final_matched_line + " " + self.data.srt__lines[
                                                      optional_matched_line_index + neighbor_relative_index],
                                                  script__line).ratio()
            else:
                break

        return final_matched_line, match_time, final_matched_line_without_punctuations, script__line_total_matches

    @staticmethod
    def _get_highest_match_index(script__line_total_matches, last_result_line_index, optional_matches_ratios):
        """
        The function should compute the highest match from <script__line_total_matches> and <optional_matches_ratios>.
        :param script__line_total_matches: The optional matches.
        :param last_result_line_index: The last match index of srt.
        :param optional_matches_ratios: The optional matches ratios when comparing to our script__line.
        :return: The highest match index.
        """

        highest_match_ratio = 0
        highest_match_index = -1
        for match_index in range(len(script__line_total_matches)):
            #  now we check which one had the highest results
            match = script__line_total_matches[match_index]
            starting_match_line_index = match[0]
            current_match_distance_ratio = normal_distribution((1.0 / (1 + abs((starting_match_line_index -
                                                                                last_result_line_index)))))
            current_match_total_ratio = current_match_distance_ratio * optional_matches_ratios[match_index]
            if highest_match_ratio < current_match_total_ratio:
                highest_match_ratio = current_match_total_ratio
                highest_match_index = match_index
        return highest_match_index

    def union_files(self, union_file_output_path):
        """
        Union an srt file and a script file into one file and write it in the <union_file_output_path>
        file that the function gets as input
        :param union_file_output_path: the file output path which there will be written the union file
        """

        output_file = open(union_file_output_path, 'w')
        match_probability_cutoff = constants.cutoff_ratio  # cutoff that ratio below that will not be written in the union file
        cut_off_almost_surely = constants.cut_off_almost_surely
        cut_off_not_sure = constants.cut_off_not_sure
        last_result_line_index = -1  # the last index of the script line that the srt line was customized
        lines_matching_probability = []  # array with the matching ratios
        number_of_no_found_matching_in_row = 0  # how much rows we didn'neighbors_matched find from the last found

        for script__line_index in tqdm(range(len(self.data.script__lines))):
            script__line = self.data.script__lines[script__line_index]
            script__line_words = script__line.split(" ")
            if "What have we been" in script__line:
                pass
            script__line_per_word_matching_matrix = self._create_probability_matrix_for_line(script__line)
            script__line_matching_matrix = numpy.dot(numpy.ones((1, len(script__line_words))),
                                                     script__line_per_word_matching_matrix)

            max_match_probability = max(script__line_matching_matrix[0])
            if max_match_probability < match_probability_cutoff:
                self.find_match_in_case_no_clear_match(script__line_index, last_result_line_index)
            else:
                # we found at least one line with good ratio
                matched_probabilities = list(enumerate(script__line_matching_matrix[0]))
                sorted_matched_probabilities = sorted(matched_probabilities, key=operator.itemgetter(1))
                highest_matches = sorted_matched_probabilities[-constants.to_overview_results_number:]  # we check only the top results
                temp_highest_matches = sorted_matched_probabilities[-constants.to_overview_results_number:]
                # remove bad ratios
                for srt__line_index, match_probability in temp_highest_matches:
                    if match_probability < match_probability_cutoff:
                        highest_matches.remove((srt__line_index, match_probability))

                highest_matches_indexes = sorted(
                    list(reversed([index for index, match_probability in highest_matches])))
                script__line_total_matches = []
                optional_matches_ratios = []
                optional_matches_times = []
                optional_matches_final_line = []
                # we now check if the neighbors of the highest matches also involved in creating the script__line
                for optional_matched_line_index in highest_matches_indexes:
                    final_matched_line, match_time, final_matched_line_without_punctuations, script__line_curr_matches \
                        = self.find_neighbors_matches(optional_matched_line_index, script__line, last_result_line_index)
                    script__line_total_matches += [script__line_curr_matches]
                    optional_matches_ratios.append(SequenceMatcher(None, final_matched_line,
                                                                   script__line).ratio())
                    optional_matches_times.append(str(match_time))  # we add the time of the final
                    optional_matches_final_line.append(final_matched_line_without_punctuations)

                highest_match_index = UnionScriptSrt._get_highest_match_index(script__line_total_matches,
                                                                              last_result_line_index,
                                                                              optional_matches_ratios)
                self.union__lines[self.data.script__lines_without_punctuations[
                    self.data.script__lines[script__line_index]]] = optional_matches_final_line[highest_match_index]
                self.matched_times.append(optional_matches_times[highest_match_index])

            script__line_without_punctuation = self.data.script__lines_without_punctuations[
                self.data.script__lines[script__line_index]].rstrip().lstrip()
            highest_match = self.union__lines[self.data.script__lines_without_punctuations[
                self.data.script__lines[script__line_index]]].rstrip().lstrip()
            matching_ratio = max([SequenceMatcher(None, script__line_without_punctuation, highest_match).ratio(),
                                  SequenceMatcher(None, highest_match, script__line_without_punctuation).ratio()])
            highest_match_initial_time = str(self.matched_times[script__line_index]).split(" --> ")[0]
            matching_lines_initial_index = self.data.srt__lines_initial_time.index(highest_match_initial_time)
            if matching_ratio < cut_off_almost_surely:
                #  the matching ratio not good enough, so therefore we do some things
                lines_matching_probability = []
                for line_srt_index in range(len(self.data.srt__lines)):
                    #  here we check the maximum ratio by using different matching type
                    srt__line = self.data.srt__lines[line_srt_index]
                    lines_matching_probability.append(SequenceMatcher(None, srt__line, script__line).ratio() *
                                                      normal_dis_for_results(line_srt_index - last_result_line_index))
                max_ratio = max(lines_matching_probability)
                max_ratio_index = lines_matching_probability.index(max_ratio)
                max_ratio = max_ratio * (1 / (normal_dis_for_results(1)))
                if max_ratio > (matching_ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                        matching_lines_initial_index - last_result_line_index)):
                    #  check if the result we got here is better than what we got at the other time
                    #  if it does, we use this result
                    if max_ratio > cut_off_not_sure or number_of_no_found_matching_in_row > MAX_FAULTS_IN_ROW:
                        #  we didn'neighbors_matched get bad result but we are not sure is good enough, we will still take it
                        # as we did above, we take here the time of the closest appearnce of the line with max ratio
                        time = str(TimeUnion.TimeUnion(self.data.srt__line_time_by_line_index[min(
                            self.data.srt__line_occurrences_by_line[self.data.srt__lines[max_ratio_index]],
                            key=lambda appearance: abs(appearance - last_result_line_index))]))
                        output_file.write(str(script__line_index + 1) + ". " + time + "\n" +
                                          self.data.script__speaker_by_line_index[script__line_index] + "\n" +
                                          self.data.script__lines_without_punctuations[
                                              self.data.script__lines[script__line_index]].rstrip().lstrip() +
                                          " - Script" + "\n" +
                                          self.data.srt__lines_without_punctuations[self.data.srt__lines[
                                              lines_matching_probability.index(
                                                  max(lines_matching_probability))]].rstrip().lstrip().lstrip(
                                              "-") + " - Srt" + "\n")
                        lines_matching_probability.append(SequenceMatcher(None,
                                                                          self.data.script__lines_without_punctuations[
                                                                              self.data.script__lines[
                                                                                  script__line_index]].
                                                                          rstrip().lstrip(),
                                                                          self.data.srt__lines_without_punctuations[
                                                                              self.data.srt__lines[
                                                                                  max_ratio_index]].rstrip().lstrip().
                                                                          lstrip("-")).ratio())
                        number_of_no_found_matching_in_row = 0
                    else:
                        #  the matching ratio were too low, therefore we decided that it's not in the srt
                        output_file.write(
                            str(script__line_index + 1) + ". 00:00:00,000 --> 00:00:00,000" + "\n" +
                            self.data.script__speaker_by_line_index[
                                script__line_index] + "\n" + script__line_without_punctuation + unknown_line_massage)
                        number_of_no_found_matching_in_row = number_of_no_found_matching_in_row + 1
                        last_result_line_index += 1
                else:
                    #  the try to find new ratio discovered as unsuccessful
                    if (matching_ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                            matching_lines_initial_index - last_result_line_index)) > cut_off_not_sure or number_of_no_found_matching_in_row > MAX_FAULTS_IN_ROW:
                        #  not bad result, but not good, still we decided to take it
                        last_result_line_index = matching_lines_initial_index
                        output_file.write(
                            str(script__line_index + 1) + ". " + str(self.matched_times[script__line_index]) + "\n" +
                            self.data.script__speaker_by_line_index[
                                script__line_index] + "\n" + script__line_without_punctuation +
                            " - Script" + "\n" + highest_match + " - Srt" + "\n")
                        lines_matching_probability.append(matching_ratio)
                        number_of_no_found_matching_in_row = 0
                    else:
                        #  the matching ratio were too low, therefore we decided that it's not in the srt
                        output_file.write(
                            str(script__line_index + 1) + ". 00:00:00,000 --> 00:00:00,000" + "\n" +
                            self.data.script__speaker_by_line_index[
                                script__line_index] + "\n" + script__line_without_punctuation + unknown_line_massage)
                        number_of_no_found_matching_in_row = number_of_no_found_matching_in_row + 1
                        last_result_line_index += 1

            else:
                #  the ratio of the words is good but we also want to check the distance between last word
                if (matching_ratio * (1 / (normal_dis_for_results(1))) * normal_dis_for_results(
                        ((
                                matching_lines_initial_index - last_result_line_index)))) > cut_off_not_sure or number_of_no_found_matching_in_row > MAX_FAULTS_IN_ROW:
                    #  its were above our cutoff therefore we took it
                    last_result_line_index = matching_lines_initial_index
                    output_file.write(
                        str(script__line_index + 1) + ". " + str(self.matched_times[script__line_index]) + "\n" +
                        self.data.script__speaker_by_line_index[
                            script__line_index] + "\n" + script__line_without_punctuation +
                        " - Script" + "\n" + highest_match + " - Srt" + "\n")
                    lines_matching_probability.append(matching_ratio)
                    number_of_no_found_matching_in_row = 0
                else:
                    #  it weren'neighbors_matched good after the distance check so we check for new line by using different method
                    lines_matching_probability = []
                    for line_srt_index in range(len(self.data.srt__lines)):
                        srt__line = self.data.srt__lines[line_srt_index]
                        lines_matching_probability.append(SequenceMatcher(None, srt__line, script__line).ratio() *
                                                          normal_dis_for_results(
                                                              line_srt_index - last_result_line_index))
                    max_ratio = max(lines_matching_probability)
                    max_ratio_index = lines_matching_probability.index(max_ratio)
                    max_ratio = max_ratio * (1 / (normal_dis_for_results(1)))
                    if max_ratio > cut_off_not_sure or number_of_no_found_matching_in_row > MAX_FAULTS_IN_ROW:
                        #  check if the new ratio worked
                        last_result_line_index = max_ratio_index
                        # as we did above, we take here the time of the closest appearnce of the line with max ratio
                        time_specific_line = str(TimeUnion.TimeUnion(
                            self.data.srt__line_time_by_line_index[min(
                                self.data.srt__line_occurrences_by_line[
                                    self.data.srt__lines[max_ratio_index]],
                                key=lambda appearance: abs(appearance - last_result_line_index))]))
                        output_file.write(str(script__line_index + 1) + ". " + time_specific_line + "\n" +
                                          self.data.script__speaker_by_line_index[script__line_index] + "\n" +
                                          self.data.script__lines_without_punctuations[
                                              self.data.script__lines[
                                                  script__line_index]].rstrip().lstrip() + " - Script" + "\n" +
                                          self.data.srt__lines_without_punctuations[self.data.srt__lines[
                                              lines_matching_probability.index(
                                                  max(lines_matching_probability))]].rstrip().lstrip().lstrip(
                                              "-") + " - Srt" + "\n")
                        lines_matching_probability.append(
                            SequenceMatcher(None, self.data.script__lines_without_punctuations[self.
                                            data.script__lines[script__line_index]].rstrip().lstrip(),
                                            self.data.srt__lines_without_punctuations[
                                                self.data.srt__lines[
                                                    max_ratio_index]].rstrip().lstrip().lstrip(
                                                "-")).ratio())
                        number_of_no_found_matching_in_row = 0
                    else:
                        #  the new ratio didn'neighbors_matched work ( low ratio ) therefore we decided that the line is no in the srt
                        output_file.write(
                            str(script__line_index + 1) + ". 00:00:00,000 --> 00:00:00,000" + "\n" +
                            self.data.script__speaker_by_line_index[
                                script__line_index] + "\n" + script__line_without_punctuation + unknown_line_massage)
                        number_of_no_found_matching_in_row = number_of_no_found_matching_in_row + 1
                        last_result_line_index += 1

        return sum(lines_matching_probability) / len(lines_matching_probability)  # our confidence in repentance


if __name__ == '__main__':

    if len(sys.argv) == 1:  # download from 'drop-box' the url that given in constant.
        d = UnionScriptSrt("script.txt", r"(.*):(.*)", "srt.txt", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n",
                           constants.access_token)
        d.download_from_dropbox(constants.url_script, constants.url_srt)
        d.create_probability_matrix_for_each_word()
        print(d.union_files(constants.outputfile))

    elif len(sys.argv) == 2:  # take from a folder of script, srt the files that we need

        d = UnionScriptSrt("script.txt", r"(.*):(.*)", "srt.txt", r"\d\n(.*?)\n(.*?)\n\n", constants.access_token)
        d.create_probability_matrix_for_each_word()
        print(d.union_files('outputfilenew' + '.txt'))

    else:  # take the srt and the script file that are in the folder
        srtFilesPath = 'srt-scrip\\srt-all\\The_Big_Bang_Theory - season 1.en'
        srtFiles = [f for f in listdir(srtFilesPath) if isfile(join(srtFilesPath, f))]  # Files in dir
        scriptFilesPath = 'srt-scrip\\scripts'
        scriptFiles = [f for f in listdir(scriptFilesPath) if isfile(join(scriptFilesPath, f))]  # Files in dir
        for i in range(0, len(srtFiles)):
            d = UnionScriptSrt("script.txt", r"(.*):(.*)", "srt.txt", r"\d\n(.*?)\n(.*?)\n\n",
                               constants.access_token)
            srtFiles = [x for x in srtFiles if " HDTV.CTU.en.srt" in x or " HDTV.YesTV.en.srt" in x]
            scriptFiles.sort(key=lambda f: int(filter(str.isdigit, f)))
            srtFiles.sort(key=lambda f: int(filter(str.isdigit, f)))
            print(srtFiles)
            print(scriptFiles)
            copyfile(srtFilesPath + "\\" + srtFiles[int(i)], 'srt.txt')
            copyfile(scriptFilesPath + "\\" + scriptFiles[i], 'script.txt')
            d.create_probability_matrix_for_each_word()
            print(d.union_files('outputfilenew_' + str(i + 1) + '.txt'))
