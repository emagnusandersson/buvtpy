

import re
import os
import enum
from lib import *
from libFs import *
import settings
import globvar



class KeyST:
  def __init__(self, size, tCalc):
    self.size=size
    self.tCalc=tCalc
    self.ind=0 # Used to figure out how index changes order after sorting
  def __eq__(self, other):
    #boString = isinstance(other, str)
    if(isinstance(other, KeyST)):
      #return ((self.size, self.tRound) == (other.size, other.tRound))
      return ((self.size, self.tCalc) == (other.size, other.tCalc))
    return str(self) == other
  def __lt__(self, other):
    #return ((self.size, self.tRound) < (other.size, other.tRound))
    return ((self.size, self.tCalc) < (other.size, other.tCalc))
  def __gt__(self, other):
    #return ((self.size, self.tRound) > (other.size, other.tRound))
    return ((self.size, self.tCalc) > (other.size, other.tCalc))
  def __str__(self):
    #return str(self.size)+'_'+str(self.tRound)
    return '%012d_%012d' %(self.size, self.tCalc)
  def __hash__(self):
    #return '%012d_%012d' %(self.size, self.tCalc)
    return hash(str(self.size)+'_'+str(self.tCalc))




class Rule:
  def __init__(self, strPat, boInc, charType, boIncSub=False, boReg=False, intLevel=0, iCandidateStart=0): #, boRootInFilterF
    self.strPat=strPat; self.boInc=boInc; self.charType=charType; self.boIncSub=boIncSub; self.boReg=boReg; self.intLevel=intLevel; self.iCandidateStart=iCandidateStart  # self.boRootInFilterF=boRootInFilterF;
    if(boReg): self.regPat=re.compile(strPat)
  def test(self, shortname, flName, intLevelOfStr):
      # "Bail" if the pattern is at a level where it is not supposed to be used. 
    if(not self.boIncSub and intLevelOfStr>self.intLevel): return False  

      # Empty pattern matches everything
    if(len(self.strPat)==0): return True

      # Detemine strName
    #if(self.boRootInFilterF): strName=flName[self.iCandidateStart:]
    if(self.iCandidateStart is not None): strName=flName[self.iCandidateStart:]
    else: strName=shortname

      # Test pattern
    if(self.boReg):
      res=self.regPat.match(strName)
      boMatch=bool(res)
    else:
      boMatch=self.strPat==strName
    return boMatch


#######################################################################################
# parseFilter
#######################################################################################
def parseFilter(strData, intLevel, iCandidateStart):
  
  arrRulef=[]
  arrRuleF=[]

  patLine=re.compile(r'^.*$', re.M)
  for i, obj in enumerate(patLine.finditer(strData)):
    strRow=obj.group(0)
    strRow=strRow.strip()
    if(strRow):
      if(strRow.startswith('#')): continue
      iSpace=strRow.find(' ')
      if(iSpace==-1): strCtrl=strRow; strPat=""
      else: strCtrl=strRow[0:iSpace]; strPat=strRow[iSpace:].strip()
      #strCtrl=strCtrl.ljust(5, '_')
      boInc=strCtrl[0]=='+'
      charType=strCtrl[1] if len(strCtrl) > 1 else 'f'
      strCtrl=strCtrl.lower()
      boIncSub=strCtrl[2]=='s' if len(strCtrl) > 2 else False
      boRootInFilterF=strCtrl[3]=='r' if len(strCtrl) > 3 else False
      iCandidateStartTmp=iCandidateStart if(boRootInFilterF) else None
      boReg=strCtrl[4]=='r' if len(strCtrl) > 4 else False
      #rule = Rule(strPat, boInc, charType, boIncSub, boRootInFilterF, boReg, intLevel, iCandidateStart)
      rule = Rule(strPat, boInc, charType, boIncSub, boReg, intLevel, iCandidateStartTmp)
      if(charType=='f'): arrRulef.append(rule)
      elif(charType=='F'): arrRuleF.append(rule)
      elif(charType=='B'): arrRulef.append(rule); arrRuleF.append(rule)
      else: return {"strTrace":myErrorStack("charType!='fFB'")}, None, None
  
  return None, arrRulef, arrRuleF


#rule = Rule('.buvt-filter', False, 'f', False, False, 0, None); arrRulef.append(rule)
#rule = Rule('.buvt-filter', False, 'f'); arrRulef.append(rule)


