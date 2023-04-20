

from lib import *
from libParse import *
from libBag import *
import globvar

  # If the leaf-most folders (of strA and strB) look the same they are cut off.
  # So the returned paths are the deverging parts.
  # Ex: strA="aaa/bbb/ccc/ddd.txt" and strB="aaa/bxb/ccc/ddd.txt" then the returned values are "aaa/bbb", "aaa/bxb"
  # If strA and strB are different only in the leaf, then the returned values are None, None.
  # Ex: strA="aaa/bbb/ccc/ddd.txt" and strB="aaa/bbb/ccc/dcd.txt" then the returned values are None, None
def extractDivergingParents(strA,strB):
  lA=len(strA); lB=len(strB); iLastSlash=None
  lShortest=lA if(lA<lB) else lB
  for i in range(-1, -lShortest, -1): # [-1, -2, ... -(lShortest-1)]
    a=strA[i]; b=strB[i]
    if(b!=a): break
    if(a==charF): iLastSlash=i
  if(iLastSlash==None): return None, None  #, None
  return strA[:iLastSlash], strB[:iLastSlash]  #, strA[iLastSlash-1:]

#strAO, strBO=extractDivergingParents("aaa/bbb/ccc/ddd.txt","aaa/bxb/ccc/ddd.txt")
#strAO, strBO=extractDivergingParents("aaa/bbb/ccc/ddd.txt","aaa/bbb/ccc/dxd.txt")


  # Ex: objAncestorOnlyRenamed={myFoldA:{myFoldB:[{"elA":rowA, "elB":rowB}, {"elA":rowA, "elB":rowB}]}}
def summarizeAncestorOnlyRename(arrA, arrB):
  objAncestorOnlyRenamed={}; n=0
  arrALeafRenamed=[]; arrBLeafRenamed=[]
  for i, rowA in enumerate(arrA):
    rowB=arrB[i]; strA=rowA["strName"]; strB=rowB["strName"]
    strParA, strParB=extractDivergingParents(strA, strB)
    if(strParA==None):
      arrALeafRenamed.append(rowA)
      arrBLeafRenamed.append(rowB)
      continue
    if(strParA not in objAncestorOnlyRenamed): objAncestorOnlyRenamed[strParA]={}
    if(strParB not in objAncestorOnlyRenamed[strParA]): objAncestorOnlyRenamed[strParA][strParB]=[]
    n+=1
    objAncestorOnlyRenamed[strParA][strParB].append({"elA":rowA, "elB":rowB})
  return n, objAncestorOnlyRenamed  #, arrALeafRenamed, arrBLeafRenamed

  # Ex: objAncestorOnlyRenamed={myFoldA:{myFoldB:[{"elA":rowA, "elB":rowB}, {"elA":rowA, "elB":rowB}]}}
  # Ex: arrAncestorOnlyRenamed=[{"n":1, "lev":0, "keyA":"myFoldA", "keyB":"myFoldB", "arrRel":[{"elA":rowA, "elB":rowB}, {"elA":rowA, "elB":rowB}]} ]
def convertObjAncestorOnlyRenamedToArr(objAncestorOnlyRenamed, StrKey=["keyA","keyB"]):
  arrAncestorOnlyRenamed=[]
  for keyA, objInner in objAncestorOnlyRenamed.items():
    lev=keyA.count(charF)
    for keyB, arrRel in objInner.items():
      n=len(arrRel)
      arrAncestorOnlyRenamed.append({"n":n, "lev":lev, StrKey[0]:keyA, StrKey[1]:keyB, "arrRel":arrRel})
  return arrAncestorOnlyRenamed


def formatAncestorOnlyRenamed(arrAncestorOnlyRenamed, fiMeta, StrOrder=["keyA","keyB"]):
  arrDisp=[]; arrMv=[]; arrSed=[]
  for row in arrAncestorOnlyRenamed:
    n=row["n"];  strSource=row[StrOrder[1]];  strTarget=row[StrOrder[0]]
    arrDisp.append("RelevantAncestor (%d file(s)):" %(n)) 
    arrDisp.append("  %s" %(strTarget))
    arrDisp.append("  %s" %(strSource))
    #boUseQuote=' ' in strTmp
    arrMv.append("  # %d file(s):" %(n)) 
    arrMv.append("mv  \"%s\" \"%s\"" %(strTarget, strSource))
    arrSed.append("sed -E 's/^( *[0-9]+ +[0-9a-f]+ +[0-9]+ +[0-9]+ +)%s(.*)/\\1%s\\2/' %s > %s" %(strTarget, strSource, fiMeta, fiMeta))
  return arrDisp, arrMv, arrSed


  # Moves "rows" (entries) from objAMetaMatch and objBMetaMatch to objAncestorOnlyRenamed and arrAIdd, arrBIdd

