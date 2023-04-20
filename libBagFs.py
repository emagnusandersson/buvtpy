

from lib import *
from libParse import *
from libBag import *
import globvar
import numpy as np

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





# summarizeAncestorOnlyRename(arrA, arrB)
# arrA and arrB (arrays) correspond to each other in that: For a certain i, arrA[i] and arrB[i] matches (One-To-One) (in some way (like having matching metadata)). But the have different strName (path).
#
# Ex:
#   Assume the input arrays:
# arrA=[{strName:"/abc/def/ghi/jkl.txt"},       {strName:"/abc/dQQQf/ghi/mmm.txt"},       {strName:"/abc/dQQQf/ghi/nnn.txt"}, {strName:"/stu/ooo.txt"}]
# arrB=[        {strName:"/mno/pqr.txt"}, {strName:"/blah/blah/dRRRf/ghi/mmm.txt"}, {strName:"/blah/blah/dRRRf/ghi/nnn.txt"}, {strName:"/vwx/ooo.txt"}]
#   Which can also be written like this (to simplyfy the notation):
# arrA=[fileA0, fileA1, fileA2, fileA3], arrB=[fileB0, fileB1, fileB2, fileB3]
#   Or extracting only the strName (path):
# PathA=["/abc/def/ghi/jkl.txt",       "/abc/dQQQf/ghi/mmm.txt",       "/abc/dQQQf/ghi/nnn.txt", "/stu/ooo.txt"]
# PathB=[        "/mno/pqr.txt", "/blah/blah/dRRRf/ghi/mmm.txt", "/blah/blah/dRRRf/ghi/nnn.txt", "/vwx/ooo.txt"]
#
# When you compare the paths of resp index, you find this:
# PathA[0] is different from PathB[0] in the leaf-part (right most part) (thus these will not be included in the output)
# PathA[1] diverges from PathB[1] in the "grandparent" (of the leaf): "/abc/dQQQf" resp "/blah/blah/dRRRf"
# PathA[2] diverges from PathB[2] in the (same as previous) "grandparent" (of the leaf): "/abc/dQQQf" resp "/blah/blah/dRRRf"
# PathA[3] diverges from PathB[3] in "/stu" resp "/vwx"
#
# Then the output becomes:
# objAncestorOnlyRenamed={
#    "/abc/dQQQf:"{"/blah/blah/dRRRf":[{"elA":fileA1, "elB":fileB1}, {"elA":fileA2, "elB":fileB2}]},
#    "/stu":{"/vwx":[{"elA":fileA3, "elB":fileB3}]}
# }
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
    arrDisp.append("RelevantAncestor (%d file%s):" %(n, pluralS(n))) 
    arrDisp.append("  %s" %(strTarget))
    arrDisp.append("  %s" %(strSource))
    #boUseQuote=' ' in strTmp
    arrMv.append("  # %d file%s:" %(n, pluralS(n))) 
    arrMv.append("mv  \"%s\" \"%s\"" %(strTarget, strSource))
    arrSed.append("sed -E 's/^( *[0-9]+ +[0-9a-f]+ +[0-9]+ +[0-9]+ +)%s(.*)/\\1%s\\2/' %s > %s" %(strTarget, strSource, fiMeta, fiMeta))
  return arrDisp, arrMv, arrSed


  # Moves "rows" (entries) from objAMetaMatch and objBMetaMatch to objAncestorOnlyRenamed and arrAIdd, arrBIdd
  # Ex of input:
  #   objAMetaMatch={"0000000001_123487081324":[{inode:..., name:...}, {inode:..., name:...}], "0000000002_123487081324":[]}
  #   objBMetaMatch={"0000000001_123487081324":[{inode:..., name:...}], "0000000002_123487081324":[{inode:..., name:...}]}
  #     objAMetaMatch and objBMetaMatch has the same keys.
  #   objAncestorOnlyRenamed is the second output from summarizeAncestorOnlyRename
  # Output arrAIdd and arrBIdd, are file that can be identified using this method
  # objAMetaMatchAfterExtraIDing and objBMetaMatchAfterExtraIDing are corresponds to objAMetaMatch, objBMetaMatch with extra idd files removed.
