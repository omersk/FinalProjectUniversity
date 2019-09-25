import dropbox

class DropBoxDownloader:
    def __init__(self, access_token):
        self.access_token = access_token  # token to get the url
        self.dropboxclient = dropbox.Dropbox(access_token)

    def download_file(self, url, file):
        with open(file, "w") as f:
            metadata, res = self.dropboxclient.files_download(path=url)
            f.write(res.content)