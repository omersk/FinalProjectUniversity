import re
import string
from tqdm import tqdm

class RegexMakerZvi:
    def __init__(self, script_file_path="Test1.txt", regex_script=r"(.*):(.*)", regex_srt=r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", srt_file_path="Test.txt"):
        self.f_script = open(script_file_path, "r+")
        self.regex_script = regex_script
        self.script_talkers = {}
        self.script_words = {}
        self.dict_words_script = {}
        self.srt_time = {}
        self.dict_words_srt = {}
        self.dict_position_script = {}
        self.srt_words = {}
        self.arr_words_script = []
        self.arr_words_srt = []
        self.regex_srt = regex_srt
        self.f_srt = open(srt_file_path, "r+")
        self.dict_without_punctuation_script = {}
        self.dict_without_punctuation_srt = {}

    def find_matches_script(self):
        test_script = self.f_script.read()
        test_script = test_script[0:re.search(r'Advertisements', test_script).end()]

        matches_script = re.finditer(self.regex_script, test_script, re.MULTILINE)
        i = 0
        # LOOP SCRIPT ---------
        for matchNum, match in tqdm(enumerate(matches_script, start=1)):
            if "Scene" not in match.group(1):
                self.script_talkers[i] = match.group(1)
                line = str(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                                  match.group(2).replace("\xe2\x80\x99", "'")).replace('\r', '')).strip('(').replace('\n', ' ').rstrip().lstrip()
                line_without_punc = line.translate(None, string.punctuation)
                self.dict_without_punctuation_script[line_without_punc] = line
                line = line_without_punc
                self.script_words[line] = i
                self.arr_words_script.append(line)
                for word in line.split(" "):
                    if word in self.dict_words_script.keys():
                        self.dict_words_script[word] += 1
                    else:
                        self.dict_words_script[word] = 1
                i += 1

    def find_matches_srt(self):
        test_srt = self.f_srt.read()
        matches_srt = re.finditer(self.regex_srt, test_srt, re.MULTILINE | re.DOTALL)
        i = 0
        # LOOP SRT -----------
        for matchNum, match in tqdm(enumerate(matches_srt, start=1)):
            if "Scene" not in match.group(1):
                self.srt_time[i] = match.group(1)
                line = str(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                                  match.group(2).replace("\xe2\x80\x99", "'")).replace('\r', '')).strip('(').rstrip().lstrip()
                a = None
                if line[0] == "-":
                    a = line.split("\n")
                if not a:
                    line = line.replace('\n', ' ')#.translate(None, string.punctuation).replace('\n', ' ')
                    line_without_punc = line.translate(None, string.punctuation)
                    self.dict_without_punctuation_srt[line_without_punc] = line
                    line = line_without_punc
                    if line not in self.srt_words.keys():
                        self.srt_words[line] = (i,)
                    else:
                        self.srt_words[line] = self.srt_words[line] + (i,)
                    self.arr_words_srt.append(line)
                    for word in line.split(" "):
                        if word in self.dict_words_srt.keys():
                            self.dict_words_srt[word] += 1
                        else:
                            self.dict_words_srt[word] = 1
                if a:
                    for line_enter in a:
                        line_with_all = line_enter
                        self.srt_time[i] = match.group(1)
                        line_enter = str(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                                          line_enter.replace("\xe2\x80\x99", "'")).replace('\r', '')).strip(
                            '(').rstrip().lstrip()
                        line_enter = line_enter.replace('\n', ' ')#.translate(None, string.punctuation).replace('\n', ' ')
                        line_enter_without_punc = line_enter.translate(None, string.punctuation)
                        self.dict_without_punctuation_srt[line_enter_without_punc] = line_with_all
                        line_enter = line_enter_without_punc
                        if line_enter not in self.srt_words.keys():
                            self.srt_words[line_enter] = (i,)
                        else:
                            self.srt_words[line_enter] = self.srt_words[line_enter] + (i,)
                        self.arr_words_srt.append(line_enter)
                        for word in line_enter.split(" "):
                            if word in self.dict_words_srt.keys():
                                self.dict_words_srt[word] += 1
                            else:
                                self.dict_words_srt[word] = 1
                        i += 1
            i += 1