def extractExtraByFolder(objAMetaMatch, objBMetaMatch, objAncestorOnlyRenamed):
  arrAIdd=[]; arrBIdd=[]
  objAMetaMatchWExtraIDing={}; objBMetaMatchWExtraIDing={}
  objAncestorOnlyRenamedDiff={}
  for key in objAMetaMatch:
    arrAMetaMatch=objAMetaMatch[key].copy()
    arrBMetaMatch=objBMetaMatch[key].copy()
    objAMetaMatchWExtraIDing[key]=arrAMetaMatch; objBMetaMatchWExtraIDing[key]=arrBMetaMatch
    lenA=len(arrAMetaMatch); lenB=len(arrBMetaMatch)
    if(lenA==1 and lenB==1): continue
    for j, rowA in reversed(list(enumerate(arrAMetaMatch))):
      strA=rowA["strName"];
      for k, rowB in reversed(list(enumerate(arrBMetaMatch))):
        strB=rowB["strName"]
        strParA, strParB=extractDivergingParents(strA, strB)
        if(strParA==None): continue
        if(strParA in objAncestorOnlyRenamed and strParB in objAncestorOnlyRenamed[strParA]):
          arrAIdd.append(rowA); arrBIdd.append(rowB)
          del arrAMetaMatch[j]; del arrBMetaMatch[k]
        if(strParA not in objAncestorOnlyRenamedDiff): objAncestorOnlyRenamedDiff[strParA]={}
        if(strParB not in objAncestorOnlyRenamedDiff[strParA]): objAncestorOnlyRenamedDiff[strParA][strParB]=[]
        objAncestorOnlyRenamedDiff[strParA][strParB].append({"elA":rowA, "elB":rowB})  
  return arrAIdd, arrBIdd, objAMetaMatchWExtraIDing, objBMetaMatchWExtraIDing


def formatMatrix(Mat, nOTOAdd=0):
  nPatOTO=len(Mat.ArrAOTO); nPatMTO=len(Mat.ArrAMTO); nPatOTM=len(Mat.ArrAOTM); nPatMTM=len(Mat.ArrAMTM); nPatOTNull=len(Mat.ArrAOTNull); nPatMTNull=len(Mat.ArrAMTNull); nPatNullTO=len(Mat.ArrBNullTO); nPatNullTM=len(Mat.ArrBNullTM)
  nOTO=len(Mat.arrAOTO); nAMTO=len(Mat.arrAMTO); nBMTO=len(Mat.arrBMTO); nAOTM=len(Mat.arrAOTM); nBOTM=len(Mat.arrBOTM); nAMTM=len(Mat.arrAMTM); nBMTM=len(Mat.arrBMTM); nAOTNull=len(Mat.arrAOTNull); nAMTNull=len(Mat.arrAMTNull); nBNullTO=len(Mat.arrBNullTO); nBNullTM=len(Mat.arrBNullTM)
  strNullTO="%d" %(nBNullTO)
  strNullTM="%d(files:%d)" %(nPatNullTM, nBNullTM)
  strOTM="%d\%d" %(nAOTM, nBOTM)
  strOTNull='%d' %(nAOTNull)
  strMTNull="%d(files:%d)" %(nPatMTNull, nAMTNull)
  strMTO="%d\%d" %(nAMTO, nBMTO)
  strMTM="%d(files:%d\%d)" %(nPatMTM, nAMTM, nBMTM)
  if(nPatNullTO!=nBNullTO): globvar.myConsole.error("nPatNullTO!=nBNullTO"); breakpoint()
  if(nPatOTNull!=nAOTNull): globvar.myConsole.error("nPatOTNull!=nAOTNull"); breakpoint()
  if(nPatOTM!=nAOTM): globvar.myConsole.error("nPatOTM!=nAOTM"); breakpoint()
  if(nPatMTO!=nBMTO): globvar.myConsole.error("nPatMTO!=nBMTO"); breakpoint()
  nFileChangedNDeleted=nBNullTO+nBNullTM
  nPatChangedNDeleted=nBNullTO+nPatNullTM
  strChangedNDeleted="%d (files:%d)" %(nPatChangedNDeleted, nFileChangedNDeleted)
  nFileChangedNCreated=nAOTNull+nAMTNull
  nPatChangedNCreated=nAOTNull+nPatMTNull
  strChangedNCreated="%d (files:%d)" %(nPatChangedNCreated, nFileChangedNCreated)
  return """Source \ Target  Null          One         Many
Null %18s %12s %12s Deleted+Changed: %s
One  %18s %12d %12s
Many %18s %12s %12s
       Created+Changed %s""" %("-", strNullTO, strNullTM, strChangedNDeleted,
       strOTNull, nOTO+nOTOAdd, strOTM,
       strMTNull, strMTO, strMTM,   strChangedNCreated)


