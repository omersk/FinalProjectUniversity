import constants
import dropbox
access_token = constants.access_token
dbx = dropbox.Dropbox(access_token)
with open("Test.txt", "w") as f:
   metadata, res = dbx.files_download(path="/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x01 - Pilot.HDTV.XOR.en.srt")
   f.write(res.content)

#response = dbx.files_list_folder(path = "/srt-scrip/srt-all/The_Big_Bang_Theory - season1.en/The Big Bang Theory - 1x01 - Pilot.HDTV.XOR.en.srt")
#with open("Test1.txt", "w") as f:
#    f.write(str(response))
