import subprocess
modules = ['dropbox', 'moviepy', 'linecache', 'shutil', 'difflib', 'scipy', 'tqdm', 'numpy', 'operator', 'math',
           'string', 're', 'matplotlib', 'os', 'sys', 'sklearn', 'python_speech_features']
for pkg in modules:
    try:
        if pkg != 'SpeechRecognition':
            globals()[pkg] = __import__(pkg)
        else:
            globals()[pkg] = __import__('speech_recognition')
    except ImportError:
        subprocess.check_call(["python", '-m', 'pip', 'install', pkg, '-q'])

#url_srt = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x01 - Pilot.720p HDTV.CTU.en.srt"
#url_srt = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x02 - The Big Bran Hypothesis.720p HDTV.CTU.en.srt"
url_srt = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x03 - The Fuzzy Boots Corollary.720p HDTV.YesTV.en.srt"
#url_srt = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x04 - The Luminous Fish Effect.HDTV.XOR.en.srt"
#url_srt_root = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/"
#url_srt = url_srt_root + "The Big Bang Theory - 1x05 - The Hamburger Postulate.HDTV.XOR.en.srt"
#url_script = "/srt-scrip/scripts/series-1-episode-1-pilot-episode.txt"
#url_script = "/srt-scrip/scripts/series-1-episode-2-the-big-bran-hypothesis.txt"
url_script = "/srt-scrip/scripts/series-1-episode-3-the-fuzzy-boots-corollary.txt"
#url_script = "/srt-scrip/scripts/series-1-episode-4-the-luminous-fish-effect.txt"
#url_script_root = "/srt-scrip/scripts/"
#url_script = url_script_root + "series-1-episode-5-the-hamburger-postulate.txt"
access_token = "ZjLsrohKF6AAAAAAAAABK_Wj6EYJneviGvdKkCdtmJ-x2l3wTT_zCcp6EDNuoGd" + "B"
BIG_NUM = 10
outputfile = 'outputfilenew.txt'

def get_sec(time_str):
    """Get Seconds from time."""
    h, m, sms = time_str.split(':')
    s, ms = sms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + 0.001 * int(ms)
