# -*- coding: utf-8 -*-
'''
Created on 02.12.2011

@author: Sebastian Wallat
'''
from xml.etree import ElementTree#
import dissomniagLive
import logging
log = logging.getLogger("dissomniagLive.api.apps.py")

def addApps(appXml):
    xml = ElementTree.XML(appXml)
    
    dispatcher = dissomniagLive.dispatcher.Dispatcher()
    
    apps = xml.findall("app")
    for app in apps:
        appName = str(app.find("name").text)
        serverUser = str(app.find("serverUser").text)
        serverIpOrHost = str(app.find("serverIpOrHost").text)
        app = dispatcher.addApp(appName, serverUser, serverIpOrHost)
        app.clone()
    return True

def appOperate(appXml):
    xml = ElementTree.XML(appXml)
    appName = str(xml.find("name").text)
    serverUser = str(xml.find("serverUser").text)
    serverIpOrHost = str(xml.find("serverIpOrHost").text)
    action = int(xml.find("action"))
    
    if appName == None or serverUser == None or serverIpOrHost == None or action == None:
        return False
    
    scriptName = xml.find("scriptName")
    
    if scriptName != None:
        scriptName = str(scriptName.text)
        
    commitOrTag = xml.find("commitOrTag")
    
    if commitOrTag != None:
        commitOrTag = str(commitOrTag.text)
    
    dispatcher = dissomniagLive.dispatcher.Dispatcher()
    if action == dissomniagLive.app.AppActions.START:
        return dispatcher.startApp(appName, serverUser, serverIpOrHost, scriptName)
    elif action == dissomniagLive.app.AppActions.STOP:
        return dispatcher.stopApp(appName, serverUser, serverIpOrHost)
    elif action == dissomniagLive.app.AppActions.COMPILE:
        return dispatcher.compileApp(appName, serverUser, serverIpOrHost)
    elif action == dissomniagLive.app.AppActions.RESET:
        return dispatcher.resetApp(appName, serverUser, serverIpOrHost)
    elif action == dissomniagLive.app.AppActions.INTERRUPT:
        return dispatcher.interruptApp(appName, serverUser, serverIpOrHost)
    elif action == dissomniagLive.app.AppActions.REFRESH_GIT:
        return dispatcher.refreshGitApp(appName, serverUser, serverIpOrHost, commitOrTag)
    elif action == dissomniagLive.app.AppActions.REFRESH_AND_RESET:
        return dispatcher.refreshAndResetApp(appName, serverUser, serverIpOrHost, commitOrTag)
    elif action == dissomniagLive.app.AppActions.CLONE:
        return dispatcher.cloneApp(appName, serverUser, serverIpOrHost)
    elif action == dissomniagLive.app.AppActions.DELETE:
        return dispatcher.deleteApp(appName, serverUser, serverIpOrHost)
    else:
        return False
        
def appGetInfo(appName):
    
    if isinstance(appName, bytes):
        appName = str(appName.decode())
    else:
        appName = str(appName)
        
    dispatcher = dissomniagLive.dispatcher.Dispatcher()
    return dispatcher.getInfo(appName)
    