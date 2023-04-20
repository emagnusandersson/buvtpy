
import secrets
import string
from lib import *
import time
import stat
import uuid

#from settings import *
import settings
import globvar
from libParse import *



ANSI_FONT_CLEAR=""
ANSI_FONT_BOLD=""
def formatF_Check_Missing_In_Folder(strPar, iStartPar, iStopPar, nSum):
  nSpan=iStopPar-iStartPar
  charS=pluralS(nSpan)
  #strFileIs='file is' if(nSum==1) else 'files are'
  strFileIs=pluralS(nSum, 'file is', 'files are')
  return f"In {strPar} (spanning {nSpan} row{charS} ({iStartPar}-{iStopPar-1})), {nSum} {strFileIs} missing.\n"
def formatF_Check_Missing_Single(iRow, strMissing, strName):
  return f"Row: {iRow}, {strMissing.upper()}: {strName}\n"
def formatF_Check_Missing_Range(iStart, n, strMissing, strName):
  return f"Row: {iStart}-{iStart+n-1} ({n}), {strMissing.upper()}: {strName}\n"



# N files could be categorized as renameable after matching size and time (N OTM, N MTO, N MTM) (See list in duplicateInitial.txt)
# After looking at renamed folders (N), a further N files can be categorized as renameable. (See list in renameAdditional.txt)
#   So a final N renameables after matching size and time and folder belonging (N OTM, N MTO, N MTM) (See list in duplicateFinal.txt)


# FMT_Check_Missing_In_Folder=   "In %s (spanning %d rows (%d-%d)), %d file(s) are missing.\n"
# FMT_Check_Missing_Single=    "Row: %d, " +ANSI_FONT_BOLD+"%s"+ANSI_FONT_CLEAR+" %s\n"
# FMT_Check_Missing_Range=   "Row: %d-%d (%d), " +ANSI_FONT_BOLD+"%s"+ANSI_FONT_CLEAR+" %s\n"


def myRandBase63(n):
  return ''.join(secrets.choice(string.ascii_lowercase +string.ascii_uppercase + string.digits+'_') for _ in range(n))

def myUUID():
  return myRandBase63(22)



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




class MyRealPath:
  def __init__(self):
    self.obj={}
  def realPath(self, fsPath):
    if(fsPath not in self.obj): 
      self.obj[fsPath]=myRealPathf(fsPath)
    return self.obj[fsPath]
myRealPath=MyRealPath()

  # getHighestMissing
  # The input strFile is assumed to be a missing file.
  # Returns boFile, strPar, strPath
  #   strPath: is the highest missing
  #   strPar: is parent of strPath
  #   boFile: signifies if strPath is a file or a folder
def getHighestMissing(fsDir, strFile): 
  boFile=True
  strPath=strFile
  while(1):
    strPar=os.path.dirname(strPath)
    if(strPar==''): return boFile, strPar, strPath
    fsPar=myRealPath.realPath(fsDir+charF+strPar)
    if( os.path.isdir(fsPar)): return boFile, strPar, strPath 
    strPath=strPar
    boFile=False


  # For all the files in arrDB: missing files are checked if they also have missing parents.
  # Returned array ObjMissing has the same size as arrDB. ObjMissing[i] contains info about arrDB[i].
  # arrDB entries (files) that exists in fsDir has a null entry in ObjMissing.
  # arrDB entries (files) that does not exist in fsDir, has an object with info about highest missing parent.
def checkHighestMissingArr(arrDB, fsDir):
  lenDB=len(arrDB); ObjMissing=[None]*lenDB
  for i, row in enumerate(arrDB):
    strName=row["strName"];   fsFile=fsDir+charF+strName;   boFileFound=os.path.exists(fsFile)
    if(boFileFound): obj=None #{"strPar":None, "strChild":None}
    else:
      boFile, strPar, strChild= getHighestMissing(fsDir, strName)
      obj={"boFile":boFile, "strPar":strPar, "strChild":strChild}
    ObjMissing[i]=obj;
  return ObjMissing


# def printNoNL(str):
#   print(str, end='')
  