#######################################################################################
# TreeParser
#######################################################################################
class TreeParser:
  def __init__(self, charTRes=settings.charTRes):
    self.charTRes=charTRes
    pass #self.boUseFilter=False
  def getBranch(self, objDir, intLevel):
    fsDir=objDir["fsDir"]
    flDir=objDir["flDir"]
    nNewf=0; nNewF=0

      # Add potetial filter rules
    if(self.boUseFilter):
      boFoundFilterFile=True
      leafFilterLoc=self.leafFilterFirst if(intLevel==0) else settings.leafFilter
      try: fi=open(fsDir+charF+leafFilterLoc,'r')
      except FileNotFoundError: boFoundFilterFile=False
      if(boFoundFilterFile):
        strDataFilter=fi.read()
        fi.close()
        #iCandidateStart=len(longnameFold)+1
        if(flDir): iCandidateStart=len(flDir)+1
        else: iCandidateStart=0
        err, arrRulefT, arrRuleFT=parseFilter(strDataFilter, intLevel, iCandidateStart)
        if(err): return err #globvar.myConsole.error(err["strTrace"]);
        nNewf=len(arrRulefT)
        nNewF=len(arrRuleFT)
        self.arrRulef[0:0]=arrRulefT
        self.arrRuleF[0:0]=arrRuleFT
      
    # if(intLevel==0 and not self.boIncludeLeafMeta):
    #   self.arrRulef.insert(0, Rule(settings.leafMeta, False, 'f'));    nNewf+=1
    
    try:
      it=os.scandir(fsDir)
    except FileNotFoundError as e:
      return {"e":e, "strTrace":myErrorStack(e.strerror)}
      #return {"strTrace":myErrorStack(f'Folder not found: "{fsDir}"')}
      #globvar.myConsole.error('Folder not found: "{fsDir}"'); 
      # if('pydevd' in sys.modules): breakpoint()
      # else: input('os.scandir error!?!?!?')
    myListUnSorted=list(it)
    myList=sorted(myListUnSorted, key=lambda x: x.name)
    boSkipLinks=not settings.boIncludeLinks
    for entry in myList:
      boFile=entry.is_file(); boDir=entry.is_dir()
      if(not boFile and not boDir):
        continue
      if(sys.platform=='win32'):
        boLink=entry.name.endswith(('.lnk'))
      else:
        boLink=entry.is_symlink()
        if(boDir and boLink):  boFile=True; boDir=False
      if(boSkipLinks and boLink): continue
      strName=entry.name
      #strName=longnameFold+charF+strName
      if(flDir): flName=flDir+charF+strName
      else: flName=strName
      fsName=fsDir+charF+strName
      #if(flName=='progPython/bin/scannedBook.py'): breakpoint()
      #if(strName=='0Downloads'): breakpoint()
      #if(strName=='ignore'): breakpoint()
      boMatch=False
      boInc=True
      arrRuleT=self.arrRuleF if boDir else self.arrRulef
      for j, rule in enumerate(arrRuleT):
        boMatch=rule.test(strName, flName, intLevel)
        if(boMatch): break
      if(boMatch): boInc=rule.boInc
      if(not boInc): continue

      objStat=os.lstat(fsName)
      ino=objStat.st_ino; mtime_ns64=objStat.st_mtime_ns; #mtime=objStat.st_mtime
      #mtime=math.floor(mtime)
      mtime_ns64Round, tCalc=roundMTime(mtime_ns64, self.charTRes)
      objEntry={"strName":flName, "ino":ino, "mtime_ns64":mtime_ns64, "mtime_ns64Round":mtime_ns64Round} #, "mtime":mtime
      if(not boDir):
        mode=objStat.st_mode;size=objStat.st_size
        #st=str(rowA["size"])+str(rowA["mtime"])
        #st='%012d_%012d' %(size,mtime)
        st=KeyST(size, tCalc)
        strType='l' if(boLink) else 'f'
        objEntry.update({"size":size, "st":st, "strType":strType}) 
        self.arrTreef.append(objEntry)
      else:
        self.arrTreeF.append(objEntry)
        obj={"fsDir":fsName, "flDir":flName}
        err=self.getBranch(obj, intLevel+1) 
        if(err): return err;
         
    #globvar.myConsole.printNL('%s: %d %d %d %d' %(flDir, len(self.arrRuleF), len(self.arrRulef), len(self.arrTreeF), len(self.arrTreef)))
    del self.arrRulef[:nNewf]
    del self.arrRuleF[:nNewF]
  
  # def calcKey(self, charTRes):
  #   for row in self.arrTreef:
  #     mtime_ns64Round, tCalc=roundMTime(mtime_ns64, charTRes)
  #     row["st"]=KeyST(row["size"], tCalc)
    

  #def parseTree(self, fsDir, boUseFilter=False, leafFilterFirst=""):
  #def parseTree(self, fsDir, boUseFilter=False, leafFilterFirst="", arrRulefStart=[]):
  #def parseTree(self, fsDir, boUseFilter=False, leafFilterFirst=""): #, boIncludeLeafMeta=False
  def parseTree(self, fsDir, charTRes, leafFilterFirst=None): #, boIncludeLeafMeta=False
    self.boUseFilter=bool(leafFilterFirst)
    self.charTRes=charTRes
    #self.boUseFilter=boUseFilter
    #print(leafFilterFirst)
    self.leafFilterFirst=leafFilterFirst if(leafFilterFirst!="") else settings.leafFilter
    #self.boIncludeLeafMeta=boIncludeLeafMeta
    self.arrTreef=[]; self.arrTreeF=[]
    self.arrRulef=[]; self.arrRuleF=[]
    err=self.getBranch({"fsDir":fsDir, "flDir":""}, 0)  #strName, ino, mtime, mtime_ns64, size, keyST

    return err, self.arrTreef, self.arrTreeF

