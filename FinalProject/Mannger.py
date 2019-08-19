import DropBoxDownloader
import RegexMaker
from difflib import SequenceMatcher
import scipy.stats
import timeUnion
from tqdm import tqdm
import constants


class Mannager:
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
        normal_dis = scipy.stats.norm(float(len(rm.arr_words_script)) / float(len(rm.arr_words_srt)), 1.5).pdf
        line_to_line = {}
        for t in tqdm(range(num_of_lines)):
            line = rm.arr_words_srt[t]
            j = 1
            arr_ranking = {
            }
            arr_ranking_only_sequence_matcher = {
            }
            l_i = max(t / 2 - 10, 0)
            cut_off = 0.4
            while l_i in range(t / 2 - 10, int(t * 1.5 + 10)) and l_i in range(len(rm.arr_words_script)):
                i = 0
                l = rm.arr_words_script[l_i]
                k = len(l)
                while SequenceMatcher(None, l[i:k], line).ratio() < SequenceMatcher(None, l[i + 2:k], line).ratio():
                    i = i + 2
                while SequenceMatcher(None, l[i:k], line).ratio() < SequenceMatcher(None, l[i:k - 2], line).ratio():
                    k = k - 2
                arr_ranking[SequenceMatcher(None, l[i:k], line).ratio() + (1.0 / 0.13) * normal_dis(float(j) / float(t + 1))] = (
                l, j, t + 1)
                arr_ranking_only_sequence_matcher[SequenceMatcher(None, l[i:k], line).ratio()] = (
                l, j, t + 1)
                j += 1
                l_i += 1
            #if arr_ranking_only_sequence_matcher[max(arr_ranking_only_sequence_matcher.keys())][0] < cut_off:
            #    j = 1
            #    arr_ranking = {
            #    }
            #    l_i = max(t / 2 - 10, 0)
            #    while l_i in range(t / 2 - 10, int(t * 1.5 + 10)) and l_i in range(len(rm.arr_words_script)):
            #        i = 0
            #        i_max = 0
            #        k_max = 0
            #        ratio_max = 0
            #        l = rm.arr_words_script[l_i]
            #        k = len(l)
            #        while i < len(l):
            #            if SequenceMatcher(None, l[i:k], line).ratio() > ratio_max:
            #                i_max = i
            #                ratio_max = SequenceMatcher(None, l[i:k], line).ratio()
            #            i = i + 2
            #        while k > i_max:
            #            if SequenceMatcher(None, l[i_max:k], line).ratio() > ratio_max:
            #                k_max = k
            #                ratio_max = SequenceMatcher(None, l[i_max:k], line).ratio()
            #            k = k - 2
            #        i = i_max
            #        k = k_max
            #        arr_ranking[SequenceMatcher(None, l[i:k], line).ratio() + (1 / 0.13) * normal_dis(j / (t + 1))] = (
            #        l, j, t + 1)
            #        j += 1
            #        l_i += 1
            if arr_ranking[max(arr_ranking.keys())][0] in line_to_line.keys():
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]] = (
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]][0],
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]][1] + " " + line,
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]][2].union(
                    timeUnion.timeUnion(rm.srt_time[rm.srt_words[line]])))
                self.dict_position[line_to_line[arr_ranking[max(arr_ranking.keys())][0]][0]] = arr_ranking[max(arr_ranking.keys())][0]
            else:
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]] = (t,
                                                                         line, timeUnion.timeUnion(rm.srt_time[rm.srt_words[line]]))
                self.dict_position[line_to_line[arr_ranking[max(arr_ranking.keys())][0]][0]] = arr_ranking[max(arr_ranking.keys())][0]

        file_1 = open(output_file, 'w')
        file_2 = open("outputfile2.txt", 'w')
        for l in tqdm(sorted(self.dict_position.keys())):
            file_1.write(str(self.dict_position[l]) + " : " + str((str(line_to_line[self.dict_position[l]][2]), str(line_to_line[self.dict_position[l]][1]))) + "\n")
        index = 0
        for l_d in tqdm(sorted(self.dict_position.keys())):
            index += 1
            file_2.writelines([str(index) + ". " + str(line_to_line[self.dict_position[l_d]][2]) + "\n", rm.script_talkers[rm.script_words[self.dict_position[l_d]]] + "\n", rm.dict_without_punctuation_script[str(self.dict_position[l_d])] + " - Script" + "\n", str(line_to_line[self.dict_position[l_d]][1]) + " - Srt" + "\n"])

d = Mannager("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.main_action(constants.url_script, constants.url_srt, int(raw_input("How much raws?")), "outputfile.txt")
