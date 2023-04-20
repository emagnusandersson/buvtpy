
import secrets
import string
from lib import *
import time
#from stat import *
import stat
import uuid
from types import SimpleNamespace
from difflib import SequenceMatcher
import re


ANSI_CURSOR_SAVE="\0337"
ANSI_CURSOR_RESTORE="\0338"
ANSI_CLEAR_BELOW="\033[J"


ANSI_FONT_CLEAR="\033[0m"
ANSI_FONT_BOLD="\033[1m"
def ANSI_CURSOR_UP(n):      return "\033["+str(n)+"A"
def ANSI_CURSOR_DOWN(n):    return "\033["+str(n)+"B"
ANSI_CLEAR_RIGHT="\033[K"
ANSI_CURSORUP="\033[A"
ANSI_CURSORDN="\033[B"

MAKESPACE_N_SAVE="\n\n"+ANSI_CURSOR_UP(2)+ANSI_CURSOR_SAVE
MY_RESET=ANSI_CURSOR_RESTORE+ANSI_CLEAR_BELOW

tStart=time.time()

leafResultCompare="resultCompare.txt"


  # For compareWOId
leafRenameSuggestionsAncestorOnly="renameSuggestionsAncestorOnly.txt"
leafRenameSuggestionsAncestorOnlyCmd="renameSuggestionsAncestorOnlyCmd.txt"
leafDuplicateInitial="renameDuplicateInitial.txt"
leafDuplicateFinal="renameDuplicateFinal.txt"
leafRenameSuggestionsAdditional="renameSuggestionsAdditional.txt"

 # For compareWOId used for renameFinish-calls
leafRenameSuggestionsOTO="renameSuggestionsOneToOne.txt"

# N files could be categorized as renameable after matching size and time (N OTM, N MTO, N MTM) (See list in duplicateInitial.txt)
# After looking at renamed folders (N), a further N files can be categorized as renameable. (See list in renameAdditional.txt)
#   So a final N renameables after matching size and time and folder belonging (N OTM, N MTO, N MTM) (See list in duplicateFinal.txt)


def myRandBase63(n):
  return ''.join(secrets.choice(string.ascii_lowercase +string.ascii_uppercase + string.digits+'_') for _ in range(n))

def myUUID():
  return myRandBase63(22)




FMT_Check_Missing_In_Folder=   "In %s (spanning %d rows (%d-%d)), %d files are missing.\n"

FMT_Check_Missing_Single=    "Row: %d, " +ANSI_FONT_BOLD+"%s"+ANSI_FONT_CLEAR+" %s\n"
FMT_Check_Missing_Range=   "Row: %d-%d (%d), " +ANSI_FONT_BOLD+"%s"+ANSI_FONT_CLEAR+" %s\n"


def parseSSVCustom(fsMeta):
  err, arrDB=parseSSV(fsMeta)
  if(err):  return err, None
  formatColumnData(arrDB, {"size":"number", "ino":"number", "mtime":"number"})
  return None, arrDB


def getSuitableTimeUnit(t): # t in seconds
  tAbs=abs(t); tSign=+1 if(t>=0) else -1
  if(tAbs<=120): return tSign*tAbs, 's'
  tAbs/=60; # t in minutes
  if(tAbs<=120): return tSign*tAbs, 'm'
  tAbs/=60; # t in hours
  if(tAbs<=48): return tSign*tAbs, 'h'
  tAbs/=24; # t in days
  if(tAbs<=2*365): return tSign*tAbs, 'd'
  tAbs/=365; # t in years
  return tSign*tAbs, 'y'


def diffArr(a):
  lenA=len(a)
  if(lenA<2): return []
  d=[0]*(lenA-1)
  for i, row in enumerate(a): d[i]=a[i+1]-a[i]
  return d

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


class MyRealPath:
  def __init__(self):
    self.obj={}
  def realPath(self, fsPath):
    if(fsPath not in self.obj): 
      self.obj[fsPath]=os.path.realpath(fsPath)
    return self.obj[fsPath]
myRealPath=MyRealPath()



def getHighestMissing(fsDir, strPath): # It is assumed that strPath is a file (not a folder) and is missing
  boFirst=True
  while(1):
    strPar=os.path.dirname(strPath)
    if(strPar==''): return boFirst, strPar, strPath
    #fsPar=os.path.realpath(fsDir+'/'+strPar)
    fsPar=myRealPath.realPath(fsDir+'/'+strPar)
    if( os.path.isdir(fsPar)): return boFirst, strPar, strPath 
    strPath=strPar
    boFirst=False


