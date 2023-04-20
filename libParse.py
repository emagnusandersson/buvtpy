

import re
import os
import enum
from lib import *
from libFs import *
import settings
import globvar

class KeyST:
  def __init__(self, size, t, charTimeAccuracy):
    self.t=t
    self.size=size
    if(charTimeAccuracy=='s'):   div=1000000000
    elif(charTimeAccuracy=='m'): div=1000000
    elif(charTimeAccuracy=='u'): div=1000
    elif(charTimeAccuracy=='n'): div=1
    elif(charTimeAccuracy=='2'): div=2000000000
    #self.tRound=(t//div)*div
    self.tCalc=(t//div)   #*div
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
  def __init__(self, strPat, boInc, charType, boIncSub, boRootInFilterF, boReg, intLevel, iStartOfRuleFileRootInFlName):
    self.strPat=strPat; self.boInc=boInc; self.charType=charType; self.boIncSub=boIncSub; self.boRootInFilterF=boRootInFilterF; self.boReg=boReg; self.intLevel=intLevel; self.iStartOfRuleFileRootInFlName=iStartOfRuleFileRootInFlName
    if(boReg): self.regPat=re.compile(strPat)
  def test(self, shortname, flName, intLevelOfStr):
      # "Bail" if the pattern is at a level where it is not supposed to be used. 
    if(not self.boIncSub and intLevelOfStr>self.intLevel): return False  

      # Empty pattern matches everything
    if(len(self.strPat)==0): return True

      # Detemine strName
    if(self.boRootInFilterF): strName=flName[self.iStartOfRuleFileRootInFlName:]
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
def parseFilter(strData, intLevel, iStartOfRuleFileRootInFlName):
  
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
      boInc=strCtrl[0]=='+'
      charType=strCtrl[1] if len(strCtrl) > 1 else 'f'
      boIncSub=strCtrl[2]=='S' if len(strCtrl) > 2 else False
      boRootInFilterF=strCtrl[3]=='R' if len(strCtrl) > 3 else False
      boReg=strCtrl[4]=='R' if len(strCtrl) > 4 else False
      rule = Rule(strPat, boInc, charType, boIncSub, boRootInFilterF, boReg, intLevel, iStartOfRuleFileRootInFlName)
      if(charType=='f'): arrRulef.append(rule)
      elif(charType=='F'): arrRuleF.append(rule)
      elif(charType=='B'): arrRulef.append(rule); arrRuleF.append(rule)
      else: return {"strTrace":myErrorStack("charType!='fFB'")}, None, None
  
  return None, arrRulef, arrRuleF




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
        #iStartOfRuleFileRootInFlName=len(longnameFold)+1
        if(flDir): iStartOfRuleFileRootInFlName=len(flDir)+1
        else: iStartOfRuleFileRootInFlName=0
        err, arrRulefT, arrRuleFT=parseFilter(strDataFilter, intLevel, iStartOfRuleFileRootInFlName)
        if(err): globvar.myConsole.error(err["strTrace"]); return
        nNewf=len(arrRulefT)
        nNewF=len(arrRuleFT)
        self.arrRulef[0:0]=arrRulefT
        self.arrRuleF[0:0]=arrRuleFT
      
    it=os.scandir(fsDir)
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
      ino=objStat.st_ino; mtime=objStat.st_mtime; mtime_ns=objStat.st_mtime_ns
      mtime=math.floor(mtime)
      if(not boDir):
        mode=objStat.st_mode;size=objStat.st_size
        #st=str(rowA["size"])+str(rowA["mtime"])
        #st='%012d_%012d' %(size,mtime)
        st=KeyST(size, mtime_ns, self.charTRes)
        strType='l' if(boLink) else 'f'
        myFile={"strName":flName, "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns, "size":size, "st":st, "strType":strType} #, "boLink":boLink
        self.arrTreef.append(myFile)
      else:
        myFold={"strName":flName, "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns}
        #self.arrTreef.append(myFold)
        self.arrTreeF.append(myFold)
        obj={"fsDir":fsName, "flDir":flName}
        self.getBranch(obj, intLevel+1) 
         
    #globvar.myConsole.printNL('%s: %d %d %d %d' %(flDir, len(self.arrRuleF), len(self.arrRulef), len(self.arrTreeF), len(self.arrTreef)))
    del self.arrRulef[:nNewf]
    del self.arrRuleF[:nNewF]
  
  # def calcKey(self, charTRes):
  #   for row in self.arrTreef:
  #     row["st"]=KeyST(row["size"], row["mtime_ns"], charTRes)
    

  def parseTree(self, fsDir, boUseFilter=False, leafFilterFirst=""):
    self.boUseFilter=boUseFilter
    #print(leafFilterFirst)
    self.leafFilterFirst=leafFilterFirst if(leafFilterFirst!="") else settings.leafFilter
    self.arrTreef=[]; self.arrTreeF=[]
    self.arrRulef=[]; self.arrRuleF=[]
    self.getBranch({"fsDir":fsDir, "flDir":""}, 0)  #strName, ino, mtime, mtime_ns, size, keyST
    return self.arrTreef, self.arrTreeF

#arrSourcef, arrSourceF =parseTree(myRealPathf(args.fiDir), True)  # Parse tree



  
#######################################################################################
# parseRenameInput
#######################################################################################
#def parseRenameInput(fiInpFile):
def parseRenameInput(fiInpFile, strStrart='MatchingData'):
  if(strStrart==None):strStrart='MatchingData'
  class EnumMode(enum.Enum): LookForStart = 1; LookForOld = 2; LookForNew = 3
  
  boInputFound=True
  try: fi=open(fiInpFile,'r')
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
    if(boIsFile):
      tmp=os.lstat(fsName)
      ino=tmp.st_ino; mode=tmp.st_mode; mtime=tmp.st_mtime; mtime_ns=tmp.st_mtime_ns; size=tmp.st_size
      st=KeyST(size, mtime_ns, settings.charTRes)
      myFile={"strName":flName, "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns, "size":size, "st":st}
      arrf.append(myFile)
    elif(boIsDir):
      tmp=os.lstat(fsName)
      ino=tmp.st_ino; mtime=tmp.st_mtime; mtime_ns=tmp.st_mtime_ns
      myFold={"strName":flName[:-1], "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns}
      arrF.append(myFold)
    else: 
      arrOther.append(flName)
  return arrf, arrF, arrOther

def parseMeta(fsMeta):
  err, arrDB=parseSSV(fsMeta)
  if(err):  return err, None
  if(len(arrDB) and 'inode' in arrDB[0]):
    for obj in arrDB:
      obj["ino"]=obj.pop("inode")
    
  formatColumnData(arrDB, {"size":"number", "ino":"number", "mtime":"number"})
  return None, arrDB

def parseMeta(fsMeta):
  err, arrDB=parseSSV(fsMeta)
  if(err):  return err, None
  nData=len(arrDB)
  if(nData==0):  return None, arrDB
    # Cast some properties 
  formatColumnData(arrDB, {"size":"number", "ino":"number"})

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
      obj["mtime_ns"]=int(obj["mtime"])
      obj["mtime"]=int(obj["mtime"][:-9])
  else:
    for obj in arrDB:
      obj["mtime"]=int(obj["mtime"])
      obj["mtime_ns"]=int(obj["mtime"])*1000000000

    # Create st
  for obj in arrDB:
    st=KeyST(obj["size"], obj["mtime_ns"], settings.charTRes)
    obj["st"]=st
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
    arrOut.append({"strHash":arrPart[0], "mtime":int(arrPart[1]), "size":int(arrPart[2]), "strName":arrPart[3]})
  
  return None, arrOut