#arrSourcef, arrSourceF =parseTree(myRealPathf(args.fiDir), True)  # Parse tree

def removeLeafMetaFromArrTreef(arrTreef, leafMeta):
  for i, entry in enumerate(arrTreef):
    if(entry["strName"]==leafMeta): arrTreef.pop(i); break

  
#######################################################################################
# parseRenameInput
#######################################################################################
#def parseRenameInput(fiInpFile):
def parseRenameInput(path, strStrart='MatchingData'):
  if(strStrart==None):strStrart='MatchingData'
  class EnumMode(enum.Enum): LookForStart = 1; LookForOld = 2; LookForNew = 3
  
  boInputFound=True
  try: fi=open(path,'r')
  except FileNotFoundError as e:
    return {"e":e, "strTrace":myErrorStack(e.strerror)}, []
  strData=fi.read(); fi.close()

  arrRename=[]
  arrInp=strData.split('\n')
  #i=0; nRows=len(arrInp)
  mode=EnumMode.LookForStart
  strOld=""; strNew=""; strMeta=""
  #while(1):
  for i, strRow in enumerate(arrInp):
    #if(i==nRows): break
    #strRow=arrInp[i]
    #i+=1
    strRow=strRow.strip()
    if(len(strRow)==0): continue
    if(strRow.startswith('#')): continue
    arrPart=strRow.split()

    if(mode==EnumMode.LookForStart):
      if(arrPart[0]==strStrart): mode=EnumMode.LookForOld; strMeta=strRow; continue
    elif(mode==EnumMode.LookForOld):
      strOld=strRow;  mode=EnumMode.LookForNew; continue
    elif(mode==EnumMode.LookForNew):
      strNew=strRow;  mode=EnumMode.LookForStart

    arrRename.append({"strOld":strOld, "strNew":strNew, "strMeta":strMeta})
  
  return None, arrRename