def checkHighestMissingArr(arrDB, fsDir):
  lenDB=len(arrDB); ObjMissing=[None]*lenDB
  for i, row in enumerate(arrDB):
    strName=row["strName"];   fsFile=fsDir+'/'+strName;   boFileFound=os.path.exists(fsFile);
    if(boFileFound): obj={"strPar":None, "strChild":None}
    else:
      boFile, strPar, strChild= getHighestMissing(fsDir, strName)
      obj={"boFile":boFile, "strPar":strPar, "strChild":strChild}
    ObjMissing[i]=obj;
  return ObjMissing

def summarizeMissing(arrDB, fsDir):
  #arrDB=arrDB[:8]
  #tStop=time.time();    print('checkHighestMissingArr starts, elapsed time '+str(round((tStop-tStart)*1000))+'ms')
  lenDB=len(arrDB)
  ObjMissing=checkHighestMissingArr(arrDB, fsDir)
  #ObjMissing[0].update({"strPar":'a'})
  #tStop=time.time();   print('checkHighestMissingArr done, elapsed time '+str(round((tStop-tStart)*1000))+'ms')

#   ObjMissing=[
# {'boFile': False, 'strPar': None, 'strChild': None},
# {'boFile': False, 'strPar': '', 'strChild': 'progC'},
# {'boFile': False, 'strPar': '', 'strChild': 'progC'},
# {'boFile': False, 'strPar': None, 'strChild': None},
# {'boFile': False, 'strPar': '', 'strChild': 'progD'},
# {'boFile': False, 'strPar': '', 'strChild': 'progD'},
# {'boFile': False, 'strPar': None, 'strChild': None},
# {'boFile': True, 'strPar': '', 'strChild': "a.txt"},
# {'boFile': False, 'strPar': 'a', 'strChild': 'progD'},
# {'boFile': False, 'strPar': 'a', 'strChild': 'progD'}]
  ObjMissing.append({"strPar":None, "strChild":None})


    # Create ArrRangePar
  strChildL=None; strParL=None
  iStart=0; iStop=0; iStartPar=0; iStopPar=0; ArrRangePar={}; ArrRange=[]
  #for i in range(0,lenDB+1):
  for i in range(0,len(ObjMissing)):
    objMissing=ObjMissing[i];  strChild=objMissing["strChild"];  strPar=objMissing["strPar"]
    if(strPar!=strParL):
       if(strChildL!=None):strChildL=uuid.uuid4().hex
    if(strChild!=strChildL):
      if(strChildL!=None): iStop=i; ArrRange.append([iStart,iStop])
      if(strChild!=None): iStart=i
    if(strPar!=strParL):
      if(strParL!=None): # parent range ended
        iStopPar=i; 
        if(strParL not in ArrRangePar): ArrRangePar[strParL]={"iStartPar":iStartPar, "ArrRange":[]}
        arrRangePar=ArrRangePar[strParL];  arrRangePar["ArrRange"].extend(ArrRange);  arrRangePar["iStopPar"]=iStopPar
        ArrRange=[]
      if(strPar!=None): iStartPar=i;
    strChildL=strChild
    strParL=strPar

    # Calculate nSum (number of missing in each arrRangePar)
  for strPar, arrRangePar in ArrRangePar.items():
    ArrRange=arrRangePar["ArrRange"]; iStartPar=arrRangePar["iStartPar"]; iStopPar=arrRangePar["iStopPar"]
    nSum=0
    for arrRange in ArrRange:
      iStart, iStop=arrRange; n=iStop-iStart
      nSum+=n
    arrRangePar["nSum"]=nSum

  
  printNoNL(MAKESPACE_N_SAVE)
  for strPar, arrRangePar in ArrRangePar.items():
    ArrRange=arrRangePar["ArrRange"]; iStartPar=arrRangePar["iStartPar"]; iStopPar=arrRangePar["iStopPar"]; nSum=arrRangePar["nSum"]
    if(strPar==""): strPar="(top folder)"
    print((MY_RESET+FMT_Check_Missing_In_Folder+MAKESPACE_N_SAVE) %(strPar, iStopPar-iStartPar, iStartPar, iStopPar-1, nSum))
    for arrRange in ArrRange:
      iStart, iStop=arrRange; n=iStop-iStart
      objMissingStart=ObjMissing[iStart]
      #objMissingStop=ObjMissing[iStop-1]
      strChild=objMissingStart["strChild"];   strPar=objMissingStart["strPar"];   boFile=objMissingStart["boFile"]
      if(strPar==''): strPar="(top folder)"
      if(n==1): 
        if(boFile): print((MY_RESET+"  "+FMT_Check_Missing_Single+MAKESPACE_N_SAVE) %(iStart, "Missing file:", strChild))
        else: print((MY_RESET+"  "+FMT_Check_Missing_Single+MAKESPACE_N_SAVE) %(iStart, "Missing folder:", strChild))
      else: print((MY_RESET+"  "+FMT_Check_Missing_Range+MAKESPACE_N_SAVE) %(iStart, iStop-1, n, "Missing folder:", strChild))

  return



