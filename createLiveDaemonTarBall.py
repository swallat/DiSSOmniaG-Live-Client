#!/usr/bin/env python3
'''
Created on 18.10.2011

@author: Sebastian Wallat
'''
import os, shutil
import tarfile

actualPath = os.path.abspath("/home/sw/git/BachelorCoding/DiSSOmniaG_liveClient/")
baseDirName = "TarTemp"
baseBuildDir = os.path.abspath(os.path.join(actualPath, baseDirName))
tarFileName = "dissomniagLive.tar.gz"

dissomniagLiveFolder = os.path.join(baseBuildDir, "usr/share/dissomniag-live/")
initDFolder = os.path.join(baseBuildDir, "etc/init.d/")

ignore_set = set(["createLiveDaemonTarBall.py", baseDirName, tarFileName, ".pydevproject", ".project", "log", "key.pem", "cert.pem"])  

def createBuildDir():
    os.makedirs(dissomniagLiveFolder, 0o755)
    os.makedirs(initDFolder, 0o755)

def copyFilesToBuildDir():
    #1. Copy Daemon Files
    
    listing = os.listdir(actualPath)
    for obj in listing:
        if obj in ignore_set:
            continue
        else:
            if os.path.isdir(obj):
                shutil.copytree(obj, os.path.join(dissomniagLiveFolder, obj), symlinks = False, ignore=shutil.ignore_patterns('*.pyc', 'tmp*', '*.log'))
            else:
                shutil.copy2(obj, dissomniagLiveFolder)
            
            
    #2. Copy init.d File
    shutil.copy2(os.path.abspath("../DiSSOmniaG/static/live/init.d/dissomniag_live"), initDFolder)
            
    

def createTarFile():
    os.chdir(baseDirName)
    with tarfile.open(tarFileName, "w:gz") as tar:
        listing = os.listdir("./")
        for infile in listing:
            if infile not in ignore_set:
                tar.add(infile)
    shutil.copy2(tarFileName, "../")
    os.chdir("../")

def cleanUp():
    try:
        shutil.rmtree(baseBuildDir)
    except Exception:
        print("Clean failed")
        exit(-1)

def deleteOldTarFile():
    try:
        shutil.rmtree(os.path.abspath(tarFileName))
    except Exception:
        pass

if __name__ == '__main__':
    failed = False
    try:
        deleteOldTarFile()
        createBuildDir()
        copyFilesToBuildDir()
        createTarFile()
    except Exception:
        failed = True
    finally:
        cleanUp()
        if failed:
            exit(-1)
        else:
            exit(0)