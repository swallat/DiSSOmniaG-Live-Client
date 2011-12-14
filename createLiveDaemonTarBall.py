#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DiSSOmniaG (Distributed Simulation Service wit OMNeT++ and Git)
# Copyright (C) 2011, 2012 Sebastian Wallat, University Duisburg-Essen
# 
# Based on an idea of:
# Sebastian Wallat <sebastian.wallat@uni-due.de, University Duisburg-Essen
# Hakim Adhari <hakim.adhari@iem.uni-due.de>, University Duisburg-Essen
# Martin Becke <martin.becke@iem.uni-due.de>, University Duisburg-Essen
#
# DiSSOmniaG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DiSSOmniaG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DiSSOmniaG. If not, see <http://www.gnu.org/licenses/>
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