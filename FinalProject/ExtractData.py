import constants
import re
import string
from tqdm import tqdm


class DataExtractor:
    """
    A class that came up to the world in order to take 2 files - srt file and script file
    and extract from this files the data that needs in order to union them.
    ...
        Methods
        -------
        __init__(self, script_file_path="Test1.txt", regex_script=r"(.*):(.*)",
                 regex_srt=r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", srt_file_path="Test.txt")
            The constructor for the class
        find_matches_script(self)
            extract the data from the script file
        find_matches_srt(self)
            extract the data from the srt file
    ...
    """
    def __init__(self, script_file_path="Test1.txt", regex_script=r"(.*):(.*)",
                 regex_srt=r"\d\r\n(.*?)\r\n(.*?)\r\n\r\n", srt_file_path="Test.txt"):
        """
        The constructor of the class
        :param script_file_path: the path of the script file
        :param regex_script: the regex structure of the script file
        :param regex_srt: the regex structure of the srt file
        :param srt_file_path: the path of the srt file
        """
        self.f_script = open(script_file_path, "r+")  # script file
        self.regex_script = regex_script  # the regex structure of the script file
        self.index_to_speaker_script = {}  # take an index of line and say who talked in the line
        self.word_to_number_appearances_script = {}  # dict that take word and count how much time the word appeared
        self.line_index_to_line_time_srt = {}  # take line index of srt file and give line time
        self.word_to_number_appearances_srt = {}  # dict that take word and count how much time the word appeared
        self.line_to_appearances_srt = {}  # take a line and give the indexes that the line appeared
        self.array_of_script_lines = []
        self.array_of_srt_lines = []
        self.initial_time = []  # array that contains the initial time of every line in srt
        self.regex_srt = regex_srt  # the regex structure of srt file
        self.f_srt = open(srt_file_path, "r+")  # the srt file
        self.dict_without_punctuation_script = {}  # line without punctuation to punctuated line for script
        self.dict_without_punctuation_srt = {}  # line without punctuation to punctuated line for srt

    def find_matches_script(self):
        """
        Extract data from the script file
        """
        test_script = self.f_script.read()
        if 'Advertisements' in test_script[:int(len(test_script)/16)]:
            test_script = test_script[0:re.search(r'Advertisements', test_script).end()]
        # match of script include - speaker, what the speaker said
        matches_script = re.finditer(self.regex_script, test_script, re.MULTILINE)
        i = 0
        for matchNum, match in tqdm(enumerate(matches_script, start=1)):
            # run on all the matches we found
            if "Scene" not in match.group(1):  # scene is not line ...
                self.index_to_speaker_script[i] = match.group(1)  # match.group(1) is the speaker name
                line = str(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                                  match.group(2).replace("\xe2\x80\x99", "'")).
                           replace('\r', '')).strip('(').replace('\n', ' ').rstrip().lstrip()  # unnecessary characters
                line_without_punc = line.translate(None, string.punctuation)  # remove punctuation
                self.dict_without_punctuation_script[line_without_punc] = line
                line = line_without_punc
                self.array_of_script_lines.append(line)
                for word in line.split(" "):
                    if word in self.word_to_number_appearances_script.keys():
                        self.word_to_number_appearances_script[word] += 1
                    else:
                        self.word_to_number_appearances_script[word] = 1
                i += 1

    def find_matches_srt(self):
        """
        Extract data from the srt file
        """
        test_srt = self.f_srt.read()
        matches_srt = re.finditer(self.regex_srt, test_srt, re.MULTILINE | re.DOTALL)
        # match of srt include - time, line
        i = 0
        for matchNum, match in tqdm(enumerate(matches_srt, start=1)):
            # for match we found
            if "Scene" not in match.group(1):  # scene is not line
                line = str(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                                  match.group(2).replace("\xe2\x80\x99", "'")).
                           replace('\r', '')).strip('(').rstrip().lstrip()  # remove unnecessary characters
                a = None
                if line[0] == "-":  # if there is more than one speaker
                    a = line.split("\n")  # split it into lines of speaker
                if not a:  # if there is only one speaker
                    self.line_index_to_line_time_srt[i] = match.group(1)
                    self.initial_time.append(match.group(1).split(' --> ')[0])
                    line = line.replace('\n', ' ')
                    line_without_punc = line.translate(None, string.punctuation)
                    self.dict_without_punctuation_srt[line_without_punc] = line
                    line = line_without_punc
                    if line not in self.line_to_appearances_srt.keys():
                        self.line_to_appearances_srt[line] = (i,)
                    else:
                        self.line_to_appearances_srt[line] = self.line_to_appearances_srt[line] + (i,)
                    self.array_of_srt_lines.append(line)
                    for word in line.split(" "):
                        if word in self.word_to_number_appearances_srt.keys():
                            self.word_to_number_appearances_srt[word] += 1
                        else:
                            self.word_to_number_appearances_srt[word] = 1
                if a:  # if there is more than one speaker
                    for line_enter in a:  # for every speaker line
                        line_with_all = line_enter
                        self.line_index_to_line_time_srt[i] = match.group(1)
                        self.initial_time.append(match.group(1).split(' --> ')[0])
                        line_enter = str(re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '',
                                                line_enter.replace("\xe2\x80\x99", "'")).replace('\r', '')).strip(
                            '(').rstrip().lstrip()  # remove unnecessary characters
                        line_enter = line_enter.replace('\n', ' ')
                        line_enter_without_punc = line_enter.translate(None, string.punctuation)
                        self.dict_without_punctuation_srt[line_enter_without_punc] = line_with_all
                        line_enter = line_enter_without_punc
                        if line_enter not in self.line_to_appearances_srt.keys():
                            self.line_to_appearances_srt[line_enter] = (i,)
                        else:
                            self.line_to_appearances_srt[line_enter] = self.line_to_appearances_srt[line_enter] + (i,)
                        self.array_of_srt_lines.append(line_enter)
                        for word in line_enter.split(" "):
                            if word in self.word_to_number_appearances_srt.keys():
                                self.word_to_number_appearances_srt[word] += 1
                            else:
                                self.word_to_number_appearances_srt[word] = 1
                        i += 1
            i += 1