def extractExtraByFolder(objAMetaMatch, objBMetaMatch, objAncestorOnlyRenamed):
  arrAIdd=[]; arrBIdd=[]
  objAMetaMatchWExtraIDing={}; objBMetaMatchWExtraIDing={}
  #objAncestorOnlyRenamedDiff={}
  for key in objAMetaMatch:
    arrAMetaMatch=objAMetaMatch[key].copy()
    arrBMetaMatch=objBMetaMatch[key].copy()
    objAMetaMatchWExtraIDing[key]=arrAMetaMatch; objBMetaMatchWExtraIDing[key]=arrBMetaMatch
    lenA=len(arrAMetaMatch); lenB=len(arrBMetaMatch)
    if(lenA==1 and lenB==1): continue
    for j, fileA in reversed(list(enumerate(arrAMetaMatch))):
      strA=fileA["strName"]
      for k, fileB in reversed(list(enumerate(arrBMetaMatch))):
        strB=fileB["strName"]
        strParA, strParB=extractDivergingParents(strA, strB)
        if(strParA==None): continue
        if(strParA in objAncestorOnlyRenamed and strParB in objAncestorOnlyRenamed[strParA]):
          arrAIdd.append(fileA); arrBIdd.append(fileB)
          del arrAMetaMatch[j]; del arrBMetaMatch[k]
          break

          # The below lines (in this for loop) are really unnecessary since objAncestorOnlyRenamedDiff is never outputed
        # if(strParA not in objAncestorOnlyRenamedDiff): objAncestorOnlyRenamedDiff[strParA]={}
        # if(strParB not in objAncestorOnlyRenamedDiff[strParA]): objAncestorOnlyRenamedDiff[strParA][strParB]=[]
        # objAncestorOnlyRenamedDiff[strParA][strParB].append({"elA":fileA, "elB":fileB})  
  return arrAIdd, arrBIdd, objAMetaMatchWExtraIDing, objBMetaMatchWExtraIDing


def formatMatrix(Mat, nOTOAdd=0):
  nPatNullTO=len(Mat.ArrBNullTO); nPatNullTM=len(Mat.ArrBNullTM)
  nPatOTNull=len(Mat.ArrAOTNull); nPatOTO=len(Mat.ArrAOTO); nPatOTM=len(Mat.ArrAOTM)
  nPatMTNull=len(Mat.ArrAMTNull); nPatMTO=len(Mat.ArrAMTO); nPatMTM=len(Mat.ArrAMTM)
  
  nANullTO=0; nBNullTO=len(Mat.arrBNullTO); nANullTM=0; nBNullTM=len(Mat.arrBNullTM)
  #if(nANullTO!=0): globvar.myConsole.error("nANullTO!=0"); breakpoint() 
  #if(nANullTM!=0): globvar.myConsole.error("nANullTM!=0"); breakpoint()
    
  nAOTNull=len(Mat.arrAOTNull); nBOTNull=0; nAOTO=len(Mat.arrAOTO); nBOTO=len(Mat.arrBOTO); nAOTM=len(Mat.arrAOTM); nBOTM=len(Mat.arrBOTM)
  #if(nBOTNull!=0): globvar.myConsole.error("nBOTNull!=0"); breakpoint()
  if(nAOTO!=nBOTO): globvar.myConsole.error(nAOTO!=nBOTO); breakpoint()
  
  nAMTNull=len(Mat.arrAMTNull); nBMTNull=0; nAMTO=len(Mat.arrAMTO); nBMTO=len(Mat.arrBMTO); nAMTM=len(Mat.arrAMTM); nBMTM=len(Mat.arrBMTM)  
  #if(nBMTNull!=0): globvar.myConsole.error("nBMTNull!=0"); breakpoint()

  if(nPatNullTO!=nBNullTO): globvar.myConsole.error("nPatNullTO!=nBNullTO"); breakpoint()
  if(nPatOTNull!=nAOTNull): globvar.myConsole.error("nPatOTNull!=nAOTNull"); breakpoint()
  if(nPatOTM!=nAOTM): globvar.myConsole.error("nPatOTM!=nAOTM"); breakpoint()
  if(nPatMTO!=nBMTO): globvar.myConsole.error("nPatMTO!=nBMTO"); breakpoint()

  strNullTO="%d" %(nBNullTO)
  strNullTM="%d(-\%d)" %(nPatNullTM, nBNullTM)
  strOTNull='%d' %(nAOTNull)
  strOT0='%d' %(nAOTO+nOTOAdd)
  strOTM="%d(%d\%d)" %(nPatOTM, nAOTM, nBOTM)
  strMTNull="%d(%d\\-)" %(nPatMTNull, nAMTNull)
  strMTO="%d(%d\%d)" %(nPatMTO, nAMTO, nBMTO)
  strMTM="%d(%d\%d)" %(nPatMTM, nAMTM, nBMTM)
  nFileChangedNDeleted=nBNullTO+nBNullTM
  nPatChangedNDeleted=nBNullTO+nPatNullTM
  strChangedNDeleted="%d(%d)" %(nPatChangedNDeleted, nFileChangedNDeleted)
  nFileChangedNCreated=nAOTNull+nAMTNull
  nPatChangedNCreated=nAOTNull+nPatMTNull
  strChangedNCreated="%d(%d)" %(nPatChangedNCreated, nFileChangedNCreated)
  strA= """Source⇣ \ Target⇾ _____0____________1___________>1___________
  0  |%18s %12s %12s ∑=%s (Deleted+Changed)
  1  |%18s %12s %12s
 >1  |%18s %12s %12s""" %("(∞)", strNullTO, strNullTM, strChangedNDeleted,
       strOTNull, strOT0, strOTM,
       strMTNull, strMTO, strMTM)
  strB="""⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻⎻∑=%s (Created+Changed)""" %( strChangedNCreated)
  strB=f"{strB:⎻<60}"
  return strA+'\n'+strB
  #⇣↓¯⎻ˉf̅▒∞



  # ArrS, ArrT are two-dimensional arrays
  # Each row contains an array of elements who matches
