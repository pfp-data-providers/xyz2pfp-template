import glob
import os

from csae_pyutils import upload_files_to_owncloud

user = os.environ["OWNCLOUD_USER"]
pw = os.environ["OWNCLOUD_PW"]
oc_folder = os.environ.get("OWNCLOUD_FOLDER")

if oc_folder:
    files = glob.glob("./datasets/*.nt")
    upload = upload_files_to_owncloud(files, user, pw, folder="pfp-data")
    print(upload)
else:
    print("no env-variable set for OWNCLOUD_FOLDER")
