import subprocess
modules = ['dropbox', 'moviepy', 'linecache', 'shutil', 'difflib', 'scipy', 'tqdm', 'numpy', 'operator', 'math',
           'string', 're', 'matplotlib', 'sys']
for pkg in modules:
    try:
        globals()[pkg] = __import__(pkg)
    except ImportError:
        subprocess.check_call(["python", '-m', 'pip', 'install', pkg])

url_srt = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x01 - Pilot.HDTV.XOR.en.srt"
url_script = "/srt-scrip/scripts/series-1-episode-1-pilot-episode.txt"
access_token = "ZjLsrohKF6AAAAAAAAABI5URO-nBYnGcRP1nuYMasHM7t3EiB7Su2psz9Ef1wuqG"
BIG_NUM = 10