def formatMatchingDataWDup(ArrS, ArrT, funMatch, funUniqueFirst, funUnique): 
  arrOut=[]
  for i, arrS in enumerate(ArrS):
    arrT=ArrT[i]
    strTmp=funMatch(arrS[0],arrT[0])
    arrOut.append(strTmp)
    nT=len(arrT); nS=len(arrS)
    boTUniq=nT==1;    boSUniq=nS==1
    boBothUniq=boTUniq and boSUniq
    
    if(not boBothUniq): arrOut.append('      # Target'+pluralS(nT))  # If both S and T are unique, then skip the labelcomment (to be more compact)
    boFirst=True
    for rowDup in arrT: 
      if(boFirst): strTmp=funUniqueFirst(rowDup)
      else: strTmp=funUnique(rowDup)
      arrOut.append(strTmp)
      boFirst=False
    
    if(not boBothUniq): arrOut.append('      # Source'+pluralS(nS))  # If both S and T are unique, then skip the labelcomment (to be more compact)
    boFirst=True
    for rowDup in arrS:
      if(boFirst): strTmp=funUniqueFirst(rowDup)
      else: strTmp=funUnique(rowDup)
      arrOut.append(strTmp)
      boFirst=False
  return arrOut

  # ObjA is a dict where each "key", is the matching data, and each "val" is an array of the elements that measures to that data.
def formatMatchingDataWDupSingleDataSet(ObjA, funMatch, funUnique): 
  arrOut=[]
  for k, arr in ObjA.items():
    strTmp=funMatch(arr[0])
    arrOut.append(strTmp)
    for row in arr: 
      strTmp=funUnique(row)
      arrOut.append(strTmp)
  return arrOut



def formatMatchingData(arrS, arrT, funMatch, funUniqueS, funUniqueT=None):
  if(funUniqueT==None): funUniqueT=funUniqueS
  arrOut=[]
  for i, rowS in enumerate(arrS):
    rowT=arrT[i]
    arrOut.append(funMatch(rowS,rowT))
    arrOut.append(funUniqueT(rowT));    arrOut.append(funUniqueS(rowS))
  return arrOut


