import subprocess
modules = ['dropbox', 'moviepy', 'linecache', 'shutil', 'difflib', 'scipy', 'tqdm', 'numpy', 'operator', 'math',
           'string', 're', 'matplotlib', 'os', 'sys']
for pkg in modules:
    try:
        if pkg != 'SpeechRecognition':
            globals()[pkg] = __import__(pkg)
        else:
            globals()[pkg] = __import__('speech_recognition')
    except ImportError:
        subprocess.check_call(["python", '-m', 'pip', 'install', pkg])

url_srt = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x01 - Pilot.HDTV.XOR.en.srt"
url_script = "/srt-scrip/scripts/series-1-episode-1-pilot-episode.txt"
access_token = "ZjLsrohKF6AAAAAAAAABKGNmrf0fqguEIXoIC-IJ3j5mzbELVUvkTepyCG_7OBtV"
BIG_NUM = 10
outputfile = 'outputfilenew.txt'

def get_sec(time_str):
    """Get Seconds from time."""
    h, m, sms = time_str.split(':')
    s, ms = sms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + 0.001 * int(ms)