def summarizeMissing(arrDB, fsDir):

  tStart=time.time()
  #arrDB=arrDB[:8]
  #tStop=time.time();    globvar.myConsole.printNL('checkHighestMissingArr starts, elapsed time '+str(round((tStop-tStart)*1000))+'ms')
  ObjMissing=checkHighestMissingArr(arrDB, fsDir)
  #ObjMissing[0].update({"strPar":'a'})
  #tStop=time.time();   globvar.myConsole.printNL('checkHighestMissingArr done, elapsed time '+str(round((tStop-tStart)*1000))+'ms')

  # For debugging:
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


  lenDB=len(ObjMissing)
  
    # Create objArrRangePar
  strChildL=None; strParL=None
  iStart=0; iStop=0; iStartPar=0; iStopPar=0; objArrRangePar={}; ArrRange=[]
  for i in range(0,lenDB+1):
    objMissing=ObjMissing[i] if i<lenDB else None;  #strChild=objMissing["strChild"];  strPar=objMissing["strPar"]
    strChild=objMissing["strChild"] if objMissing else None
    strPar=objMissing["strPar"] if objMissing else None
    if(strPar!=strParL):
       if(strChildL!=None): strChildL=uuid.uuid4().hex # If parent changed then force on-going child range to end.
    if(strChild!=strChildL):
      if(strChildL!=None): 
        iStop=i; ArrRange.append([iStart,iStop])
      if(strChild!=None): 
        iStart=i
    if(strPar!=strParL):
      if(strParL!=None): # parent range ended
        iStopPar=i; 
        if(strParL not in objArrRangePar): objArrRangePar[strParL]={"iStartPar":iStartPar, "ArrRange":[]}
        arrRangePar=objArrRangePar[strParL];  arrRangePar["ArrRange"].extend(ArrRange);  arrRangePar["iStopPar"]=iStopPar
        ArrRange=[]
      if(strPar!=None): iStartPar=i;
    strChildL=strChild
    strParL=strPar

    # Calculate nSum (number of missing in each arrRangePar)
  for strPar, arrRangePar in objArrRangePar.items():
    ArrRange=arrRangePar["ArrRange"]; #iStartPar=arrRangePar["iStartPar"]; iStopPar=arrRangePar["iStopPar"]
    nSum=0
    for arrRange in ArrRange:
      iStart, iStop=arrRange; n=iStop-iStart
      nSum+=n
    arrRangePar["nSum"]=nSum

    # Write objArrRangePar to console
  StrOut=[]
  for strPar, arrRangePar in objArrRangePar.items():
    ArrRange=arrRangePar["ArrRange"]; iStartPar=arrRangePar["iStartPar"]; iStopPar=arrRangePar["iStopPar"]; nSum=arrRangePar["nSum"]
    if(strPar==""): strPar="(top folder)"
    #StrOut.append((FMT_Check_Missing_In_Folder) %(strPar, iStopPar-iStartPar, iStartPar, iStopPar-1, nSum))
    StrOut.append(formatF_Check_Missing_In_Folder(strPar, iStartPar, iStopPar, nSum))
    for arrRange in ArrRange:
      iStart, iStop=arrRange; n=iStop-iStart
      objMissingStart=ObjMissing[iStart]
      #objMissingStop=ObjMissing[iStop-1]
      strChild=objMissingStart["strChild"];   strPar=objMissingStart["strPar"];   boFile=objMissingStart["boFile"]
      if(strPar==''): strPar="(top folder)"
      if(n==1): 
        strMissing="file" if(boFile) else "folder";  strMissing="Missing "+strMissing
        #StrOut.append(("  "+FMT_Check_Missing_Single) %(iStart, strMissing, strChild))
        StrOut.append("  "+formatF_Check_Missing_Single(iStart, strMissing, strChild))
      else:
        #StrOut.append(("  "+FMT_Check_Missing_Range) %(iStart, iStop-1, n, "Missing folder:", strChild))
        StrOut.append("  "+formatF_Check_Missing_Range(iStart, n, "Missing folder", strChild))
  
  
  tDay,nHour,nMin,nSec,tms,tus,tns=formatTDiff(time.time()-tStart)
  StrOut.append(("Time: %d:%02d:%02d, Done") %(nHour,nMin,nSec))
  strOut=''.join(StrOut)
  globvar.myConsole.printNL(strOut)

  return


  # Go through the meta-file, for each row (file), check if the file exist, and report those in a summaristic way.  
#def checkSummarizeMissingInterior(fsDir, fsMeta):
def checkSummarizeMissingInterior(**args):
  fsDir=myRealPathf(args["fiDir"])
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta)

  err, arrDB=parseMeta(fsMeta, settings.charTRes)
  if(err): globvar.myConsole.error(err["strTrace"]); return
  summarizeMissing(arrDB, fsDir)