def formatMatchingDataWDup(ArrS, ArrT, boIno):
  arrOut=[]
  for i, arrS in enumerate(ArrS):
    arrT=ArrT[i]
    size=arrS[0]["size"]; mtime=arrS[0]["mtime"]
    strIno=str(arrS[0]["ino"]) if boIno else ""

    strTmp='  MatchingData %s %10d %20d' %(strIno, size, mtime)
    arrOut.append(strTmp)
    boTDup=len(arrT)>1;    boSDup=len(arrS)>1
    boAny=boTDup or boSDup

    if(not boTDup):
      if(boAny): arrOut.append('      # Target');
      arrOut.append("    "+arrT[0]["strName"])
    else:
      arrOut.append('      # Targets');
      boFirst=True
      for rowDup in arrT: 
        strComment=" " if(boFirst) else "#"; 
        arrOut.append('    '+strComment+rowDup["strName"]); boFirst=False
    if(not boSDup):
      if(boAny): arrOut.append('      # Source')
      arrOut.append("    "+arrS[0]["strName"])
    else:
      arrOut.append('      # Sources')
      boFirst=True
      for rowDup in arrS:
        strComment=" " if(boFirst) else "#"
        arrOut.append('    '+strComment+rowDup["strName"]); boFirst=False
  return arrOut



def formatMatchingData(arrS, arrT, funMatch, funUniqueS, funUniqueT=None):
  if(funUniqueT==None): funUniqueT=funUniqueS
  arrOut=[]
  for i, rowS in enumerate(arrS):
    rowT=arrT[i]
    arrOut.append(funMatch(rowS,rowT))
    arrOut.append(funUniqueT(rowT));    arrOut.append(funUniqueS(rowS))
  return arrOut

