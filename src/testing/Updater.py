import requests
import tarfile
import shutil
import glob
import os


def updatePiRowFlo():

    print(" ")
    print(" ")
    print(" ")
    print("========== PiRowFlo Updater ========================================")
    print(" ")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    updatetmpfolder = "/tmp/pirowfloupdate"
    updatefinaldest = BASE_DIR

    response = requests.get("https://api.github.com/repos/inonoob/pirowflo/releases/latest")
    Version = response.json()["name"]
    print(" ")
    print("========== Getting newest {0} of PiRowFlo from Github ==========".format(Version))
    print(" ")

    if os.path.exists(updatetmpfolder):
        shutil.rmtree(updatetmpfolder)
    os.makedirs(updatetmpfolder)
    response = requests.get("https://api.github.com/repos/inonoob/pirowflo/releases/latest")
    resp = response.json()["tarball_url"]
    Version = response.json()["name"]
    response2 = requests.get(resp, stream=True)
    file = open("/tmp/pirowfloupdate/pirowflo-lastversion.tar.gz","wb")
    file.write(response2.content)
    file.close()

    print(" ")
    print("========== Extracting newest release of PiRowFlo in /tmp ===========")
    print(" ")


    my_tar = tarfile.open(updatetmpfolder + "/pirowflo-lastversion.tar.gz")
    my_tar.extractall(updatetmpfolder)  # specify which folder to extract to
    my_tar.close()

    print(" ")
    print("========== Copy newest release of PiRowFlo to target folder ========")
    print(" ")

    pirowfloupdatefolder = glob.glob(updatetmpfolder + "/inonoob-pirowflo-*")
    if os.path.exists(updatefinaldest):
        shutil.rmtree(updatefinaldest)
    shutil.copytree(pirowfloupdatefolder[0], updatefinaldest, symlinks=True)
    shutil.rmtree(updatetmpfolder)

    print(" ")
    print("=============================== DONE! ==============================")
    print(" ")



if __name__ == "__main__":
    updatePiRowFlo()