def checkSummarizeMissingInterior(fsMeta, fsDir):  # Go through the hashcode-file, for each row (file), check if the hashcode matches the actual files hashcode  
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): print(err["strTrace"]); return
  summarizeMissing(arrDB, fsDir)


def categorizeFile(fsDir, strName):
  fsFile=fsDir+'/'+strName;     boFileFound=os.path.exists(fsFile)
  if(boFileFound): return ' ', None, None
  else:
    boFile, strPar, flChild= getHighestMissing(fsDir, strName)
    charMissing='f' if(boFile) else 'd'
    return charMissing, strPar, flChild

def printNoNL(str):
  print(str, end='')

def checkInterior(fsMeta, fsDir, intStart):  # Go through the hashcode-file, for each row (file), check if the hashcode matches the actual files hashcode  
  global tStart
  nNotFound=0; nMisMatchTimeSize=0; nMisMatchHash=0; nOK=0

  err, arrDB=parseSSVCustom(fsMeta)
  if(err): print(err["strTrace"]); return

  lenDB=len(arrDB)
  leafFileMetaOld= os.path.basename(fsMeta)

  printNoNL(MAKESPACE_N_SAVE)

    # Variables for "missing streaks"
  flMissingFile=""
  iNotFoundFirst=0
  lenFlChildL=0
  charMissingL=' '; flChildL=""
  
  nHour=0; nMin=0; nSec=0
  
  #for iRowCount, row in enumerate(arrDB):
  for iRowCount in range(intStart,lenDB):
    row=arrDB[iRowCount]
    strHashOld=row["strHash"]; intSizeOld=row["size"]; intTimeOld=row["mtime"]; strName=row["strName"]

    fsFile=fsDir+'/'+strName;   
    charMissing, strPar, flChild=categorizeFile(fsDir, strName)

    printNoNL(MY_RESET)
    
      # If streak starts
    if(charMissing=='f' and charMissingL!='f'): iNotFoundFirst=iRowCount
    elif(charMissing=='d' and charMissingL!='d'): iNotFoundFirst=iRowCount
    elif(charMissing=='d' and charMissingL=='d' and flChild!=flChildL): iNotFoundFirst=iRowCount

      # If streak continues
    if(charMissing=='f' and charMissingL=='f'): printNoNL(ANSI_CURSORUP+ANSI_CLEAR_BELOW)
    elif(charMissing=='d' and charMissingL=='d' and flChild==flChildL): printNoNL(ANSI_CURSORUP+ANSI_CLEAR_BELOW)


    tDay,nHour,nMin,nSec,tms,tus,tns=formatTDiff(time.time()-tStart)
    if(charMissing=='f'):
      nNotFoundLoc=iRowCount-iNotFoundFirst+1
      if(nNotFoundLoc==1): printNoNL((FMT_Check_Missing_Single+MAKESPACE_N_SAVE) %(iNotFoundFirst, "Missing file:", strName))
      else:
        strTmp=os.path.dirname(strName)
        if(strTmp==""): strTmp="(top folder)"
        printNoNL((FMT_Check_Missing_Range+MAKESPACE_N_SAVE) %(iNotFoundFirst, iRowCount, nNotFoundLoc, "Missing files in:", strTmp))
    elif(charMissing=='d'):
      nNotFoundLoc=iRowCount-iNotFoundFirst+1
      if(nNotFoundLoc==1): printNoNL((FMT_Check_Missing_Single+MAKESPACE_N_SAVE) %(iNotFoundFirst, "Missing folder:", flChild))
      else: printNoNL((FMT_Check_Missing_Range+MAKESPACE_N_SAVE) %(iNotFoundFirst, iRowCount, nNotFoundLoc, "Missing folder:", flChild))
    else: 
      printNoNL(("%d:%02d:%02d, "+ANSI_FONT_BOLD+"Checking row:"+ANSI_FONT_CLEAR+" %d (%s)\n") %(nHour, nMin, nSec, iRowCount, strName))
    
    charMissingL=charMissing; flChildL=flChild
    if(charMissing!=' '): nNotFound+=1; continue


      # Calculate hash
    strHash=myMD5(fsFile).decode("utf-8")   
    if(strHash!=strHashOld):  # If hashes mismatches
        # Check modTime and size (perhaps the user forgott to run sync before running check
      st = os.stat(fsFile); st_size=st.st_size; st_mtime=st.st_mtime
      intTimeNew=math.floor(st_mtime)
      boTMatch=intTimeNew==intTimeOld;    boSizeMatch=st_size==intSizeOld
      StrTmp=[]
      if(not boTMatch or not boSizeMatch ): # If meta data mismatches
        strBase=os.path.basename(strName)
        if(strBase==leafFileMetaOld): 
          strTmp=(MY_RESET+"Row: %d, (%s is ignored)") %(iRowCount, strName);      StrTmp.append(strTmp)
        else:
          strTmp = (MY_RESET+"Row: %d") %(iRowCount);      StrTmp.append(strTmp)
          StrTmp.append(ANSI_FONT_BOLD+"META MISMATCH (RUN HASHBERT SYNC)"+ANSI_FONT_CLEAR)
          tDiff=intTimeNew-intTimeOld
          tDiffHuman, charUnit=getSuitableTimeUnit(tDiff)
          if(not boTMatch): strTmp = (ANSI_FONT_BOLD+"tDiff"+ANSI_FONT_CLEAR+" (new-old): %i%c") %(tDiffHuman, charUnit);    StrTmp.append(strTmp)
          if(not boSizeMatch): strTmp = (ANSI_FONT_BOLD+"size"+ANSI_FONT_CLEAR+" (old/new): %d/%d") %(intSizeOld, st_size);    StrTmp.append(strTmp)
          
          strTmpB = "%s" %(strName);    StrTmp.append(strTmpB)
        
        nMisMatchTimeSize+=1
      else: # Meta data matches
        strTmp = (MY_RESET+"Row: %d, "+ANSI_FONT_BOLD+"Hash Mismatch"+ANSI_FONT_CLEAR) %(iRowCount);    StrTmp.append(strTmp)
        StrTmp.append("(old/new): "+strHashOld+" / "+strHash);   
        StrTmp.append(strName);    
        nMisMatchHash+=1
      
      strTmp=", ".join(StrTmp)+"\n"
      printNoNL(strTmp)
      printNoNL(MAKESPACE_N_SAVE)
    
    else: nOK+=1;  # Hashes match

  tDay,nHour,nMin,nSec,tms,tus,tns=formatTDiff(time.time()-tStart)
  StrSum=[]
  StrSum.append("RowCount: %d")
  strTmp="NotFound: %d";
  if(nNotFound): strTmp=ANSI_FONT_BOLD+strTmp+ANSI_FONT_CLEAR
  StrSum.append(strTmp)
  strTmp="MisMatchTimeSize: %d";
  if(nMisMatchTimeSize): strTmp=ANSI_FONT_BOLD+strTmp+ANSI_FONT_CLEAR
  StrSum.append(strTmp)
  strTmp="MisMatchHash: %d";
  if(nMisMatchHash): strTmp=ANSI_FONT_BOLD+strTmp+ANSI_FONT_CLEAR
  StrSum.append(strTmp)
  StrSum.append("OK: %d")
  strSum=', '.join(StrSum)

  print((MY_RESET+"Time: %d:%02d:%02d, Done ("+strSum+")") %(nHour,nMin,nSec, iRowCount, nNotFound, nMisMatchTimeSize, nMisMatchHash, nOK))
  if(nMisMatchTimeSize): print(ANSI_FONT_BOLD+"SINCE META (SIZE/TIME) MISMATCHES, IT IS OBVIOUS THAT HASHBERT SYNC WASN'T CALLED (CALL HASHBERT SYNC BEFORE RUNNING HASHBERT CHECK)"+ANSI_FONT_CLEAR)


  return ""