class ComparisonWID:
  def __init__(self, strIdType, arrSource, arrTarget, strCommandName, myReporter):
    self.strIdType=strIdType; self.arrSource=arrSource; self.arrTarget=arrTarget
    self.strCommandName=strCommandName; self.myReporter=myReporter
  
  def compare(self):
    strIdType=self.strIdType; arrSource=self.arrSource; arrTarget=self.arrTarget
        # Untouched
    #arrSource.sort(key=lambda x: x["strName"]);   arrTarget.sort(key=lambda x: x["strName"])
    arrSource.sort(key=lambda x: x["strName"]);   arrTarget.sort(key=lambda x: x["strName"])
    #arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSource, arrTarget, ['strName', strIdType, 'size', 'mtime_ns64Round']) 
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSource, arrTarget, ['strName', strIdType, 'st']) 
    self.arrSourceUnTouched=arrA; self.arrTargetUnTouched=arrB

        # Changed
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ['strName', strIdType])
    self.arrSourceChanged=arrA; self.arrTargetChanged=arrB

        # Rename (MetaMatch)
    arrSourceRem.sort(key=lambda x: x[strIdType]);   arrTargetRem.sort(key=lambda x: x[strIdType])
    #arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, [strIdType, 'size', 'mtime_ns64Round'])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, [strIdType, 'st'])
    self.arrSourceMetaMatch=arrA; self.arrTargetMetaMatch=arrB
    
        # arrAncestorOnlyRenamed is never used in T2M
      # Extract files not renamed in leaf 
    # nAncestorOnlyRenamed, objAncestorOnlyRenamed=summarizeAncestorOnlyRename(self.arrSourceMetaMatch, self.arrTargetMetaMatch)
    # arrAncestorOnlyRenamed=convertObjAncestorOnlyRenamedToArr(objAncestorOnlyRenamed, ['s', 't'])
    # arrAncestorOnlyRenamed.sort(key=lambda x: -x["n"]);   arrAncestorOnlyRenamed.sort(key=lambda x: -x["lev"])
    # self.arrAncestorOnlyRenamed=arrAncestorOnlyRenamed

        # Copy renamed to origin
    arrSourceRem.sort(key=lambda x: x["strName"]);   arrTargetRem.sort(key=lambda x: x["strName"])
    #arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ["strName", 'size', 'mtime_ns64Round'])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ["strName", 'st'])
    self.arrSourceNST=arrA; self.arrTargetNST=arrB

        # Matching strName
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ['strName']) 
    self.arrSourceMatchingStrName=arrA; self.arrTargetMatchingStrName=arrB

        # Matching id
    arrSourceRem.sort(key=lambda x: x[strIdType]);   arrTargetRem.sort(key=lambda x: x[strIdType])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, [strIdType])
    self.arrSourceMatchingId=arrA; self.arrTargetMatchingId=arrB


        # Matching ST (Copy)
    #arrSourceRem.sort(key=lambda x:(x["size"], x["mtime_ns64Round"]));   arrTargetRem.sort(key=lambda x:(x["size"], x["mtime_ns64Round"]))
    #def funST(rowA): return str(rowA["st"])
    #objSourceMetaMatch, objTargetMetaMatch=extractMatchingManyToManyF(arrSourceRem, arrTargetRem, funST)

    self.arrSourceRem=arrSourceRem; self.arrTargetRem=arrTargetRem


  def formatScreen(self):
    strIdType=self.strIdType
    strIdTypeL='FileId' if(strIdType=='ino') else strIdType  #"L" for Long (inode instead of ino)
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nChanged=len(self.arrSourceChanged)
    nMetaMatch=len(self.arrSourceMetaMatch)
    nNST=len(self.arrSourceNST)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nMatchingId=len(self.arrSourceMatchingId)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)

    StrScreen=[]

    strTmp='Matching meta data               # Categorized as:                                     Action';    StrScreen.append(strTmp)
    n=nUnTouched
    strTmp='%s, strName, ST  source/target                                          None  Short-cut  Delete   Write' %(strIdTypeL);    StrScreen.append(strTmp)
    strTmp='  OK      OK     OK:% 14d Untouched%36d       -       -        -' %(n, n);    StrScreen.append(strTmp)

    n=nChanged
    strTmp='  OK      OK     - :% 14d Changed                                    -        -    % 7d % 7d' %(n,n,n);    StrScreen.append(strTmp)

    strTmpA='(set new name) %d' %(nMetaMatch)
    strTmp='  OK      -      OK:% 14d Renamed %48s    -        -' %(nMetaMatch, strTmpA);   StrScreen.append(strTmp)

    strTmpA='(set new FileId) %d' %(nNST)
    strTmp='  -       OK     OK:% 14d File copied, then renamed to origin %20s    -        -' %(nNST,strTmpA);   StrScreen.append(strTmp)

    n=nMatchingStrName
    strTmp='  -       OK     - :% 14d Deleted+recreated                          -        -    % 7d % 7d' %(n,n,n);  StrScreen.append(strTmp)

    n=nMatchingId
    strTmp='  OK      -      - :% 14d Reused id (or renamed and changed)         -        -    % 7d % 7d' %(n,n,n);   StrScreen.append(strTmp)

    #strTmp='Copy                                -      -     OK : %d' %(-1);   StrScreen.append(strTmp)

    strTmpA='%d/%d' %(nSourceRem, nTargetRem)
    strTmp='  -       -      - :% 14s Created/Deleted                            -        -    % 7d % 7d' %(strTmpA, nTargetRem, nSourceRem); StrScreen.append(strTmp)

    strTmpA='%d/%d' %(nSource, nTarget)
    nShortCut=nMetaMatch+nNST; #strTmpB=str(nShortCut).ljust(10)
    nTmp=nChanged+nMatchingStrName+nMatchingId; nDeleteTmp=nTmp+nTargetRem; nWriteTmp=nTmp+nSourceRem
    #strTmpC='Del:%d / Write:%d' %(nDeleteTmp, nWriteTmp)
    strTmp='                Sum:% 14s % 45d % 10d % 7d % 7d' %(strTmpA, nUnTouched, nShortCut, nDeleteTmp, nWriteTmp);    StrScreen.append(strTmp);   #StrResultMore.append('\n'+strTmp)

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
    return StrScreen

  def formatRenameOTO(self):
    strIdType=self.strIdType
    nMetaMatch=len(self.arrSourceMetaMatch)
    StrRenameOTO=[]
    if(nMetaMatch>0):
      def funMatch(s,t):
        return '  MatchingData %s %10d %19d' %(s[strIdType], s["size"], s["mtime_ns64Round"])
      def funUnique(s):
        mtime_ns64=s["mtime_ns64"]
        d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
        return '    %s%s' %(s["strName"], strD)
      # StrTmp=formatMatchingData(self.arrSourceMetaMatch, self.arrTargetMetaMatch, funMatch, funUnique)
      # StrRenameOTO.extend(StrTmp)

        # Sort by strName
      for i, rowS in enumerate(self.arrSourceMetaMatch): rowS["ind"]=i
      arrStmp=sorted(self.arrSourceMetaMatch, key=lambda x: x["strName"])
        # Create Ind
      Ind=[None]*nMetaMatch
      for i, rowS in enumerate(arrStmp): Ind[i]=rowS["ind"] 
      arrTtmp=eInd(self.arrTargetMetaMatch, Ind)
      StrTmp=formatMatchingData(arrStmp, arrTtmp, funMatch, funUnique)
      if(len(StrTmp)): StrRenameOTO.append("# Rename (MetaMatch) one-to-one match of id, size and time")
      StrRenameOTO.extend(StrTmp)
    return StrRenameOTO

  def formatResultMore(self):
    strIdType=self.strIdType
    strIdTypeL='FileId' if(strIdType=='ino') else strIdType  #"L" for Long (inode instead of ino)
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nChanged=len(self.arrSourceChanged)
    nMetaMatch=len(self.arrSourceMetaMatch)
    nNST=len(self.arrSourceNST)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nMatchingId=len(self.arrSourceMatchingId)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)

      # Return empty result if nothing to report
    #nTmp=nChanged+nMetaMatch+nNST+nMatchingStrName+nMatchingId+nSourceRem+nTargetRem
    nTmp=nChanged+nNST+nMatchingStrName+nMatchingId+nSourceRem+nTargetRem
    if(nTmp==0): return []

    StrResultMore=[]
    StrResultMore.append("Result from running %s" %(self.strCommandName))


    #strTmp='Untouched: Matching: (%s, strName, ST): %d' %(strIdTypeL, nUnTouched);    StrResultMore.append('\n'+strTmp)
    
    strTmp='Changed: Matching: (%s, strName, - ): %d' %(strIdTypeL, nChanged);    StrResultMore.append('\n'+strTmp)
    if(nChanged>0):
      funMatch=lambda s,t: '  MatchingData %s %s' %(s[strIdType],s["strName"]);
      funUnique=lambda s: '    %10d %10d' %(s["size"],s["mtime_ns64"])
      arrData=formatMatchingData(self.arrSourceChanged, self.arrTargetChanged, funMatch, funUnique)
      StrResultMore.extend(arrData)

    #strTmp='Renamed: Matching: (%s,    -   , ST): %d' %(strIdTypeL, nMetaMatch); StrResultMore.append('\n'+strTmp)

    strTmp='File copied, then renamed to origin: Matching: ( -, strName, ST): %d' %(nNST);   StrResultMore.append('\n'+strTmp)
    if(nNST>0):
      def funMatch(s,t):
        return '  MatchingData %10d %19d %s' %(s["size"], s["mtime_ns64Round"], s["strName"])
      def funUnique(s):
        mtime_ns64=s["mtime_ns64"]
        d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
        return '    %s%s' %(s[strIdType], strD)
      arrData=formatMatchingData(self.arrSourceNST, self.arrTargetNST, funMatch, funUnique)
      StrResultMore.extend(arrData)

    strTmp='Deleted+recreated: Matching: ( - , strName, - ): %d' %(nMatchingStrName);  StrResultMore.append('\n'+strTmp)
    if(nMatchingStrName>0):
      funMatch=lambda s,t: '  MatchingData %s' %(s['strName']);
      funUnique=lambda s: '    %s %10d %10d' %(s[strIdType],s["size"],s["mtime_ns64"])
      arrData=formatMatchingData(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, funMatch, funUnique)
      StrResultMore.extend(arrData)

    strTmp='Reused id (or renamed and changed): Matching: (%s,    -   , - ): %d' %(strIdTypeL, nMatchingId);   StrResultMore.append('\n'+strTmp)
    if(nMatchingId>0):
      funMatch=lambda s,t: '  MatchingData %s' %(s[strIdType]);
      funUnique=lambda s: '    %10d %10d %s' %(s["size"], s["mtime_ns64"], s["strName"])
      arrData=formatMatchingData(self.arrSourceMatchingId, self.arrTargetMatchingId, funMatch, funUnique)
      StrResultMore.extend(arrData)

    #strTmp='WO any matching: %d/%d (source(created)/target(deleted))' %(nSourceRem, nTargetRem); StrResultMore.append('\n'+strTmp);

    strTmp='Created: %d' %(nSourceRem); StrResultMore.append('\n'+strTmp)
    if(nSourceRem>0):
      for i, row in enumerate(self.arrSourceRem): StrResultMore.append('%s %10d %10d %s' %(row[strIdType], row["size"], row["mtime_ns64"], row["strName"]))
    strTmp='Deleted: %d' %(nTargetRem); StrResultMore.append('\n'+strTmp)
    if(nTargetRem>0):
      for i, row in enumerate(self.arrTargetRem): StrResultMore.append('%s %10d %10d %s' %(row[strIdType], row["size"], row["mtime_ns64"], row["strName"]))

    return StrResultMore

  def format(self):
    StrSum=self.formatScreen()
    self.myReporter.Str["screen"]=StrSum
    self.myReporter.Str["T2M_sum"]=StrSum
    self.myReporter.Str["T2M_resultMore"]=self.formatResultMore()
    self.myReporter.Str["T2M_renameOTO"]=self.formatRenameOTO()
    self.myReporter.Str["T2M_HL"]=[]
    

  def getCategoryArrays(self):
    arrSourceUnTouched=self.arrSourceUnTouched; arrTargetUnTouched=self.arrTargetUnTouched
    arrSourceChanged=self.arrSourceChanged; arrTargetChanged=self.arrTargetChanged
    arrSourceMetaMatch=self.arrSourceMetaMatch; arrTargetMetaMatch=self.arrTargetMetaMatch
    arrSourceNST=self.arrSourceNST; arrTargetNST=self.arrTargetNST
    arrSourceMatchingStrName=self.arrSourceMatchingStrName; arrTargetMatchingStrName=self.arrTargetMatchingStrName
    arrSourceMatchingId=self.arrSourceMatchingId; arrTargetMatchingId=self.arrTargetMatchingId
    arrSourceRem=self.arrSourceRem; arrTargetRem=self.arrTargetRem
    return [arrSourceUnTouched, arrTargetUnTouched, arrSourceChanged, arrTargetChanged, arrSourceMetaMatch, arrTargetMetaMatch, arrSourceNST, arrTargetNST, arrSourceMatchingStrName, arrTargetMatchingStrName, arrSourceMatchingId, arrTargetMatchingId, arrSourceRem, arrTargetRem]




