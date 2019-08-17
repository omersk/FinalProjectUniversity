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

    def main_action(self, url_script, url_srt, num_of_lines, output_file):
        d = DropBoxDownloader.DropBoxDownloader(self.access_token)
        d.download_file(url_script, self.script_file_path)
        d.download_file(url_srt, self.srt_file_path)
        rm = RegexMaker.RegexMaker(self.script_file_path, self.regex_script, self.regex_srt, self.srt_file_path)
        rm.find_matches_script()
        rm.find_matches_srt()
        normal_dis = scipy.stats.norm(float(len(rm.arr_words_script)) / float(len(rm.arr_words_srt)), 3).pdf
        line_to_line = {}
        for t in tqdm(range(num_of_lines)):
            line = rm.arr_words_srt[t]
            j = 1
            arr_ranking = {
            }
            l_i = max(t / 2 - 10, 0)
            while l_i in range(t / 2 - 10, int(t * 1.5 + 10)) and l_i in range(len(rm.arr_words_script)):
                i = 0
                l = rm.arr_words_script[l_i]
                k = len(l)
                while SequenceMatcher(None, l[i:k], line).ratio() < SequenceMatcher(None, l[i + 2:k], line).ratio():
                    i = i + 2
                while SequenceMatcher(None, l[i:k], line).ratio() < SequenceMatcher(None, l[i:k - 2], line).ratio():
                    k = k - 2
                arr_ranking[SequenceMatcher(None, l[i:k], line).ratio() + (1 / 0.13) * normal_dis(j / (t + 1))] = (
                l, j, t + 1)
                j += 1
                l_i += 1
            if arr_ranking[max(arr_ranking.keys())][0] in line_to_line.keys():
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]] = (
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]][0] + " " + line,
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]][1].union(
                    timeUnion.timeUnion(rm.srt_time[rm.srt_words[line]])))
            else:
                line_to_line[arr_ranking[max(arr_ranking.keys())][0]] = (
                line, timeUnion.timeUnion(rm.srt_time[rm.srt_words[line]]))

        file_1 = open(output_file, 'w')
        for l in tqdm(line_to_line):
            file_1.write(str(l) + " : " + str((line_to_line[l][0], str(line_to_line[l][1]))) + "\n")


d = Mannager("script.txt", r"(.*):(.*)", r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", "srt.txt",constants.access_token)
d.main_action(constants.url_script, constants.url_srt, 50, "outputfile.txt")