##################################

def dimReduce(A):
  arrO=[]
  for i, row in enumerate(A): arrO.expand(row)
  return arrO


# OTO=OneToOne, OTM=OneToMany, MTO=ManyToOne, MTM=ManyToMany
# T\S    Null    One     Many
# Null           Created Created
# One    Deleted OTO     MTO
# Many   Deleted OTM     MTM


def objManyToManyRemoveEmpty(objA, objB):  # Modifies objA, objB
  KeyDel=[]
  for key, arrA in objA.items():
    arrB=objB[key]; lenA=len(arrA); lenB=len(arrB)
    if(lenA==0 and lenB==0): KeyDel.append(key)
  for key in KeyDel:
    del objA[key]; del objB[key] 


  # objA, objB is the output of extractMatchingManyToManyF.
  # Thus objA, objB has the same property keys.
def convertObjManyToManyToMat(objA, objB):
  ArrAOTO=[]; ArrBOTO=[]; ArrAOTM=[]; ArrBOTM=[]; ArrAMTO=[]; ArrBMTO=[]; ArrAMTM=[]; ArrBMTM=[]
  arrARem=[]; arrBRem=[]
  ArrAOTNull=[]; ArrAMTNull=[]; ArrBNullTO=[]; ArrBNullTM=[]
  arrAOTNull=[]; arrAMTNull=[]; arrBNullTO=[]; arrBNullTM=[]
  arrAOTO=[]; arrBOTO=[]; arrAOTM=[]; arrBOTM=[]; arrAMTO=[]; arrBMTO=[]; arrAMTM=[]; arrBMTM=[]
  for key, arrA in objA.items():
    arrB=objB[key]
    lenA=len(arrA); lenB=len(arrB)
    if(lenA==0):
      if(lenB==0): print("lenA==0 and lenB==0"); breakpoint(); #del objA[key]; objB[key] 
      elif(lenB==1): ArrBNullTO.append(arrB);  arrBNullTO.extend(arrB)
      else: ArrBNullTM.append(arrB);  arrBNullTM.extend(arrB)
    elif(lenA==1):
      if(lenB==0): ArrAOTNull.append(arrA);  arrAOTNull.extend(arrA)
      elif(lenB==1): ArrAOTO.append(arrA); ArrBOTO.append(arrB);    arrAOTO.extend(arrA); arrBOTO.extend(arrB)
      else: ArrAOTM.append(arrA); ArrBOTM.append(arrB);    arrAOTM.extend(arrA); arrBOTM.extend(arrB)
    else:
      if(lenB==0): ArrAMTNull.append(arrA);  arrAMTNull.extend(arrA)
      elif(lenB==1): ArrAMTO.append(arrA); ArrBMTO.append(arrB);    arrAMTO.extend(arrA); arrBMTO.extend(arrB)
      else: ArrAMTM.append(arrA); ArrBMTM.append(arrB);    arrAMTM.extend(arrA); arrBMTM.extend(arrB)

  arrARem=arrAMTNull+arrAOTNull
  arrBRem=arrBNullTO+arrBNullTM
  return SimpleNamespace(**{"ArrAOTO":ArrAOTO, "ArrBOTO":ArrBOTO, "ArrAOTM":ArrAOTM, "ArrBOTM":ArrBOTM, "ArrAMTO":ArrAMTO, "ArrBMTO":ArrBMTO, "ArrAMTM":ArrAMTM, "ArrBMTM":ArrBMTM, "arrARem":arrARem, "arrBRem":arrBRem, "arrAOTO":arrAOTO, "arrBOTO":arrBOTO, "arrAOTM":arrAOTM, "arrBOTM":arrBOTM, "arrAMTO":arrAMTO, "arrBMTO":arrBMTO, "arrAMTM":arrAMTM, "arrBMTM":arrBMTM,
  "ArrAOTNull":ArrAOTNull, "ArrAMTNull":ArrAMTNull, "ArrBNullTO":ArrBNullTO, "ArrBNullTM":ArrBNullTM, "arrAOTNull":arrAOTNull, "arrAMTNull":arrAMTNull, "arrBNullTO":arrBNullTO, "arrBNullTM":arrBNullTM})



def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()


def markRelBest(ArrA, ArrB):
  for i, arrA in enumerate(ArrA):
    arrB=ArrB[i]; lenA=len(arrA); lenB=len(arrB)
    jBest=-1; kBest=-1; fitBest=0
    for j, elA in enumerate(arrA):
      #bestAByB=[None]*lenB
      for k, elB in enumerate(arrB):
        strNameA=elA["strName"]; strNameB=elB["strName"]
        rat=similar(strNameA, strNameB)
        if(rat>fitBest): fitBest=rat; jBest=j; kBest=k
    if(jBest>0): elABest=arrA.pop(jBest);  arrA.insert(0, elABest)
    if(kBest>0): elBBest=arrB.pop(kBest);  arrB.insert(0, elBBest)



# def rmFrArr(arrA, strPat):
#   regPat=re.compile(strPat)
#   for i, el in reversed(list(enumerate(arrA))):
#     res=regPat.match(el["strName"])
#     boMatch=bool(res)
#     if(boMatch): del arrA[i]