class ComparisonWOID:
  def __init__(self, arrSource, arrTarget):
    self.arrSource=arrSource; self.arrTarget=arrTarget
  
  def compare(self):
    arrSource=self.arrSource; arrTarget=self.arrTarget
        # Untouched
    arrSource=sorted(arrSource, key=lambda x: x["strName"]);   arrTarget=sorted(arrTarget, key=lambda x: x["strName"])
    arrA, arrB, arrSourceTouched, arrTargetTouched=extractMatching(arrSource, arrTarget, ['strName', 'size', 'mtime'])
    self.arrSourceUnTouched=arrA; self.arrTargetUnTouched=arrB

        # Rename (MetaMatch)
    arrSourceTouched=sorted(arrSourceTouched, key=lambda x:(x["size"], x["mtime"]));   arrTargetTouched=sorted(arrTargetTouched, key=lambda x:(x["size"], x["mtime"]))

    #def funST(rowA): return str(rowA["size"])+str(rowA["mtime"])
    def funST(rowA): return rowA["st"]
    objSourceMetaMatch, objTargetMetaMatch=extractMatchingManyToManyF(arrSourceTouched, arrTargetTouched, funST)

    MatIni=convertObjManyToManyToMat(objSourceMetaMatch, objTargetMetaMatch)
    self.MatIni=MatIni

      # Extract files not renamed in leaf 
    nAncestorOnlyRenamed, objAncestorOnlyRenamed=summarizeAncestorOnlyRename(MatIni.arrAOTO, MatIni.arrBOTO)  #, arrSourceLeafRenamed, arrTargetLeafRenamed
    arrAncestorOnlyRenamed=convertObjAncestorOnlyRenamedToArr(objAncestorOnlyRenamed, ['s', 't'])
    arrAncestorOnlyRenamed=sorted(arrAncestorOnlyRenamed, key=lambda x: -x["n"]);   arrAncestorOnlyRenamed=sorted(arrAncestorOnlyRenamed, key=lambda x: -x["lev"])
    self.arrAncestorOnlyRenamed=arrAncestorOnlyRenamed
    self.nAncestorOnlyRenamed=nAncestorOnlyRenamed

      # Extract files Idd by ancestor folder from duplicates
    arrSourceIddByFolder, arrTargetIddByFolder, objSourceMetaMatchWExtraIDing, objTargetMetaMatchWExtraIDing=extractExtraByFolder(objSourceMetaMatch, objTargetMetaMatch, objAncestorOnlyRenamed)
    
    self.arrSourceIddByFolder=arrSourceIddByFolder; self.arrTargetIddByFolder=arrTargetIddByFolder

    objManyToManyRemoveEmpty(objSourceMetaMatchWExtraIDing, objTargetMetaMatchWExtraIDing)  # Modifies the arguments
    MatFin=convertObjManyToManyToMat(objSourceMetaMatchWExtraIDing, objTargetMetaMatchWExtraIDing)
    self.MatFin=MatFin


        # Changed (NoMetaMatch with matching strName)
    arrSourceNoMetaMatch=sorted(MatFin.arrARem, key=lambda x: x["strName"]);   arrTargetNoMetaMatch=sorted(MatFin.arrBRem, key=lambda x: x["strName"])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceNoMetaMatch, arrTargetNoMetaMatch, ['strName'])
    self.arrSourceMatchingStrName=arrA; self.arrTargetMatchingStrName=arrB

    #arrCreate, arrDelete = arrSourceRem, arrTargetRem
    self.arrSourceRem=arrSourceRem; self.arrTargetRem=arrTargetRem


  def format(self, strCommandName, fsDir, fiMeta):
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)
    MatIni=self.MatIni; MatFin=self.MatFin
    nIddByFolder=len(self.arrSourceIddByFolder)

    StrScreen=[]; StrResultFile=[]; StrRenameOTO=[]; #StrRenameLeaf=[]; StrRenameAncestorOnly=[]; StrDuplicateInitial=[]; StrDuplicateFinal=[]

    strIni=formatMatrix(MatIni)
    ArrADup=MatIni.ArrAOTM+MatIni.ArrAMTO+MatIni.ArrAMTM; ArrBDup=MatIni.ArrBOTM+MatIni.ArrBMTO+MatIni.ArrBMTM
    markRelBest(ArrADup, ArrBDup)
    StrDuplicateInitial=formatMatchingDataWDup(ArrADup, ArrBDup, False)
    lenOTO=len(MatIni.ArrAOTO);   lenOTM=len(MatIni.ArrAOTM);   lenMTO=len(MatIni.ArrAMTO);   lenMTM=len(MatIni.ArrAMTM)

      # Leaf- vs Parent- changes 
    StrRenameAncestorOnly, StrRenameAncestorOnlyMv, StrRenameAncestorOnlySed=formatAncestorOnlyRenamed(self.arrAncestorOnlyRenamed, fiMeta, ["t", "s"])
    StrRenameAncestorOnlyCmd=StrRenameAncestorOnlyMv + StrRenameAncestorOnlySed
    if(len(StrRenameAncestorOnlyCmd)):StrRenameAncestorOnlyCmd=["cd "+fsDir]+StrRenameAncestorOnlyCmd


    strFin=formatMatrix(MatFin, nIddByFolder)
    ArrADup=MatFin.ArrAOTM+MatFin.ArrAMTO+MatFin.ArrAMTM; ArrBDup=MatFin.ArrBOTM+MatFin.ArrBMTO+MatFin.ArrBMTM
    markRelBest(ArrADup, ArrBDup)
    StrDuplicateFinal=formatMatchingDataWDup(MatFin.ArrAOTM+MatFin.ArrAMTO+MatFin.ArrAMTM, MatFin.ArrBOTM+MatFin.ArrBMTO+MatFin.ArrBMTM, False)

    #StrRenameAdditional=formatMatchingDataOld(self.arrSourceIddByFolder, self.arrTargetIddByFolder, ['size', 'mtime'], ['strName'], '  MatchingData %10d %20d', '    %s')
    funMatch=lambda s,t: '  MatchingData %10d %20d' %(s["size"],s["mtime"]);  funUnique=lambda s: "    %s" %(s["strName"])
    StrRenameAdditional=formatMatchingData(self.arrSourceIddByFolder, self.arrTargetIddByFolder, funMatch, funUnique)


      # Format OTO
    #StrTmp=formatMatchingDataOld(MatFin.arrAOTO, MatFin.arrBOTO, ['size', 'mtime'], ['strName'], '  MatchingData %10d %20d', '    %s')
    funMatch=lambda s,t: '  MatchingData %10d %20d' %(s["size"],s["mtime"]);  funUnique=lambda s: "    %s" %(s["strName"])
    StrTmp=formatMatchingData(MatFin.arrAOTO, MatFin.arrBOTO, funMatch, funUnique)
    if(len(StrTmp)): StrRenameOTO.append("# Rename (MetaMatch) one-to-one match of size and time")
    StrRenameOTO.extend(StrTmp)

    StrResultFile.append("Result from running %s" %(strCommandName))

    strTmp='Files in Source/Target: %d/%d' %(nSource, nTarget);    StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
    strTmp='Untouched (Matching strName and ST (ST=size and time)): %d' %(nUnTouched);    StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)

    strTmp="Identification table: (ST- (size-and-time-combo-) occurances (after the untouched files are removed))";   StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
    StrScreen.append(strIni);   StrResultFile.append(strIni)
    
    StrTmp=[];
    StrTmp.append('OTO files only renamed in folder: %d. (%d folders)' %(self.nAncestorOnlyRenamed, len(self.arrAncestorOnlyRenamed)));
    StrScreen.extend(StrTmp);    StrResultFile.extend([""]+StrTmp)

    if(nIddByFolder):
      StrTmp=[];
      StrTmp.append('%d files can be futher be identified by looking at renamed folders.' %(nIddByFolder));
      lenOTO=len(MatFin.ArrAOTO);   lenOTM=len(MatFin.ArrAOTM);   lenMTO=len(MatFin.ArrAMTO);   lenMTM=len(MatFin.ArrAMTM)

      StrScreen.extend(StrTmp);    StrResultFile.extend([""]+StrTmp)

      strTmp="""Modified identification table after recategorizing files identified via renamed folders:""";   StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
      StrScreen.append(strFin);   StrResultFile.append(strFin)

    strDupExtra=" (others may be found among those with duplicate ST)" if(len(ArrADup)) else ""
    strTmp='Changed (Matching strName): %d%s' %(nMatchingStrName, strDupExtra);  StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
    #arrData=formatMatchingDataOld(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, ['strName'], ['size', 'mtime'], '  MatchingData %s', '    %10d %10d')
    funMatch=lambda s,t: '  MatchingData %s' %s["strName"];  funUnique=lambda s: '    %10d %10d' %(s["size"],s["mtime"])
    arrData=formatMatchingData(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, funMatch, funUnique)
    StrResultFile.extend(arrData)

    strTmp='Created: %d%s' %(nSourceRem, strDupExtra); StrScreen.append(strTmp);  StrResultFile.append('\n'+strTmp)
    for i, row in enumerate(self.arrSourceRem): StrResultFile.append('%10d %10d %s' %(row["size"], row["mtime"], row["strName"]))
    strTmp='Deleted: %d%s' %(nTargetRem, strDupExtra); StrScreen.append(strTmp);  StrResultFile.append('\n'+strTmp)
    for i, row in enumerate(self.arrTargetRem): StrResultFile.append('%10d %10d %s' %(row["size"], row["mtime"], row["strName"]))

    return [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional]

    