def categorizeFile(fsDir, strName):
  fsFile=fsDir+charF+strName;     boFileFound=os.path.exists(fsFile)
  if(boFileFound): return ' ', None, None
  else:
    boFile, strPar, flChild= getHighestMissing(fsDir, strName)
    charMissing='f' if(boFile) else 'd'
    return charMissing, strPar, flChild


  # Go through the meta-file, for each row (file), check if the hashcode matches the actual files hashcode  
#def checkHash(fsDir, fsMeta, charTRes, iStart):
def checkInterior(**args):
  fsDir=myRealPathf(args["fiDir"])
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta) 
  iStart=int(args["iStart"])
  charTRes=args["charTRes"]

  tStart=time.time()
  myConsole=globvar.myConsole
  nNotFound=0; nMisMatchTimeSize=0; nMisMatchHash=0; nOK=0

  err, arrDB=parseMeta(fsMeta, charTRes)
  if(err): myConsole.error(err["strTrace"]); return

  lenDB=len(arrDB)
  leafFileMetaOld= os.path.basename(fsMeta)

  #myConsole.print(MAKESPACE_N_SAVE)
  myConsole.makeSpaceNSave()

    # Variables for "missing streaks"
  flMissingFile=""
  iNotFoundFirst=0
  lenFlChildL=0
  charMissingL=' '; flChildL=""
  
  nHour=0; nMin=0; nSec=0
  
  #for iRowCount, row in enumerate(arrDB):
  for iRowCount in range(iStart,lenDB):
    row=arrDB[iRowCount]
    strHashOld=row["strHash"]; intSizeOld=row["size"]; intTimeOld=row["mtime_ns64Round"]; strName=row["strName"]

    fsFile=fsDir+charF+strName;   
    charMissing, strPar, flChild=categorizeFile(fsDir, strName)

    #myConsole.print(MY_RESET)
    myConsole.myReset()
    
      # If streak starts
    if(charMissing=='f' and charMissingL!='f'): iNotFoundFirst=iRowCount
    elif(charMissing=='d' and charMissingL!='d'): iNotFoundFirst=iRowCount
    elif(charMissing=='d' and charMissingL=='d' and flChild!=flChildL): iNotFoundFirst=iRowCount

      # If streak continues
    if(charMissing=='f' and charMissingL=='f'):
      myConsole.cursorUp(); myConsole.clearBelow()
      #myConsole.print(ANSI_CURSORUP+ANSI_CLEAR_BELOW)
    elif(charMissing=='d' and charMissingL=='d' and flChild==flChildL):
      myConsole.cursorUp(); myConsole.clearBelow()
      #myConsole.print(ANSI_CURSORUP+ANSI_CLEAR_BELOW)


    tDay,nHour,nMin,nSec,tms,tus,tns=formatTDiff(time.time()-tStart)
    if(charMissing=='f'):
      nNotFoundLoc=iRowCount-iNotFoundFirst+1
      if(nNotFoundLoc==1):
        #myConsole.print((FMT_Check_Missing_Single+MAKESPACE_N_SAVE) %(iNotFoundFirst, "Missing file:", strName))
        myConsole.print(formatF_Check_Missing_Single(iNotFoundFirst, "Missing file", strName))
        myConsole.makeSpaceNSave()
      else:
        strTmp=os.path.dirname(strName)
        if(strTmp==""): strTmp="(top folder)"
        #myConsole.print((FMT_Check_Missing_Range+MAKESPACE_N_SAVE) %(iNotFoundFirst, iRowCount, nNotFoundLoc, "Missing files in:", strTmp))
        myConsole.print(formatF_Check_Missing_Range(iNotFoundFirst, nNotFoundLoc, "Missing files in", strTmp))
        myConsole.makeSpaceNSave()
    elif(charMissing=='d'):
      nNotFoundLoc=iRowCount-iNotFoundFirst+1
      if(nNotFoundLoc==1):
        #myConsole.print((FMT_Check_Missing_Single+MAKESPACE_N_SAVE) %(iNotFoundFirst, "Missing folder:", flChild))
        myConsole.print(formatF_Check_Missing_Single(iNotFoundFirst, "Missing folder", flChild))
        myConsole.makeSpaceNSave()
      else:
        #myConsole.print((FMT_Check_Missing_Range+MAKESPACE_N_SAVE) %(iNotFoundFirst, iRowCount, nNotFoundLoc, "Missing folder:", flChild))
        myConsole.print(formatF_Check_Missing_Range(iNotFoundFirst, nNotFoundLoc, "Missing folder", flChild))
        myConsole.makeSpaceNSave()
    else: 
      #myConsole.print(("%d:%02d:%02d, "+ANSI_FONT_BOLD+"Checking row:"+ANSI_FONT_CLEAR+" %d (%s)\n") %(nHour, nMin, nSec, iRowCount, strName))
      myConsole.printNL(("%d:%02d:%02d, Checking row: %d (%s)") %(nHour, nMin, nSec, iRowCount, strName))
    
    charMissingL=charMissing; flChildL=flChild
    if(charMissing!=' '): nNotFound+=1; continue


      # Calculate hash
    #strHash=myMD5(fsFile).decode("utf-8")
    strHash=myMD5W(row, fsDir)
    if(strHash!=strHashOld):  # If hashes mismatches
        # Check modTime and size (perhaps the user forgott to run sync before running check
      st = os.lstat(fsFile); st_size=st.st_size; st_mtime=st.st_mtime
      intTimeNew=math.floor(st_mtime)
      boTMatch=intTimeNew==intTimeOld;    boSizeMatch=st_size==intSizeOld
      myConsole.myReset()
      StrTmp=[]
      if(not boTMatch or not boSizeMatch ): # If meta data mismatches
        strBase=os.path.basename(strName)
        if(strBase==leafFileMetaOld):
          #strTmp=(MY_RESET+"Row: %d, (%s is ignored)") %(iRowCount, strName);   StrTmp.append(strTmp)
          strTmp=("Row: %d, (%s is ignored)") %(iRowCount, strName);   StrTmp.append(strTmp)
        else:
          #strTmp = (MY_RESET+"Row: %d") %(iRowCount);   StrTmp.append(strTmp)
          strTmp = ("Row: %d") %(iRowCount);   StrTmp.append(strTmp)
          

          StrLab=[]
          if(not boSizeMatch): StrLab.append("SIZE")
          if(not boTMatch): StrLab.append("MTIME")
          strLab=' and '.join(StrLab)
          StrTmp.append(ANSI_FONT_BOLD+strLab+" MISMATCH!!!"+ANSI_FONT_CLEAR+" (make sure to SYNC first)")
          if(not boSizeMatch): strTmp = (ANSI_FONT_BOLD+"size"+ANSI_FONT_CLEAR+" (db/new): %d/%d") %(intSizeOld, st_size);    StrTmp.append(strTmp)
          if(not boTMatch): 
            tDiff=intTimeNew-intTimeOld; tDiffHuman, charUnit=getSuitableTimeUnit(tDiff)
            strTmp = (ANSI_FONT_BOLD+"tDiff"+ANSI_FONT_CLEAR+" (new-db): %i%c") %(tDiffHuman, charUnit);    StrTmp.append(strTmp)
          
          strTmpB = "%s" %(strName);    StrTmp.append(strTmpB)
        
        nMisMatchTimeSize+=1
      else: # Meta data matches
        #strTmp = (MY_RESET+"Row: %d, "+ANSI_FONT_BOLD+"Hash Mismatch"+ANSI_FONT_CLEAR) %(iRowCount);    StrTmp.append(strTmp)
        strTmp = ("Row: %d, Hash Mismatch!!!") %(iRowCount);    StrTmp.append(strTmp)
        StrTmp.append("(db/new): "+strHashOld+" / "+strHash);   
        StrTmp.append(strName);    
        nMisMatchHash+=1
      
      strTmp=", ".join(StrTmp)
      myConsole.printNL(strTmp)
      #myConsole.print(MAKESPACE_N_SAVE)
      myConsole.makeSpaceNSave()
    
    else: nOK+=1;  # Hashes match

  tDay,nHour,nMin,nSec,tms,tus,tns=formatTDiff(time.time()-tStart)
  StrSum=[]
  StrSum.append("nRowTested/nRowTot: %d/%d")
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

  myConsole.myReset()
  myConsole.printNL(("Time: %d:%02d:%02d, Done ("+strSum+")") %(nHour,nMin,nSec, lenDB-iStart, lenDB, nNotFound, nMisMatchTimeSize, nMisMatchHash, nOK))
  if(nMisMatchTimeSize): myConsole.printNL(ANSI_FONT_BOLD+"META (SIZE/MTIME) MISMATCHES!!!"+ANSI_FONT_CLEAR+" (on "+str(nMisMatchTimeSize)+" files) This happens when the meta-file hasn't been SYNC-ed before checking")


  return ""