class ComparisonWOID:
  def __init__(self, arrSource, arrTarget, strCommandName, myReporter):
    self.arrSource=arrSource; self.arrTarget=arrTarget
    self.strCommandName=strCommandName; self.myReporter=myReporter
  
  def compare(self):
    arrSource=self.arrSource; arrTarget=self.arrTarget
        # Untouched
    arrSource.sort(key=lambda x: x["strName"]);   arrTarget.sort(key=lambda x: x["strName"])
    #arrA, arrB, arrSourceTouched, arrTargetTouched=extractMatching(arrSource, arrTarget, ['strName', 'size', 'mtime_ns64Round'])
    arrA, arrB, arrSourceTouched, arrTargetTouched=extractMatching(arrSource, arrTarget, ['strName', 'st'])
    self.arrSourceUnTouched=arrA; self.arrTargetUnTouched=arrB

        # Rename (MetaMatch)
    arrSourceTouched.sort(key=lambda x:(x["size"], x["mtime_ns64Round"]));   arrTargetTouched.sort(key=lambda x:(x["size"], x["mtime_ns64Round"]))

    #def funST(rowA): return str(rowA["size"])+str(rowA["mtime_ns64"])
    def funST(rowA): return rowA["st"]
    objSourceMetaMatch, objTargetMetaMatch=extractMatchingManyToManyF(arrSourceTouched, arrTargetTouched, funST)

      # Calculate Mat(Ini)
    MatIni=convertObjManyToManyToMat(objSourceMetaMatch, objTargetMetaMatch)
    self.MatIni=MatIni

      # Create collections (obj/arr) of files only renamed in ancestor. (Just noting down renamed ancestor would be enough (only the keys(2-dim) of objAncestorOnlyRenamed are used)) 
    nAncestorOnlyRenamed, objAncestorOnlyRenamed=summarizeAncestorOnlyRename(MatIni.arrAOTO, MatIni.arrBOTO)  #, arrSourceLeafRenamed, arrTargetLeafRenamed
    arrAncestorOnlyRenamed=convertObjAncestorOnlyRenamedToArr(objAncestorOnlyRenamed, ['s', 't'])
    arrAncestorOnlyRenamed.sort(key=lambda x: -x["n"]);   arrAncestorOnlyRenamed.sort(key=lambda x: -x["lev"])
    self.arrAncestorOnlyRenamed=arrAncestorOnlyRenamed;   self.nAncestorOnlyRenamed=nAncestorOnlyRenamed

      # Extract files Idd by ancestor folder from duplicates
    arrSourceIddByFolder, arrTargetIddByFolder, objSourceMetaMatchWExtraIDing, objTargetMetaMatchWExtraIDing=extractExtraByFolder(objSourceMetaMatch, objTargetMetaMatch, objAncestorOnlyRenamed)
    self.arrSourceIddByFolder=arrSourceIddByFolder; self.arrTargetIddByFolder=arrTargetIddByFolder

      # Recalculate Mat(Fin)
    objManyToManyRemoveEmpty(objSourceMetaMatchWExtraIDing, objTargetMetaMatchWExtraIDing)  # Modifies the arguments
    MatFin=convertObjManyToManyToMat(objSourceMetaMatchWExtraIDing, objTargetMetaMatchWExtraIDing)
    self.MatFin=MatFin


      # Changed (NoMetaMatch with matching strName)
    arrSourceNoMetaMatch=sorted(MatFin.arrARem, key=lambda x: x["strName"]);   arrTargetNoMetaMatch=sorted(MatFin.arrBRem, key=lambda x: x["strName"])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceNoMetaMatch, arrTargetNoMetaMatch, ['strName'])
    self.arrSourceMatchingStrName=arrA; self.arrTargetMatchingStrName=arrB

    #arrCreate, arrDelete = arrSourceRem, arrTargetRem
    self.arrSourceRem=arrSourceRem; self.arrTargetRem=arrTargetRem

  def formatScreen(self):
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)
    MatIni=self.MatIni; MatFin=self.MatFin
    nIddByFolder=len(self.arrSourceIddByFolder)

    StrScreen=[]; 

    strTmp='Files in Source/Target: %d/%d' %(nSource, nTarget);    StrScreen.append(strTmp);   #StrResultMore.append('\n'+strTmp)
    strTmp='Untouched: Matching: (strName and ST (ST=size and time)): %d' %(nUnTouched);    StrScreen.append(strTmp);   #StrResultMore.append('\n'+strTmp)

    strTmp="Identification table: nPattern(nFileS\\nFileT) (after the untouched files are removed))";   StrScreen.append(strTmp)
    StrScreen.append(self.strIni);   #StrResultMore.append('\n'+strTmp); StrResultMore.append(self.strIni)

    StrTmp=[]
    StrTmp.append('OTO files only renamed in folder: %d. (%d folders)' %(self.nAncestorOnlyRenamed, len(self.arrAncestorOnlyRenamed)));
    StrScreen.extend(StrTmp);    #StrResultMore.extend([""]+StrTmp)

    if(nIddByFolder):
      StrTmp=[]
      StrTmp.append('%d files can be futher be identified by looking at renamed folders.' %(nIddByFolder));
      lenOTO=len(MatFin.ArrAOTO);   lenOTM=len(MatFin.ArrAOTM);   lenMTO=len(MatFin.ArrAMTO);   lenMTM=len(MatFin.ArrAMTM)
      StrScreen.extend(StrTmp);    #StrResultMore.extend([""]+StrTmp)

      strTmp="""Modified identification table after recategorizing files identified via renamed folders:""";   StrScreen.append(strTmp)
      StrScreen.append(self.strFin);   #StrResultMore.append('\n'+strTmp); StrResultMore.append(self.strFin)

    strDupExtra=" (others may be found among those with duplicate ST)" if(self.nArrADup) else ""
    strTmp='Changed: Matching: (strName): %d%s' %(nMatchingStrName, strDupExtra);  StrScreen.append(strTmp)

    strTmp='Created: %d%s' %(nSourceRem, strDupExtra); StrScreen.append(strTmp)
    strTmp='Deleted: %d%s' %(nTargetRem, strDupExtra); StrScreen.append(strTmp)
    return StrScreen

  def formatResultMore(self):
    nMatchingStrName=len(self.arrSourceMatchingStrName);  nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)

      # Return empty result if nothing to report
    nTmp=nMatchingStrName+nSourceRem+nTargetRem
    if(nTmp==0): return []

    StrResultMore=[]
    StrResultMore.append("Result from running %s" %(self.strCommandName))

    strDupExtra=" (others may be found among those with duplicate ST)" if(self.nArrADup) else ""
    strTmp='Changed: Matching: (strName): %d%s' %(nMatchingStrName, strDupExtra);  StrResultMore.append('\n'+strTmp)
    if(nMatchingStrName>0):
      funMatch=lambda s,t: '  MatchingData %s' %s["strName"];
      funUnique=lambda s: '    %10d %10d' %(s["size"],s["mtime_ns64"])
      arrData=formatMatchingData(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, funMatch, funUnique)
      StrResultMore.extend(arrData)

    strTmp='Created: %d%s' %(nSourceRem, strDupExtra); StrResultMore.append('\n'+strTmp)
    if(nSourceRem>0):
      for i, row in enumerate(self.arrSourceRem): StrResultMore.append('%10d %10d %s' %(row["size"], row["mtime_ns64"], row["strName"]))
    strTmp='Deleted: %d%s' %(nTargetRem, strDupExtra); StrResultMore.append('\n'+strTmp)
    if(nTargetRem>0):
      for i, row in enumerate(self.arrTargetRem): StrResultMore.append('%10d %10d %s' %(row["size"], row["mtime_ns64"], row["strName"]))
    return StrResultMore

  def formatRenameOTO(self):
    MatFin=self.MatFin

    StrRenameOTO=[]
    def funMatch(s,t):
      return '  MatchingData %10d %19d' %(s["size"], s["mtime_ns64Round"])
    def funUnique(s):
      mtime_ns64=s["mtime_ns64"]
      d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
      return '    %s%s' %(s["strName"], strD)

    # StrTmp=formatMatchingData(MatFin.arrAOTO, MatFin.arrBOTO, funMatch, funUnique)


      # Sort by strName
    for i, rowS in enumerate(MatFin.arrAOTO): rowS["ind"]=i
    arrStmp=sorted(MatFin.arrAOTO, key=lambda x: x["strName"])
      # Create Ind
    Ind=[None]*len(MatFin.arrAOTO)
    for i, rowS in enumerate(arrStmp): Ind[i]=rowS["ind"] 
    arrTtmp=eInd(MatFin.arrBOTO, Ind)
    StrTmp=formatMatchingData(arrStmp, arrTtmp, funMatch, funUnique)
    if(len(StrTmp)): StrRenameOTO.append("# Rename (MetaMatch) one-to-one match of size and time")
    StrRenameOTO.extend(StrTmp)
    return StrRenameOTO

  def format(self, fsDir, fiMeta):
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)
    MatIni=self.MatIni; MatFin=self.MatFin
    nIddByFolder=len(self.arrSourceIddByFolder)

    StrScreen=[]; StrResultMore=[]; StrRenameOTO=[]

    self.strIni=formatMatrix(MatIni)
    ArrADup=MatIni.ArrAOTM+MatIni.ArrAMTO+MatIni.ArrAMTM; ArrBDup=MatIni.ArrBOTM+MatIni.ArrBMTO+MatIni.ArrBMTM
    markRelBest(ArrADup, ArrBDup)
    #StrDuplicateInitial=formatMatchingDataWDupOld(ArrADup, ArrBDup, False)
    def funMatch(s,t):
      return '  MatchingData %10d %19d' %(s["size"], s["mtime_ns64Round"])
    def funUnique(s):
      mtime_ns64=s["mtime_ns64"]
      d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
      return '    %s%s' %(s["strName"], strD)
    def funUniqueC(s):
      mtime_ns64=s["mtime_ns64"]
      d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
      return '    #%s%s' %(s["strName"], strD)
    StrDuplicateInitial=formatMatchingDataWDup(ArrADup, ArrBDup, funMatch, funUnique, funUniqueC)


    lenOTO=len(MatIni.ArrAOTO);   lenOTM=len(MatIni.ArrAOTM);   lenMTO=len(MatIni.ArrAMTO);   lenMTM=len(MatIni.ArrAMTM)

      # Leaf- vs Parent- changes 
    StrRenameAncestorOnly, StrRenameAncestorOnlyMv, StrRenameAncestorOnlySed=formatAncestorOnlyRenamed(self.arrAncestorOnlyRenamed, fiMeta, ["t", "s"])


    self.strFin=formatMatrix(MatFin, nIddByFolder)
    ArrADup=MatFin.ArrAOTM+MatFin.ArrAMTO+MatFin.ArrAMTM; ArrBDup=MatFin.ArrBOTM+MatFin.ArrBMTO+MatFin.ArrBMTM
    self.nArrADup=len(ArrADup)
    markRelBest(ArrADup, ArrBDup)
    #StrDuplicateFinal=formatMatchingDataWDupOld(ArrADup, ArrBDup, False)
    def funMatch(s,t):
      return '  MatchingData %10d %19d' %(s["size"], s["mtime_ns64Round"])
    def funUnique(s):
      mtime_ns64=s["mtime_ns64"]
      d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
      return '    %s%s' %(s["strName"], strD)
    def funUniqueC(s):
      mtime_ns64=s["mtime_ns64"]
      d=mtime_ns64-s["mtime_ns64Round"]; strD='\n#(%d)' % mtime_ns64 if(d) else ''
      return '    #%s%s' %(s["strName"], strD)
    StrDuplicateFinal=formatMatchingDataWDup(ArrADup, ArrBDup, funMatch, funUnique, funUniqueC)

    StrRenameAdditional=formatMatchingData(self.arrSourceIddByFolder, self.arrTargetIddByFolder, funMatch, funUnique)


    StrSum=self.formatScreen()
    StrResultMore=self.formatResultMore()
    StrRenameOTO=self.formatRenameOTO()

    self.myReporter.Str["screen"]=StrSum
    self.myReporter.Str["T2T_sum"]=StrSum
    self.myReporter.Str["T2T_resultMore"]=StrResultMore
    self.myReporter.Str["T2T_renameOTO"]=StrRenameOTO
    self.myReporter.Str["T2T_ancestrallyOTORenamedAncestor"]=StrRenameAncestorOnly
    self.myReporter.Str["T2T_renameDuplicateInitial"]=StrDuplicateInitial
    self.myReporter.Str["T2T_renameDuplicateFinal"]=StrDuplicateFinal
    self.myReporter.Str["T2T_renameAdditional"]=StrRenameAdditional
    
