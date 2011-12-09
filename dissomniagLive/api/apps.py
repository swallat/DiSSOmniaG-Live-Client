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
        try:
            app = dispatcher.addApp(appName, serverUser, serverIpOrHost)
        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error(str(e))
    return True

def appOperate(appXml):
    xml = ElementTree.XML(appXml)
    appName = str(xml.find("name").text)
    serverUser = str(xml.find("serverUser").text)
    serverIpOrHost = str(xml.find("serverIpOrHost").text)
    action = int(xml.find("action").text)
    
    if appName == None or serverUser == None or serverIpOrHost == None or action == None:
        return False
    
    scriptName = xml.find("scriptName")
    
    if scriptName != None:
        scriptName = str(scriptName.text)
    else:
        scriptName = None
        
    commitOrTag = xml.find("commitOrTag")
    if commitOrTag != None:
        commitOrTag = str(commitOrTag.text)
    else:
        commitOrTag = None
    try:
        returnMe = None
        dispatcher = dissomniagLive.dispatcher.Dispatcher()
        if action == dissomniagLive.app.AppActions.START:
            returnMe = dispatcher.startApp(appName, serverUser, serverIpOrHost, scriptName)
        elif action == dissomniagLive.app.AppActions.STOP:
            returnMe = dispatcher.stopApp(appName, serverUser, serverIpOrHost)
        elif action == dissomniagLive.app.AppActions.COMPILE:
            returnMe = dispatcher.compileApp(appName, serverUser, serverIpOrHost)
        elif action == dissomniagLive.app.AppActions.RESET:
            returnMe = dispatcher.resetApp(appName, serverUser, serverIpOrHost)
        elif action == dissomniagLive.app.AppActions.INTERRUPT:
            returnMe = dispatcher.interruptApp(appName, serverUser, serverIpOrHost)
        elif action == dissomniagLive.app.AppActions.REFRESH_GIT:
            returnMe = dispatcher.refreshGitApp(appName, serverUser, serverIpOrHost, commitOrTag)
        elif action == dissomniagLive.app.AppActions.REFRESH_AND_RESET:
            returnMe = dispatcher.refreshAndResetApp(appName, serverUser, serverIpOrHost, commitOrTag)
        elif action == dissomniagLive.app.AppActions.CLONE:
            returnMe = dispatcher.cloneApp(appName, serverUser, serverIpOrHost)
        elif action == dissomniagLive.app.AppActions.DELETE:
            returnMe = dispatcher.deleteApp(appName, serverUser, serverIpOrHost)
        elif action == dissomniagLive.app.AppActions.CLEAN:
            returnMe = dispatcher.cleanApp(appName, serverUser, serverIpOrHost)
        else:
            returnMe = False
        
        log.info("appOperate returns: %s" % str(returnMe))
        return returnMe
    except Exception as e:
        import traceback
        traceback.print_exc()
        log.error(str(e))
        return False
        
def getAppInfo(appName):
    if isinstance(appName, bytes):
        appName = str(appName.decode())
    else:
        appName = str(appName)
        
    dispatcher = dissomniagLive.dispatcher.Dispatcher()
    try:
        print(dispatcher.getInfo(appName))
        return dispatcher.getInfo(appName)
    except Exception as e:
        import traceback
        traceback.print_exc()
        log.error(str(e))
        return None
    