class ComparisonWID:
  def __init__(self, strIdType, arrSource, arrTarget):
    self.strIdType=strIdType; self.arrSource=arrSource; self.arrTarget=arrTarget
  
  def compare(self):
    strIdType=self.strIdType; arrSource=self.arrSource; arrTarget=self.arrTarget
        # Untouched
    arrSource=sorted(arrSource, key=lambda x: x["strName"]);   arrTarget=sorted(arrTarget, key=lambda x: x["strName"])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSource, arrTarget, ['strName', strIdType, 'size', 'mtime']) 
    self.arrSourceUnTouched=arrA; self.arrTargetUnTouched=arrB

        # Changed
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ['strName', strIdType])
    self.arrSourceChanged=arrA; self.arrTargetChanged=arrB

        # Rename (MetaMatch)
    arrSourceRem=sorted(arrSourceRem, key=lambda x: x[strIdType]);   arrTargetRem=sorted(arrTargetRem, key=lambda x: x[strIdType])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, [strIdType, 'size', 'mtime'])
    self.arrSourceMetaMatch=arrA; self.arrTargetMetaMatch=arrB
    
    nAncestorOnlyRenamed, objAncestorOnlyRenamed=summarizeAncestorOnlyRename(self.arrSourceMetaMatch, self.arrTargetMetaMatch)
    arrAncestorOnlyRenamed=convertObjAncestorOnlyRenamedToArr(objAncestorOnlyRenamed, ['s', 't'])
    arrAncestorOnlyRenamed=sorted(arrAncestorOnlyRenamed, key=lambda x: -x["n"]);   arrAncestorOnlyRenamed=sorted(arrAncestorOnlyRenamed, key=lambda x: -x["lev"])
    self.arrAncestorOnlyRenamed=arrAncestorOnlyRenamed

        # Copy renamed to origin
    arrSourceRem=sorted(arrSourceRem, key=lambda x: x["strName"]);   arrTargetRem=sorted(arrTargetRem, key=lambda x: x["strName"])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ["strName", 'size', 'mtime'])
    self.arrSourceNST=arrA; self.arrTargetNST=arrB

        # Matching strName
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ['strName']) 
    self.arrSourceMatchingStrName=arrA; self.arrTargetMatchingStrName=arrB

        # Matching id
    arrSourceRem=sorted(arrSourceRem, key=lambda x: x[strIdType]);   arrTargetRem=sorted(arrTargetRem, key=lambda x: x[strIdType])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, [strIdType])
    self.arrSourceMatchingId=arrA; self.arrTargetMatchingId=arrB


        # Matching ST (Copy)
    #arrSourceRem=sorted(arrSourceRem, key=lambda x:(x["size"], x["mtime"]));   arrTargetRem=sorted(arrTargetRem, key=lambda x:(x["size"], x["mtime"]))
    #def funST(rowA): return str(rowA["size"])+str(rowA["mtime"])
    #objSourceMetaMatch, objTargetMetaMatch=extractMatchingManyToManyF(arrSourceRem, arrTargetRem, funST)

    self.arrSourceRem=arrSourceRem; self.arrTargetRem=arrTargetRem


  def format(self, strCommandName, fsDir, fiMeta):
    strIdType=self.strIdType
    strIdTypeL='FileId' if(strIdType=='ino') else strIdType  #"L" for Long (inode instead of ino)
    #strIdTypeL=strIdType 
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nChanged=len(self.arrSourceChanged)
    nMetaMatch=len(self.arrSourceMetaMatch)
    nNST=len(self.arrSourceNST)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nMatchingId=len(self.arrSourceMatchingId)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)

      # Format info data
    StrScreen=[]; StrResultFile=[]; StrRenameOTO=[]; StrDuplicateInitial=[]; StrDuplicateFinal=[]; StrRenameAdditional=[]
    StrResultFile.append("Result from running %s" %(strCommandName))

    strTmp='Matching meta data               # Categorized as:                       short-cut action';    StrScreen.append(strTmp)
    strTmp='%s, strName, ST  source/target' %(strIdTypeL);    StrScreen.append(strTmp)
    strTmp='  OK      OK     OK:% 14d Untouched                             leave unchanged' %(nUnTouched);    StrScreen.append(strTmp)
    strTmp='Untouched: (Matching: %s, strName, ST): %d' %(strIdTypeL, nUnTouched);    StrResultFile.append('\n'+strTmp)
    
    strTmp='  OK      OK     - :% 14d Changed                               (none)' %(nChanged);    StrScreen.append(strTmp)
    strTmp='Changed: (Matching: %s, strName, - ): %d' %(strIdTypeL, nChanged);    StrResultFile.append('\n'+strTmp)
    #arrData=formatMatchingDataOld(self.arrSourceChanged, self.arrTargetChanged, [strIdTypeL, "strName"], ['size', 'mtime'], '  MatchingData %s %s', '    %10d %20d')
    funMatch=lambda s,t: '  MatchingData %s %s' %(s[strIdType],s["strName"]);  funUnique=lambda s: '    %10d %20d' %(s["size"],s["mtime"])
    arrData=formatMatchingData(self.arrSourceChanged, self.arrTargetChanged, funMatch, funUnique)

    StrResultFile.extend(arrData)

    strTmp='  OK      -      OK:% 14d Renamed                               set new name' %(nMetaMatch);   StrScreen.append(strTmp)
    strTmp='Renamed: (Matching: %s,    -   , ST): %d' %(strIdTypeL, nMetaMatch);   StrResultFile.append('\n'+strTmp)
    #strTmp='  Leafs: %d' %(len(arrSourceLeafRenamed));   StrScreen.append(strTmp);   StrResultFile.append(strTmp)
    #StrRenameOTO.append("#All except duplicates")
    #StrTmp=formatMatchingDataOld(self.arrSourceMetaMatch, self.arrTargetMetaMatch, [strIdType, 'size', 'mtime'], ["strName"], '  MatchingData %s %10d %20d', '    %s')
    funMatch=lambda s,t: '  MatchingData %s %10d %20d' %(s[strIdType],s["size"],s["mtime"]);  funUnique=lambda s: '    %s' %(s["strName"])
    StrTmp=formatMatchingData(self.arrSourceMetaMatch, self.arrTargetMetaMatch, funMatch, funUnique)
    StrRenameOTO.extend(StrTmp)

    StrRenameAncestorOnly, StrRenameAncestorOnlyMv, StrRenameAncestorOnlySed=formatAncestorOnlyRenamed(self.arrAncestorOnlyRenamed, fiMeta, ["t", "s"])
    StrRenameAncestorOnlyCmd=StrRenameAncestorOnlyMv + StrRenameAncestorOnlySed
    if(len(StrRenameAncestorOnlyCmd)):StrRenameAncestorOnlyCmd=["cd "+fsDir]+StrRenameAncestorOnlyCmd

    strTmp='  -       OK     OK:% 14d File copied, then renamed to origin   set new inode' %(nNST);   StrScreen.append(strTmp)
    strTmp='File copied, then renamed to origin: (Matching:  -, strName, ST): %d' %(nNST);   StrResultFile.append('\n'+strTmp)
    #arrData=formatMatchingDataOld(self.arrSourceNST, self.arrTargetNST, ["strName", 'size', 'mtime'], [strIdTypeL], '  MatchingData %s %10d %20d', '    %s')
    funMatch=lambda s,t: '  MatchingData %s %10d %20d' %(s["strName"],s["size"],s["mtime"]);  funUnique=lambda s: '    %s' %(s[strIdType])
    arrData=formatMatchingData(self.arrSourceNST, self.arrTargetNST, funMatch, funUnique)
    StrResultFile.extend(arrData)

    strTmp='  -       OK     - :% 14d Deleted+recreated                     (none)' %(nMatchingStrName);  StrScreen.append(strTmp)
    strTmp='Deleted+recreated: (Matching:  - , strName, - ): %d' %(nMatchingStrName);  StrResultFile.append('\n'+strTmp)
    #arrData=formatMatchingDataOld(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, ['strName'], [strIdType, 'size', 'mtime'], '  MatchingData %s', '    %s %10d %10d')
    funMatch=lambda s,t: '  MatchingData %s' %(s['strName']);  funUnique=lambda s: '    %s %10d %10d' %(s[strIdType],s["size"],s["mtime"])
    arrData=formatMatchingData(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, funMatch, funUnique)
    StrResultFile.extend(arrData)

    strTmp='  OK      -      - :% 14d Reused id (or renamed and changed)    (none)' %(nMatchingId);   StrScreen.append(strTmp)
    strTmp='Reused id (or renamed and changed): (Matching: %s,    -   , - ): %d' %(strIdTypeL, nMatchingId);   StrResultFile.append('\n'+strTmp)
    #arrData=formatMatchingDataOld(self.arrSourceMatchingId, self.arrTargetMatchingId, [strIdType], ['size', 'mtime', "strName"], '  MatchingData %s', '    %10d %10d %s')
    funMatch=lambda s,t: '  MatchingData %s' %(s[strIdType]);  funUnique=lambda s: '    %10d %10d %s' %(s["size"],s["mtime"], s["strName"])
    arrData=formatMatchingData(self.arrSourceMatchingId, self.arrTargetMatchingId, funMatch, funUnique)
    StrResultFile.extend(arrData)

    #strTmp='Copy                                -      -     OK : %d' %(-1);   StrScreen.append(strTmp)

    strTmpA='%d/%d' %(nSourceRem, nTargetRem)
    strTmp='  -       -      - :% 14s Created/Deleted (source/target)       (none)' %(strTmpA); StrScreen.append(strTmp);
    #strTmp='WO any matching: %d/%d (source(created)/target(deleted))' %(nSourceRem, nTargetRem); StrResultFile.append('\n'+strTmp);

    strTmpA='%d/%d' %(nSource, nTarget)
    strTmp=' # in Source/Target:% 14s' %(strTmpA);    StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)

    strTmp='Created: %d' %(nSourceRem); StrResultFile.append('\n'+strTmp)
    for i, row in enumerate(self.arrSourceRem): StrResultFile.append('%s %10d %10d %s' %(row[strIdType], row["size"], row["mtime"], row["strName"]))
    strTmp='Deleted: %d' %(nTargetRem); StrResultFile.append('\n'+strTmp)
    for i, row in enumerate(self.arrTargetRem): StrResultFile.append('%s %10d %10d %s' %(row[strIdType], row["size"], row["mtime"], row["strName"]))
    
    nSomeKindOfMatching=nUnTouched+nChanged+nMetaMatch+nNST+nMatchingId+nMatchingStrName
    nSourceCheck=nSomeKindOfMatching+nSourceRem; nTargetCheck=nSomeKindOfMatching+nTargetRem
          # Checking the sums
    boSourceOK=nSource==nSourceCheck; boTargetOK=nTarget==nTargetCheck
    boBoth=boSourceOK and boTargetOK
    strOK="OK"; strNOK="NOK" # strOK="OK"; strNOK="✗"
    strNSourceMatch=strOK if(boSourceOK) else strNOK; strNTargetMatch=strOK if(boTargetOK) else strNOK

    if(not boSourceOK or not boTargetOK):
      strCheck="Checking the sums of the categories: Source: %d (%s), Target: %d (%s)" %(nSourceCheck, strNSourceMatch, nTargetCheck, strNTargetMatch);  StrScreen.append(strCheck)
      strTmp='!!ERROR the sums does not match with the number of files';  StrScreen.append(strTmp)

    return [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd]

  def getCategoryArrays(self):
    arrSourceUnTouched=self.arrSourceUnTouched; arrTargetUnTouched=self.arrTargetUnTouched
    arrSourceChanged=self.arrSourceChanged; arrTargetChanged=self.arrTargetChanged
    arrSourceMetaMatch=self.arrSourceMetaMatch; arrTargetMetaMatch=self.arrTargetMetaMatch
    arrSourceNST=self.arrSourceNST; arrTargetNST=self.arrTargetNST
    arrSourceMatchingStrName=self.arrSourceMatchingStrName; arrTargetMatchingStrName=self.arrTargetMatchingStrName
    arrSourceMatchingId=self.arrSourceMatchingId; arrTargetMatchingId=self.arrTargetMatchingId
    arrSourceRem=self.arrSourceRem; arrTargetRem=self.arrTargetRem
    return [arrSourceUnTouched, arrTargetUnTouched, arrSourceChanged, arrTargetChanged, arrSourceMetaMatch, arrTargetMetaMatch, arrSourceNST, arrTargetNST, arrSourceMatchingStrName, arrTargetMatchingStrName, arrSourceMatchingId, arrTargetMatchingId, arrSourceRem, arrTargetRem]

