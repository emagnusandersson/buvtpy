
import os
import copy
import uuid
#from pathlib import Path
import pathlib
from lib import *
import settings
import globvar
import sys
import subprocess
import shutil


def checkPathFormat(arr):
  boFWDSlash=False
  for row in arr:
    if('/' in row["strName"]): boFWDSlash=True; break
  if(boFWDSlash): return 'linux'
  return 'win32'

    
#
# Higher level fs interfaces
#
def myRealPathf(fiPath):
  if(sys.platform=="win32"): flPath=os.path.expandvars(fiPath)
  else: flPath=fiPath
  fsPath=os.path.expanduser(flPath)
  return fsPath


#######################################################################################
# renameFiles (or folders)
#######################################################################################
def renameFiles(fsDir, arrRename): 
  arrTmpName=[]
  for row in arrRename:    # Rename to temporary names
    hex=uuid.uuid4().hex
    fsTmp=fsDir+charF+row['strNew']+'_'+hex
    arrTmpName.append(fsTmp)
    fsOld=fsDir+charF+row['strOld']
    fsPar=os.path.dirname(fsTmp);  boExist=os.path.exists(fsPar);  boIsDir=os.path.isdir(fsPar)
    if(boExist): 
      if(not boIsDir): return {"strTrace":myErrorStack("boExist and not boIsDir")}
    else: pathlib.Path(fsPar).mkdir(parents=True, exist_ok=True)
    try: os.rename(fsOld, fsTmp)
    except FileNotFoundError as e:
      return {"e":e, "strTrace":myErrorStack(e.strerror)}    

  for i, row in enumerate(arrRename):    # Rename to final names
    fsTmp=arrTmpName[i]
    fsNew=fsDir+charF+row['strNew']
    fsPar=os.path.dirname(fsNew);  boExist=os.path.exists(fsPar);  boIsDir=os.path.isdir(fsPar)
    if(boExist): 
      if(not boIsDir): return {"strTrace":myErrorStack("boExist and not boIsDir")}
    else: pathlib.Path(fsPar).mkdir(parents=True, exist_ok=True)
    try: os.rename(fsTmp, fsNew)
    except FileNotFoundError as e:
      return {"e":e, "strTrace":myErrorStack(e.strerror)}   
  return None

# def escBackSlash(str):
#   return str.replace('\\', '\\\\')
   
def myRmFiles(arrEntry, fsDir):
  if(len(arrEntry)==0): return None
  if(sys.platform=="linux"): strRmCommand='rm'
  elif(sys.platform=="win32"): strRmCommand='del'
  else: return 'unhandled OS'
  arr=[strRmCommand]
  for row in arrEntry:
    fsName=fsDir+charF+row["strName"]
    arr.append(fsName)

  dictExtra={"shell":True} if(sys.platform=="win32") else {}
  strOut=subprocess.run(arr, **dictExtra)
  # if(sys.platform=="linux"): 
  #   strOut=subprocess.run(arr)
  # elif(sys.platform=="win32"): 
  #   strOut=subprocess.run(arr, shell=True)
#os.path.realpath
def myRmFolders(arrEntry, fsDir):
  if(len(arrEntry)==0): return None
  arr=['rmdir']
  for row in arrEntry:
    fsName=fsDir+charF+row["strName"]
    arr.append(fsName)
  dictExtra={"shell":True} if(sys.platform=="win32") else {}
  strOut=subprocess.run(arr, **dictExtra)
  # if(sys.platform=="linux"): 
  #   strOut=subprocess.run(arr)
  # elif(sys.platform=="win32"): 
  #   strOut=subprocess.run(arr, shell=True)
def myMkFolders(arrEntry, fsDir):
  if(len(arrEntry)==0): return None
  # arr=['rmdir', r'C:\\Users\\emagn\\progPython\\buvt-TargetFs\\Target\\progC']
  # arr=['rmdir', """C:\\Users\\emagn\\progPython\\buvt-TargetFs\\Target\\progC"""]
  # strOut=subprocess.run(arr, shell=True)
  arr=['mkdir']
  for row in arrEntry:
    fsName=fsDir+charF+row["strName"]
    if(sys.platform=="win32"): fsName=os.path.realpath(fsName)
    arr.append(fsName)
  dictExtra={"shell":True} if(sys.platform=="win32") else {}
  strOut=subprocess.run(arr, **dictExtra)
  # if(sys.platform=="linux"): 
  #   strOut=subprocess.run(arr)
  # elif(sys.platform=="win32"): 
  #   strOut=subprocess.run(arr, shell=True)
  pass