def getRsyncList(fsDir):
  #leafOutputRsync='outputRsync.txt'
  #subprocess.run(['DIR=`mktemp -d /tmp/rsync.XXXXXX`'])
  #dirpath = tempfile.mkdtemp()
  
  #temp_dir = tempfile.TemporaryDirectory()
  #subprocess.run(['rsync', '-nr', "--out-format='%n'", fsDir, dirpath, '>', leafOutputRsync])
  #strData=subprocess.check_output(['rsync', '-nr', "--out-format='%n'", fsDir+charF, temp_dir.name])
  strData=subprocess.check_output(['rsync', '-nrF', "--out-format='%n'", fsDir+charF, "/dev/false"])

  strData=strData.decode("utf-8")
  #subprocess.run(['rmdir', '$DIR'])
  #subprocess.run(['rmdir', dirpath])
  #temp_dir.cleanup()

  arrInp=strData.split('\n')
  arrInp=arrInp[1:]
  arrf=[]; arrF=[]; arrOther=[]

  for flName in arrInp:
    if(len(flName)==0): continue
    flName=flName.strip("'")
    fsName=fsDir+charF+flName
    boIsFile=os.path.isfile(fsName)
    boIsDir=os.path.isdir(fsName)
    if(boIsFile or boIsDir):
      tmp=os.lstat(fsName)
      ino=tmp.st_ino; mtime_ns64=tmp.st_mtime_ns; #mtime=tmp.st_mtime
      mtime_ns64Round, tCalc=roundMTime(mtime_ns64, blah.charTRes)
    objEntry={"ino":ino, "mtime_ns64":mtime_ns64, "mtime_ns64Round":mtime_ns64Round} #, "mtime":mtime
    if(boIsFile):
      mode=tmp.st_mode; size=tmp.st_size
      st=KeyST(size, tCalc)
      objEntry.update({"strName":flName, "size":size, "st":st})
      arrf.append(objEntry)
    elif(boIsDir):
      objEntry.update({"strName":flName[:-1]})
      arrF.append(objEntry)
    else: 
      arrOther.append(flName)
  return arrf, arrF, arrOther

# def parseMeta(fsMeta, charTRes):
#   err, arrDB=parseSSV(fsMeta)
#   if(err):  return err, None
#     # Rename inode to ino
#   if(len(arrDB) and 'inode' in arrDB[0]):
#     for obj in arrDB:
#       obj["ino"]=obj.pop("inode")
    
#   formatColumnData(arrDB, {"size":"number", "ino":"number", "mtime":"number"})
#   return None, arrDB

def parseMeta(fsMeta, charTRes):
  err, arrDB=parseSSV(fsMeta)
  if(err):  return err, None
  nData=len(arrDB)
  if(nData==0):  return None, arrDB
    # Cast some properties 
  formatColumnData(arrDB, {"size":"number", "inode":"number", "ino":"number"})

  strOSTypeMeta=checkPathFormat(arrDB)
  if(strOSTypeMeta=='linux' and sys.platform=='win32'):
    for obj in arrDB: obj["strName"]=obj["strName"].replace('/','\\')
  elif(strOSTypeMeta=='win32' and sys.platform=='linux'):
    globvar.myConsole.error("strOSTypeMeta=='win32' and sys.platform=='linux'")

    # Rename inode to ino
  if('inode' in arrDB[0]):
    for obj in arrDB: obj["ino"]=obj.pop("inode")
  
    # If any mtime is longer than 10 char, then assume ns
  boNs=False
  for obj in arrDB:
    if(len(obj["mtime"])>10): boNs=True; break
  if(boNs):
    for obj in arrDB:
      obj["mtime_ns64"]=int(obj["mtime"])
      #obj["mtime"]=int(obj["mtime"][:-9])
  else:
    for obj in arrDB:
      mtimeS=int(obj["mtime"])
      #obj["mtime"]=mtimeS
      obj["mtime_ns64"]=mtimeS*1e9

    # Create st
  for obj in arrDB:
    mtime_ns64Round, tCalc=roundMTime(obj["mtime_ns64"], charTRes)
    obj["mtime_ns64Round"]=mtime_ns64Round
    obj["st"]=KeyST(obj["size"], tCalc)
  return None, arrDB




#######################################################################################
# parseHashFile
#######################################################################################
def parseHashFile(fsHashFile):
  try: fi=open(fsHashFile,'r')
  except FileNotFoundError as e:
    return {"e":e, "strTrace":myErrorStack(e.strerror)}, None    #"strErr":e.strerror, 
  strData=fi.read();   fi.close()
  arrOut=[];   arrInp=strData.split('\n')
  for strRow in arrInp:
    strRow=strRow.strip()
    if(len(strRow)==0): continue
    if(strRow.startswith('#')): continue
    arrPart=strRow.split(None, 3)
    arrOut.append({"strHash":arrPart[0], "mtime_ns64":int(arrPart[1])*1e9, "size":int(arrPart[2]), "strName":arrPart[3]})
  
  return None, arrOut