def myCopyEntries(arrEntry, fsDirSource, fsDirTarget):
  if(sys.platform=="linux"): strCpCommand='cp'; strArg='-pP'
  elif(sys.platform=="win32"): strCpCommand='copy'; strArg='\\L'
  for row in arrEntry:
    fsSouceName=fsDirSource+charF+row["strName"]
    fsTargetName=fsDirTarget+charF+row["strName"]
    if(sys.platform=="win32"): fsSouceName=os.path.realpath(fsSouceName)
    if(sys.platform=="win32"): fsTargetName=os.path.realpath(fsTargetName)

    fsPar=os.path.dirname(fsTargetName);  boExist=os.path.exists(fsPar);  boIsDir=os.path.isdir(fsPar)
    if(boExist): 
      if(not boIsDir): return {"strTrace":myErrorStack("boExist and not boIsDir")}
    else: pathlib.Path(fsPar).mkdir(parents=True, exist_ok=True)
    #strOut=subprocess.run([strCpCommand, strArg, fsSouceName, fsTargetName])
    shutil.copy2(fsSouceName, fsTargetName, follow_symlinks=False) #untested



def writeMetaFile(arrDB, fsMeta):
      # If fsMeta exist then rename it
  if(os.path.isfile(fsMeta)):
    fsMetaWithCounter=calcFileNameWithCounter(fsMeta)
    os.rename(fsMeta, fsMetaWithCounter)

    # Write fsMeta
  fo=open(fsMeta,'w')
  fo.write('strType ino strHash mtime size strName\n')  #uuid 
  for row in arrDB:
    #fo.write('%s %10s %32s %10s %10s %s\n' %(row["uuid"], row["ino"], row["strHash"], math.floor(row["mtime"]), row["size"], row["strName"]))
    #fo.write('%10s %32s %10s %10s %s\n' %(row["ino"], row["strHash"], math.floor(row["mtime"]), row["size"], row["strName"]))
    # if('boLink' in row):
    #   strType='l' if row["boLink"] else 'f'
    # if('strType' in  row): 
    strType=row["strType"]
    fo.write('%s %10s %32s %s %10s %s\n' %(strType, row["ino"], row["strHash"], row["mtime_ns64"], row["size"], row["strName"]))
  fo.close()

def writeHashFile(arrDB, fsHash):
      # If fsHash exist then rename it
  if(os.path.isfile(fsHash)):
    fsHashWithCounter=calcFileNameWithCounter(fsHash)
    os.rename(fsHash, fsHashWithCounter)

    # Write fsHash
  fo=open(fsHash,'w')
  #fo.write('strHash mtime size strName\n')
  for row in arrDB:
    fo.write('%32s %10s %10s %s\n' %(row["strHash"], row["mtime_ns64"], row["size"], row["strName"]))
  fo.close()




def selectFrArrDB(arrDB, flPrepend):    # Separate relevant from non-relevant entries in arrDB
  arrDBNonRelevant=[];  arrDBRelevant=[]
  nPrepend=len(flPrepend)
  for row in arrDB:
    rowCopy=copy.copy(row)
    if(row["strName"][:nPrepend]!=flPrepend): arrDBNonRelevant.append(rowCopy)
    else:
      rowCopy["strName"]=rowCopy["strName"][nPrepend:]
      #strNameCrop=rowCopy["strName"][nPrepend:]
      #rowCopy.update({"strName":strNameCrop})
      arrDBRelevant.append(rowCopy)
  return arrDBNonRelevant, arrDBRelevant
# arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)



class MyReporter:
  def __init__(self, StrStem):
    self.StrStem=StrStem
    self.StrStemWScreen=['screen']+StrStem  #settings.StrStemReport
    self.StrStemWOSum=StrStem[1:]  
    self.myInit()
  def myInit(self):
    self.Str={}
    for strStem in self.StrStemWScreen:
      if(strStem in self.Str): self.Str[strStem].clear()
      else: self.Str[strStem]=[]
  def getStr(self):
    arrOut=[]
    for strStem in self.StrStemWScreen:
      StrTmp=self.Str[strStem]
      arrOut.append(StrTmp)
    return arrOut
  def writeToFile(self):
    StrSeeMoreIn=[]
    for strStem in self.StrStemWOSum:
      Str=self.Str[strStem]
      p=settings.arrPath[strStem]
      if(len(Str)): StrSeeMoreIn.append(p.name)
    for strStem in self.StrStem:
      Str=self.Str[strStem]
      p=settings.arrPath[strStem]
      if(len(Str)): strTmp='\n'.join(self.Str[strStem])+'\n';
      else: strTmp=""
      fof=open(p,'w');   fof.write(strTmp);   fof.close()
    
    StrScreen=self.Str['screen']
    if(StrSeeMoreIn): StrScreen.append("More info in these files: "+', '.join(StrSeeMoreIn))
    strTmp='\n'.join(StrScreen);   globvar.myConsole.printNL(strTmp)




