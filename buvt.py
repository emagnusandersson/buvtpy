#!/usr/bin/env python


#
# For variable naming convention see https://emagnusandersson.com/prefixes_to_variables
#

# Typical debug session
# python -m pdb scannedBook.py --boTest 1
# b 130   # set breakpoint
# b       # list breakpoints
# cl 1    # clear breakpoint
# run     # run
# c       # continue
# n       # next
# s       # step down
# r       # continue till function returns
# l       # list surronding

# export PATH=$PATH:~/progPython/bin
# ln -s ~/progPython/scannedBook/scannedBook.py ~/progPython/bin/scannedBook.py

# Go to /run/media/magnus/myPassport/books/
# Execute:
#   scannedBook.py

# python -m pdb ./buvt.py
# python -m pdb ~/progPython/buvt/buvt.py


# mbuTool scan      # Create NEWMETA and NEWMETAF
# mbuTool suggestRenameTS -d DIR_BU [-nm NEWMETA]      # Create RENAMESUGGESTION using ts-matching
# mbuTool suggestRenameI -om OLDMETA [-nm NEWMETA]     # Create RENAMESUGGESTION using inode-matching
# mbuTool suggestRenameF -om OLDMETAF [-nm NEWMETAF]   # Create RENAMESUGGESTIONF using inode-matching
# mbuTool renameF   # Rename according to RENAMESUGGESTIONF
# mbuTool renameComplete    # Rename according to RENAMESUGGESTION

#python can one increase performance by predeclaring the length of arrays and lists
# rsync -rtvPiFn --delete ~/ /empty > outR.txt
# rsync -rtvPiF --delete Source/ Target/
# rsync -rtvPiFn --delete Source/ /empty > outR.txt

#^(?!cd|>f)
#^.*? 
#/$
#sort outR.txt > outRSorted.txt
#sort toBeRenamed.txt > renameFileArgSorted.txt


# Rename arrDBSMetaMatch to arrDBSMatchingIDST

# buvt deleteResultFiles





# WOId
#          Source                                                                                                           Target
#
#            ⑃        compareTreeToTree, syncTreeToTreeBrutal, renameFinishToTree, renameFinishToTreeByFolder ⇢               ⑃
#
#           compareTreeToST, syncTreeToHashcodeFileBrutal, renameFinishToHashcodeFile, renameFinishToHashcodeFileByFolder
#            ⇣                                                                                                                ⇣
#       buvt-meta.txt                                                                                                     buvt-meta.txt




# WId (inode)
#          Source                                                                                                            Target
#                           
#            ⑃                                      renameFinishToTree ⇢                                                        ⑃
#                                                                      
#  compareTreeToMeta, syncTreeToMeta, renameFinishToMeta
#            ⇣                                                                                                                 ⇣
#       buvt-meta.txt                                                                                                     buvt-meta.txt
#                                                    ─┬─
#                                                    ─┴ moveMeta ⇢

#   On ~
# syncTreeToMeta    (or compareTreeToMeta + renameFinishToMeta)
#
# compareTreeToTree, (renameFinishToTree (OTO), renameFinishToTree (Additional) ...)    (or renameFinishToTree)  
# syncTreeToTreeBrutal
#
# moveMeta
#
#   On myPassport
# syncTreeToMeta
#
# compareTreeToMeta
#
# compareTreeToTree, (renameFinishToTree (OTO), renameFinishToTree (Additional) ...)  
# syncTreeToTreeBrutal
#
# compareTreeToST




from distutils.log import debug
import math
import os
import argparse
import time
import re
import sys
from glob import glob
from os.path import relpath
from importlib import import_module
from operator import itemgetter
import enum
import subprocess
from lib import *
from libApp import *
from libExtractMatching import *
from pathlib import Path
import uuid
import tempfile
import copy
import errno
import traceback
from types import SimpleNamespace
import shutil



class KeyST:
  def __init__(self, s, t, charTimeAccuracy):
    self.t=t
    self.s=s
    if(charTimeAccuracy=='s'):   div=1000000000
    elif(charTimeAccuracy=='m'): div=1000000
    elif(charTimeAccuracy=='u'): div=1000
    elif(charTimeAccuracy=='n'): div=1
    self.tRound=(t//div)*div
  def __eq__(self, other):
    return ((self.s, self.tRound) == (other.s, other.tRound))
  def __lt__(self, other):
    return ((self.s, self.tRound) < (other.s, other.tRound))
  def __gt__(self, other):
    return ((self.s, self.tRound) > (other.s, other.tRound))
  def __str__(self):
    return str(self.s)+'_'+str(self.tRound)

class KeyHST:
  def __init__(self, hash, s, t, charTimeAccuracy):
    self.hash=hash
    self.t=t
    self.s=s
    if(charTimeAccuracy=='s'):   div=1000000000
    elif(charTimeAccuracy=='m'): div=1000000
    elif(charTimeAccuracy=='u'): div=1000
    elif(charTimeAccuracy=='n'): div=1
    self.tRound=(t//div)*div
  def __eq__(self, other):
    return ((self.hash, self.s, self.tRound) == (other.hash, other.s, other.tRound))
  def __lt__(self, other):
    return ((self.hash, self.s, self.tRound) < (other.hash, other.s, other.tRound))
  def __gt__(self, other):
    return ((self.hash, self.s, self.tRound) > (other.hash, other.s, other.tRound))
  def __str__(self):
    return str(self.hash)+'_'+str(self.s)+'_'+str(self.tRound)

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

    def funST(rowA): return str(rowA["size"])+str(rowA["mtime"])
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

    StrRenameAdditional=formatMatchingData(self.arrSourceIddByFolder, self.arrTargetIddByFolder, ['size', 'mtime'], ['strName'], '  MatchingData %10d %20d', '    %s')


      # Format OTO
    StrTmp=formatMatchingData(MatFin.arrAOTO, MatFin.arrBOTO, ['size', 'mtime'], ['strName'], '  MatchingData %10d %20d', '    %s')
    if(len(StrTmp)): StrRenameOTO.append("# Rename (MetaMatch) one-to-one match of size and time")
    StrRenameOTO.extend(StrTmp)

    StrResultFile.append("Result from running %s" %(strCommandName))

    strTmp='Files in Source/Target: %d/%d' %(nSource, nTarget);    StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
    strTmp='Untouched (Matching strName and ST (ST=size and time)): %d' %(nUnTouched);    StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)

    strTmp="Identification table: (after matching ST)";   StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
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
    arrData=formatMatchingData(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, ['strName'], ['size', 'mtime'], '  MatchingData %s', '    %10d %10d')
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

        # Matching id
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, [strIdType])
    self.arrSourceMatchingId=arrA; self.arrTargetMatchingId=arrB

        # Matching strName
    arrSourceRem=sorted(arrSourceRem, key=lambda x: x["strName"]);   arrTargetRem=sorted(arrTargetRem, key=lambda x: x["strName"])
    arrA, arrB, arrSourceRem, arrTargetRem=extractMatching(arrSourceRem, arrTargetRem, ['strName']) 
    self.arrSourceMatchingStrName=arrA; self.arrTargetMatchingStrName=arrB

        # Matching ST (Copy)
    #arrSourceRem=sorted(arrSourceRem, key=lambda x:(x["size"], x["mtime"]));   arrTargetRem=sorted(arrTargetRem, key=lambda x:(x["size"], x["mtime"]))
    #def funST(rowA): return str(rowA["size"])+str(rowA["mtime"])
    #objSourceMetaMatch, objTargetMetaMatch=extractMatchingManyToManyF(arrSourceRem, arrTargetRem, funST)

    self.arrSourceRem=arrSourceRem; self.arrTargetRem=arrTargetRem


  def format(self, strCommandName, fsDir, fiMeta):
    strIdType=self.strIdType
    nSource=len(self.arrSource); nTarget=len(self.arrTarget)
    nUnTouched=len(self.arrSourceUnTouched)
    nChanged=len(self.arrSourceChanged)
    nMetaMatch=len(self.arrSourceMetaMatch)
    nNST=len(self.arrSourceNST)
    nMatchingId=len(self.arrSourceMatchingId)
    nMatchingStrName=len(self.arrSourceMatchingStrName)
    nSourceRem=len(self.arrSourceRem);  nTargetRem=len(self.arrTargetRem)

      # Format info data
    StrScreen=[]; StrResultFile=[]; StrRenameOTO=[]; StrDuplicateInitial=[]; StrDuplicateFinal=[]; StrRenameAdditional=[]
    StrResultFile.append("Result from running %s" %(strCommandName))

    strTmp='Files in Source/Target: %d/%d' %(nSource, nTarget);    StrScreen.append(strTmp);   StrResultFile.append('\n'+strTmp)
    strTmp='                                  Matching meta data';    StrScreen.append(strTmp)
    strTmp='    Categorized as:                %s, strName, ST' %(strIdType);    StrScreen.append(strTmp)
    strTmp='Untouched                           ✔️      ✔️     ✔️ : %d' %(nUnTouched);    StrScreen.append(strTmp);
    strTmp='Untouched: (Matching: %s, strName, ST): %d' %(strIdType, nUnTouched);    StrResultFile.append('\n'+strTmp)
    
    strTmp='Changed                             ✔️      ✔️     - : %d' %(nChanged);    StrScreen.append(strTmp)
    strTmp='Changed: (Matching: %s, strName, - ): %d' %(strIdType, nChanged);    StrResultFile.append('\n'+strTmp)
    arrData=formatMatchingData(self.arrSourceChanged, self.arrTargetChanged, [strIdType, "strName"], ['size', 'mtime'], '  MatchingData %s %s', '    %10d %20d')
    StrResultFile.extend(arrData)

    strTmp='Renamed                             ✔️      -     ✔️ : %d' %(nMetaMatch);   StrScreen.append(strTmp)
    strTmp='Renamed: (Matching: %s,    -   , ST): %d' %(strIdType, nMetaMatch);   StrResultFile.append('\n'+strTmp)
    #strTmp='  Leafs: %d' %(len(arrSourceLeafRenamed));   StrScreen.append(strTmp);   StrResultFile.append(strTmp)
    #StrRenameOTO.append("#All except duplicates")
    StrTmp=formatMatchingData(self.arrSourceMetaMatch, self.arrTargetMetaMatch, [strIdType, 'size', 'mtime'], ["strName"], '  MatchingData %s %10d %20d', '    %s')
    StrRenameOTO.extend(StrTmp)

    StrRenameAncestorOnly, StrRenameAncestorOnlyMv, StrRenameAncestorOnlySed=formatAncestorOnlyRenamed(self.arrAncestorOnlyRenamed, fiMeta, ["t", "s"])
    StrRenameAncestorOnlyCmd=StrRenameAncestorOnlyMv + StrRenameAncestorOnlySed
    if(len(StrRenameAncestorOnlyCmd)):StrRenameAncestorOnlyCmd=["cd "+fsDir]+StrRenameAncestorOnlyCmd

    strTmp='File copied, then renamed to origin -      ✔️     ✔️ : %d' %(nNST);   StrScreen.append(strTmp)
    strTmp='File copied, then renamed to origin: (Matching:  -, strName, ST): %d' %(nNST);   StrResultFile.append('\n'+strTmp)
    arrData=formatMatchingData(self.arrSourceNST, self.arrTargetNST, ["strName", 'size', 'mtime'], [strIdType], '  MatchingData %s %10d %20d', '    %s')
    StrResultFile.extend(arrData)

    strTmp='Reused id (or renamed and changed)  ✔️      -     - : %d' %(nMatchingId);   StrScreen.append(strTmp)
    strTmp='Reused id (or renamed and changed): (Matching: %s,    -   , - ): %d' %(strIdType, nMatchingId);   StrResultFile.append('\n'+strTmp)
    arrData=formatMatchingData(self.arrSourceMatchingId, self.arrTargetMatchingId, [strIdType], ['size', 'mtime', "strName"], '  MatchingData %s', '    %10d %10d %s')
    StrResultFile.extend(arrData)

    strTmp='Deleted+recreated                   -      ✔️     - : %d' %(nMatchingStrName);  StrScreen.append(strTmp)
    strTmp='Deleted+recreated: (Matching:  - , strName, - ): %d' %(nMatchingStrName);  StrResultFile.append('\n'+strTmp)
    arrData=formatMatchingData(self.arrSourceMatchingStrName, self.arrTargetMatchingStrName, ['strName'], [strIdType, 'size', 'mtime'], '  MatchingData %s', '    %s %10d %10d')
    StrResultFile.extend(arrData)

    #strTmp='Copy                                -      -     ✔️ : %d' %(-1);   StrScreen.append(strTmp)

    strTmp='Created/Deleted (source/target)     -      -     - : %d/%d' %(nSourceRem, nTargetRem); StrScreen.append(strTmp);
    #strTmp='WO any matching: %d/%d (source(created)/target(deleted))' %(nSourceRem, nTargetRem); StrResultFile.append('\n'+strTmp);
    strTmp='Created: %d' %(nSourceRem); StrResultFile.append('\n'+strTmp)
    for i, row in enumerate(self.arrSourceRem): StrResultFile.append('%s %10d %10d %s' %(row[strIdType], row["size"], row["mtime"], row["strName"]))
    strTmp='Deleted: %d' %(nTargetRem); StrResultFile.append('\n'+strTmp)
    for i, row in enumerate(self.arrTargetRem): StrResultFile.append('%s %10d %10d %s' %(row[strIdType], row["size"], row["mtime"], row["strName"]))
    
    nSomeKindOfMatching=nUnTouched+nChanged+nMetaMatch+nNST+nMatchingId+nMatchingStrName
    nSourceCheck=nSomeKindOfMatching+nSourceRem; nTargetCheck=nSomeKindOfMatching+nTargetRem
          # Checking the sums
    boSourceOK=nSource==nSourceCheck; boTargetOK=nTarget==nTargetCheck
    boBoth=boSourceOK and boTargetOK
    strOK="OK"; strNOK="NOK" # strOK="✔️"; strNOK="✗"
    strNSourceMatch=strOK if(boSourceOK) else strNOK; strNTargetMatch=strOK if(boTargetOK) else strNOK

    if(boBoth): strCheck="OK (matching the numbers of files in source/target (seen above))"
    else: strCheck="Source: %d (%s), Target: %d (%s) (when comparing to the number of files in source/target (seen above)" %(nSourceCheck, strNSourceMatch, nTargetCheck, strNTargetMatch)
    strTmp='                Checking the sums of the categories: %s' %(strCheck);   StrScreen.append(strTmp)

    if(not boSourceOK or not boTargetOK):
      strTmp='!!ERROR the sums does not match with the number of files';  StrScreen.append(strTmp)
    


    return [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd]

  def getCategoryArrays(self):
    arrSourceUnTouched=self.arrSourceUnTouched; arrTargetUnTouched=self.arrTargetUnTouched
    arrSourceChanged=self.arrSourceChanged; arrTargetChanged=self.arrTargetChanged
    arrSourceMetaMatch=self.arrSourceMetaMatch; arrTargetMetaMatch=self.arrTargetMetaMatch
    arrSourceNST=self.arrSourceNST; arrTargetNST=self.arrTargetNST
    arrSourceMatchingId=self.arrSourceMatchingId; arrTargetMatchingId=self.arrTargetMatchingId
    arrSourceMatchingStrName=self.arrSourceMatchingStrName; arrTargetMatchingStrName=self.arrTargetMatchingStrName
    arrSourceRem=self.arrSourceRem; arrTargetRem=self.arrTargetRem
    return [arrSourceUnTouched, arrTargetUnTouched, arrSourceChanged, arrTargetChanged, arrSourceMetaMatch, arrTargetMetaMatch, arrSourceNST, arrTargetNST, arrSourceMatchingId, arrTargetMatchingId, arrSourceMatchingStrName, arrTargetMatchingStrName, arrSourceRem, arrTargetRem]




boAskBeforeWrite=True

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
# getBranch
#######################################################################################
def getBranch(arrf, arrF, objDir, intLevel, dictRule, leafFilterLoc, boUseFilter=False):
  #global arrRulef, arrRuleF
  fsDir=objDir["fsDir"]
  flDir=objDir["flDir"]
  arrRulef=dictRule["arrRulef"]
  arrRuleF=dictRule["arrRuleF"]
  nNewf=0; nNewF=0

    # Add potetial filter rules
  if(boUseFilter):
    boFoundFilterFile=True
    try: fi=open(fsDir+'/'+leafFilterLoc,'r')
    except FileNotFoundError: boFoundFilterFile=False
    if(boFoundFilterFile):
      strDataFilter=fi.read()
      fi.close()
      #iStartOfRuleFileRootInFlName=len(longnameFold)+1
      if(flDir): iStartOfRuleFileRootInFlName=len(flDir)+1
      else: iStartOfRuleFileRootInFlName=0
      err, arrRulefT, arrRuleFT=parseFilter(strDataFilter, intLevel, iStartOfRuleFileRootInFlName)
      if(err): print(err["strTrace"]); return
      nNewf=len(arrRulefT)
      nNewF=len(arrRuleFT)
      #arrRulef=arrRulefT+arrRulef
      #arrRuleF=arrRuleFT+arrRuleF
      arrRulef[0:0]=arrRulefT
      arrRuleF[0:0]=arrRuleFT
    
  it=os.scandir(fsDir)
  myListUnSorted=list(it)
  myList=sorted(myListUnSorted, key=lambda x: x.name)
  for entry in myList:
    boFile=entry.is_file()
    boFold=entry.is_dir()
    if(not boFile and not boFold): continue
    if(entry.is_symlink()): continue
    strName=entry.name
    #strName=longnameFold+'/'+strName
    if(flDir): flName=flDir+'/'+strName
    else: flName=strName
    fsName=fsDir+'/'+strName
    #if(flName=='progPython/bin/scannedBook.py'): breakpoint()
    #if(strName=='0Downloads'): breakpoint()
    #if(strName=='ignore'): breakpoint()
    boMatch=False
    boInc=True
    if(not boFold):
      for j, rule in enumerate(arrRulef):
        boMatch=rule.test(strName, flName, intLevel)
        if(boMatch): break
      if(boMatch): boInc=rule.boInc
      if(boInc):
        tmp=os.stat(fsName)
        ino=tmp.st_ino; mode=tmp.st_mode; mtime=tmp.st_mtime; mtime_ns=tmp.st_mtime_ns; size=tmp.st_size
        #myFile=MyFile(flName, ino, mtime, mtime_ns, size, 's')
        myFile={"strName":flName, "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns, "size":size, "keyST":KeyST(size, mtime_ns, 's')}
        arrf.append(myFile)
    else:
      for j, rule in enumerate(arrRuleF):
        boMatch=rule.test(strName, flName, intLevel)
        if(boMatch): break
      if(boMatch): boInc=rule.boInc
      if(boInc):
        tmp=os.stat(fsName)
        ino=tmp.st_ino; mtime=tmp.st_mtime; mtime_ns=tmp.st_mtime_ns
        #myFold=MyFold(flName, ino, mtime, mtime_ns)
        myFold={"strName":flName, "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns}
        #arrf.append(myFold)
        arrF.append(myFold)
        obj={"fsDir":fsName, "flDir":flName}
        getBranch(arrf, arrF, obj, intLevel+1, dictRule, leafFilter, boUseFilter) 
        
  #arrRulef=arrRulef[nNewf:]
  #arrRuleF=arrRuleF[nNewF:]
  del arrRulef[:nNewf]
  del arrRuleF[:nNewF]

def parseTree(fsDir, boUseFilter=False):
  arrSourcef=[]; arrSourceF=[]
  dictRule={"arrRulef":[], "arrRuleF":[]}
  getBranch(arrSourcef, arrSourceF, {"fsDir":fsDir, "flDir":""}, 0, dictRule, leafFilterFirst, boUseFilter)  #strName, ino, mtime, mtime_ns, size, keyST
  #for row in arrSourcef: row["mtime"]=math.floor(row["mtime"])  # Floor mtime
  return arrSourcef, arrSourceF

#arrSourcef, arrSourceF =parseTree(os.path.realpath(args.fiDir), True)  # Parse tree

# Matching:         match: NAME MTIME SIZE
# RenameCandidates: match:  -   MTIME SIZE
# NameMtime:        match: NAME MTIME  -
# NameSize:         match: NAME   -   SIZE
# Name:             match: NAME   -    -
# Mtime:            match:  -   MTIME  -
# Size:             match:  -     -   SIZE
# Rest:             match:  -     -    -


#######################################################################################
# extractDuplicateKey
#######################################################################################
def extractDuplicateKey(arr,arrKey):
  if(not isinstance(arrKey, list)): arrKey=[arrKey]
  objDup={};  arrUniqueInContainer=[];  arrUniqueWDubRep=[];
  lenArr=len(arr)
  if(lenArr==0): return arrUniqueWDubRep, arrUniqueInContainer, objDup
  boDict=isinstance(arr[0], dict)
  for i, row in enumerate(arr):
    iNext=i+1
    boMatch=True
    if(iNext!=lenArr):
      rowNext=arr[iNext]
      for key in arrKey:
        attr=row[key] if boDict else getattr(row, key)
        attrNext=rowNext[key] if boDict else getattr(rowNext, key)
        if(attrNext!=attr): boMatch=False
    else: boMatch=False
      # Create strAttr (key in objDup)
    strAttr=""
    for key in arrKey:
      attr=row[key] if boDict else getattr(row, key)
      strAttr+=str(attr)

    if(boMatch):
      if(strAttr in objDup): objDup[strAttr].append(row)
      else: objDup[strAttr]=[row]
    else:
      arrUniqueWDubRep.append(row)
      if(strAttr in objDup): objDup[strAttr].append(copy.copy(row))
      else: arrUniqueInContainer.append(row)

    # Adding the last row.
    #   If it had a duplicate, then it hasn't been added yet.
    #   If it's unique, then it should be added.
  # rowNext=arr[lenArr-1]
  # arrUniqueWDubRep.append(rowNext)  
  return arrUniqueWDubRep, arrUniqueInContainer, objDup

#arrUniqueWDubRep, arrUniqueInContainer, objDup= extractDuplicateKey([{"a":1}, {"a":1}, {"a":2}], "a")
  
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


#######################################################################################
# renameFiles (or folders)
#######################################################################################
def renameFiles(fsDir, arrRename): 
  arrTmpName=[]
  for row in arrRename:    # Rename to temporary names
    hex=uuid.uuid4().hex
    fsTmp=fsDir+'/'+row['strNew']+'_'+hex
    arrTmpName.append(fsTmp)
    fsOld=fsDir+'/'+row['strOld']
    fsPar=os.path.dirname(fsTmp);  boExist=os.path.exists(fsPar);  boIsDir=os.path.isdir(fsPar)
    if(boExist): 
      if(not boIsDir): return {"strTrace":myErrorStack("boExist and not boIsDir")}
    else: Path(fsPar).mkdir(parents=True, exist_ok=True)
    try: os.rename(fsOld, fsTmp)
    except FileNotFoundError as e:
      return {"e":e, "strTrace":myErrorStack(e.strerror)}    

  for i, row in enumerate(arrRename):    # Rename to final names
    fsTmp=arrTmpName[i]
    fsNew=fsDir+'/'+row['strNew']
    fsPar=os.path.dirname(fsNew);  boExist=os.path.exists(fsPar);  boIsDir=os.path.isdir(fsPar)
    if(boExist): 
      if(not boIsDir): return {"strTrace":myErrorStack("boExist and not boIsDir")}
    else: Path(fsPar).mkdir(parents=True, exist_ok=True)
    try: os.rename(fsTmp, fsNew)
    except FileNotFoundError as e:
      return {"e":e, "strTrace":myErrorStack(e.strerror)}   
  return None


   
def myRmFiles(arrTargetRem, fsDirTarget):
  if(len(arrTargetRem)):
    arr=['rm']
    for row in arrTargetRem:
      fsName=fsDirTarget+'/'+row["strName"]
      arr.append(fsName)
    subprocess.run(arr)  # check_output   arr.insert(0,'rm');

def myRmFolders(arrTargetRem, fsDirTarget):
  if(len(arrTargetRem)):
    arr=['rmdir']
    for row in arrTargetRem:
      fsName=fsDirTarget+'/'+row["strName"]
      arr.append(fsName)
    subprocess.run(arr)  # check_output   arr.insert(0,'rm');

def myCopyEntries(arrSourceRem, fsDirSource, fsDirTarget):
  for row in arrSourceRem:
    fsSouceName=fsDirSource+'/'+row["strName"]
    fsTargetName=fsDirTarget+'/'+row["strName"]
    fsPar=os.path.dirname(fsTargetName);  boExist=os.path.exists(fsPar);  boIsDir=os.path.isdir(fsPar)
    if(boExist): 
      if(not boIsDir): return {"strTrace":myErrorStack("boExist and not boIsDir")}
    else: Path(fsPar).mkdir(parents=True, exist_ok=True)
    subprocess.run(['cp', '-p', fsSouceName,fsTargetName])

def getRsyncList(fsDir):
  #leafOutputRsync='outputRsync.txt'
  #subprocess.run(['DIR=`mktemp -d /tmp/rsync.XXXXXX`'])
  #dirpath = tempfile.mkdtemp()
  
  #temp_dir = tempfile.TemporaryDirectory()
  #subprocess.run(['rsync', '-nr', "--out-format='%n'", fsDir, dirpath, '>', leafOutputRsync])
  #strData=subprocess.check_output(['rsync', '-nr', "--out-format='%n'", fsDir+'/', temp_dir.name])
  strData=subprocess.check_output(['rsync', '-nrF', "--out-format='%n'", fsDir+'/', "/dev/false"])

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
    fsName=fsDir+'/'+flName
    boIsFile=os.path.isfile(fsName)
    boIsDir=os.path.isdir(fsName)
    if(boIsFile):
      tmp=os.stat(fsName)
      ino=tmp.st_ino; mode=tmp.st_mode; mtime=tmp.st_mtime; mtime_ns=tmp.st_mtime_ns; size=tmp.st_size
      #myFile=MyFile(flName, ino, mtime, mtime_ns, size, 's')
      myFile={"strName":flName, "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns, "size":size, "keyST":KeyST(size, mtime_ns, 's')}
      arrf.append(myFile)
    elif(boIsDir):
      tmp=os.stat(fsName)
      ino=tmp.st_ino; mtime=tmp.st_mtime; mtime_ns=tmp.st_mtime_ns
      #myFold=MyFold(flName[:-1], ino, mtime, mtime_ns)
      myFold={"strName":flName[:-1], "ino":ino, "mtime":mtime, "mtime_ns":mtime_ns}
      arrF.append(myFold)
    else: 
      arrOther.append(flName)
  return arrf, arrF, arrOther



def writeMetaFile(arrDB, fsMeta):
      # If fsMeta exist then rename it
  if(os.path.isfile(fsMeta)):
    fsMetaWithCounter=calcFileNameWithCounter(fsMeta)
    os.rename(fsMeta, fsMetaWithCounter)

    # Write fsMeta
  fo=open(fsMeta,'w')
  fo.write('ino strHash mtime size strName\n')  #uuid 
  for row in arrDB:
    #fo.write('%s %10s %32s %10s %10s %s\n' %(row["uuid"], row["ino"], row["strHash"], math.floor(row["mtime"]), row["size"], row["strName"]))
    fo.write('%10s %32s %10s %10s %s\n' %(row["ino"], row["strHash"], math.floor(row["mtime"]), row["size"], row["strName"]))
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
    fo.write('%32s %10s %10s %s\n' %(row["strHash"], math.floor(row["mtime"]), row["size"], row["strName"]))
  fo.close()

def analysDupInd(arrS, arrT, objSDup, objTDup):
  arrOTO=[]; arrOTM=[]; arrMTO=[]; arrMTM=[]
  for i, row in enumerate(arrS):
    rowT=arrT[i]
    size=row["size"];   mtime=row["mtime"];   strKeyST=str(size)+str(mtime)
    boTDup=strKeyST in objTDup;    boSDup=strKeyST in objSDup 
    if(not boSDup and not boTDup): arrOTO.append(i)
    elif(not boSDup and boTDup): arrOTM.append(i)
    elif(boSDup and not boTDup): arrMTO.append(i)
    else: arrMTM.append(i)
  return arrOTO, arrOTM, arrMTO, arrMTM

def analysDup(arrS, arrT, objSDup, objTDup):
  arrSourceOTO=[]; ArrSourceOTM=[]; ArrSourceMTO=[]; ArrSourceMTM=[]
  arrTargetOTO=[]; ArrTargetOTM=[]; ArrTargetMTO=[]; ArrTargetMTM=[]
  for i, row in enumerate(arrS):
    rowT=arrT[i]
    size=row["size"];   mtime=row["mtime"];   strKeyST=str(size)+str(mtime)
    boSDup=strKeyST in objSDup;   boTDup=strKeyST in objTDup
    if(not boSDup and not boTDup): arrSourceOTO.append(row); arrTargetOTO.append(rowT);
    elif(not boSDup and boTDup): ArrSourceOTM.append([row]); ArrTargetOTM.append(objTDup[strKeyST]);
    elif(boSDup and not boTDup): ArrSourceMTO.append(objSDup[strKeyST]); ArrTargetMTO.append([rowT]);
    else: ArrSourceMTM.append(objSDup[strKeyST]); ArrTargetMTM.append(objTDup[strKeyST]);
  return arrSourceOTO, ArrSourceOTM, ArrSourceMTO, ArrSourceMTM, arrTargetOTO, ArrTargetOTM, ArrTargetMTO, ArrTargetMTM


def formatMatchingDataWDup(ArrS, ArrT, boIno):
  arrOut=[]
  for i, arrS in enumerate(ArrS):
    arrT=ArrT[i]
    size=arrS[0]["size"]; mtime=arrS[0]["mtime"]
    strKeyST=str(size)+str(mtime)
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


def formatMatchingData(arrS, arrT, ArrColMatch, ArrColUnique, fmtColMatch="  %s", fmtColUnique="    %s"):
    # The columns doesn't have to exist in both arrS and arrT. One of them is enough. 
    
  if(isinstance(ArrColMatch[0], list)):
    if(len(ArrColMatch)==1): ArrColMatch[1]=ArrColMatch[0]    # Convert [[c0, c1...]] => [[c0, c1...], [c0, c1...]]
  else: ArrColMatch=[ArrColMatch, ArrColMatch]                # Convert [c0, c1...] => [[c0, c1...], [c0, c1...]]
  if(isinstance(ArrColUnique[0], list)):
    if(len(ArrColUnique)==1): ArrColUnique[1]=ArrColUnique[0] #         (same as above)
  else: ArrColUnique=[ArrColUnique, ArrColUnique]             #         (same as above)
  arrColMatchS, arrColMatchT=ArrColMatch
  arrColUniqueS, arrColUniqueT=ArrColUnique
  if(len(arrS)==0): return []
  arrOut=[]
  for i, row in enumerate(arrS):
    rowT=arrT[i]
    arrHead=[]
    for j, strCol in enumerate(arrColMatchS):
      val=row[strCol] if(strCol in row) else rowT[strCol]
      arrHead.append(val)
    strHead=fmtColMatch %tuple(arrHead)
    arrOut.append(strHead)

    arrRowT=[];  arrRowS=[]
    for j, strCol in enumerate(arrColUniqueT):    arrRowT.append(rowT[strCol])
    for j, strCol in enumerate(arrColUniqueS):    arrRowS.append(row[strCol])
    strRowT=fmtColUnique %tuple(arrRowT);     strRowS=fmtColUnique %tuple(arrRowS)
    arrOut.append(strRowT);    arrOut.append(strRowS)
  return arrOut

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
    if(a=='/'): iLastSlash=i
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
    lev=keyA.count("/")
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

def writeResultInfo(StrScreen=[], StrResultFile=[], StrRenameOTO=[], StrRenameAncestorOnly=[], StrRenameAncestorOnlyCmd=[], StrDuplicateInitial=[], StrDuplicateFinal=[], StrRenameAdditional=[]):
  StrWrittenFiles=[]

  strTmp='\n'.join(StrResultFile)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafResultCompare)
  fof=open(leafResultCompare,'w');   fof.write(strTmp);   fof.close()
  
  strTmp='\n'.join(StrRenameOTO)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafRenameSuggestionsOTO)
  fof=open(leafRenameSuggestionsOTO,'w'); fof.write(strTmp);   fof.close()

  strTmp='\n'.join(StrRenameAncestorOnly)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafRenameSuggestionsAncestorOnly)
  fof=open(leafRenameSuggestionsAncestorOnly,'w'); fof.write(strTmp);   fof.close()

  strTmp='\n'.join(StrRenameAncestorOnlyCmd)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafRenameSuggestionsAncestorOnlyCmd)
  fof=open(leafRenameSuggestionsAncestorOnlyCmd,'w'); fof.write(strTmp);   fof.close()

  strTmp='\n'.join(StrDuplicateInitial)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafDuplicateInitial)
  fof=open(leafDuplicateInitial,'w'); fof.write(strTmp);   fof.close()

  strTmp='\n'.join(StrDuplicateFinal)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafDuplicateFinal)
  fof=open(leafDuplicateFinal,'w'); fof.write(strTmp);   fof.close()

  strTmp='\n'.join(StrRenameAdditional)
  if(strTmp): strTmp+='\n'; StrWrittenFiles.append(leafRenameSuggestionsAdditional)
  fof=open(leafRenameSuggestionsAdditional,'w'); fof.write(strTmp);   fof.close()
  
  if(StrWrittenFiles): StrScreen.append("More data written to these files: "+', '.join(StrWrittenFiles))
  strTmp='\n'.join(StrScreen);   print(strTmp)





# Notations:
# ST=size and time (time (or mTime)==modification time)
# OTO=OneToOne, OTM=OneToMany, MTO=ManyToOne, MTM=ManyToMany
#
# N files are untouched (matching strName and ST)
# N files in RenameInitial (IDd by ST). (ST-matching also resulting in duplicates: N OTM, N MTO, N MTM) (See list in duplicateInitial.txt)
# After looking at renamed folders (N), a further N files can be IDd as renameable. (See list in renameAdditional.txt)
#   So a final N renameables after matching ST and folder belonging (N OTM, N MTO, N MTM) (See list in duplicateFinal.txt)



#                                                  All
#                                          ╭───────╯ ╰────────╮
#                                      Untouched           Touched   
#                                                             |
#                                                      [match by meta]    
#                         ╭─────────────────────────────────╯ | ╰──────────────────────────╮
#   RenameInitial (OneToOne)                  OneToMany+ManyToOne+ManyToMany         NoMetaMatch (NToNull, NullToN)
#                       /  \                                  |                            |
# metaMatchChangeInParent  metaMatchChangeInLeaf        metaMatchDuplicate                 |
#                                                                                  [match by strName]
#                                                                                 ╭─────╯ ╰───────╮
#                                                                              Changed      Deleted+Created

#   [match metaMatchChangeInParent with metaMatchDuplicate] 
#                    ╭─────────╯ ╰─────────╮
#  addTomMetaMatchChangeInParent      addToNoMetaMatch

# Note, among the duplicates, there can be changed/deleted/created files
# Changed in OneToMany+ManyToOne+ManyToMany
# Deleted in OneToMany+ManyToMany
# Created in ManyToOne+ManyToMany

# T\S    Null    One     Many
# Null           Created Created
# One    Deleted OTO     MTO
# Many   Deleted OTM     MTM


# Changed, Deleted, Created are written in resultCompare.txt

#####################################################################


  # Moves "rows" (entries) from objAMetaMatch and objBMetaMatch to objAncestorOnlyRenamed and arrAIdd, arrBIdd
def extractExtraByFolderOld(objAMetaMatch, objBMetaMatch, objAncestorOnlyRenamed):
  arrAIdd=[]; arrBIdd=[]
  for key, arrAMetaMatch in objAMetaMatch.items():
    arrBMetaMatch=objBMetaMatch[key]
    lenA=len(arrAMetaMatch); lenB=len(arrBMetaMatch)
    if(lenA==1 and lenB==1): continue
    for j, rowA in reversed(list(enumerate(arrAMetaMatch))):
      for k, rowB in reversed(list(enumerate(arrBMetaMatch))):
        strA=rowA["strName"]; strB=rowB["strName"]
        strParA, strParB=extractDivergingParents(strA, strB)
        if(strParA==None): continue
        if(strParA in objAncestorOnlyRenamed and strParB in objAncestorOnlyRenamed[strParA]):
          objAncestorOnlyRenamed[strParA][strParB].append({"elA":rowA, "elB":rowB})
          arrAIdd.append(rowA); arrBIdd.append(rowB)
          del arrAMetaMatch[j]; del arrBMetaMatch[k]
  return arrAIdd, arrBIdd

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
      for k, rowB in reversed(list(enumerate(arrBMetaMatch))):
        strA=rowA["strName"]; strB=rowB["strName"]
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
  strNullTM="%d(%d)" %(nBNullTM, nPatNullTM)
  strOTM="%d\%d" %(nAOTM, nBOTM)
  strOTNull='%d' %(nAOTNull)
  strMTNull="%d(%d)" %(nAMTNull, nPatMTNull)
  strMTO="%d\%d" %(nAMTO, nBMTO)
  strMTM="%d\%d(%d)" %(nAMTM, nBMTM, nPatMTM)
  if(nPatNullTO!=nBNullTO): print("nPatNullTO!=nBNullTO"); breakpoint()
  if(nPatOTNull!=nAOTNull): print("nPatOTNull!=nAOTNull"); breakpoint()
  if(nPatOTM!=nAOTM): print("nPatOTM!=nAOTM"); breakpoint()
  if(nPatMTO!=nBMTO): print("nPatMTO!=nBMTO"); breakpoint()
  nFileChangedNDeleted=nBNullTO+nBNullTM
  nPatChangedNDeleted=nBNullTO+nPatNullTM
  strChangedNDeleted="%d(%d)" %(nFileChangedNDeleted, nPatChangedNDeleted)
  nFileChangedNCreated=nAOTNull+nAMTNull
  nPatChangedNCreated=nAOTNull+nPatMTNull
  strChangedNCreated="%d(%d)" %(nFileChangedNCreated, nPatChangedNCreated)
  return """Source⇣ \ Target⇢  Null          One         Many
Null %18s %12s %12s ⇠Deleted+Changed: %s
One  %18s %12d %12s
Many %18s %12s %12s
       Created+Changed⇡ %s""" %("-", strNullTO, strNullTM, strChangedNDeleted,
       strOTNull, nOTO+nOTOAdd, strOTM,
       strMTNull, strMTO, strMTM,   strChangedNCreated)



def compareTreeToTree():
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', "--fiDirSource", default='.')
  parser.add_argument('-t', "--fiDirTarget", default='.')
  args = parser.parse_args(argv)

      # Parse trees
  fsDirSource=os.path.realpath(args.fiDirSource)
  fsDirTarget=os.path.realpath(args.fiDirTarget)
  arrSourcef, arrSourceF =parseTree(fsDirSource, True)
  arrTargetf, arrTargetF =parseTree(fsDirTarget, False)

  for row in arrSourcef: row["mtime"]=math.floor(row["mtime"])  # Floor mtime
  for row in arrTargetf: row["mtime"]=math.floor(row["mtime"])  # Floor mtime


  comparisonWOID=ComparisonWOID(arrSourcef, arrTargetf)
  err=comparisonWOID.compare()
  if(err): print(err["strTrace"]); return
  strCommandName=sys._getframe().f_code.co_name
  [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional]=comparisonWOID.format(strCommandName, fsDirTarget, 'buvt-meta.txt')
  writeResultInfo(StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional)


def compareTreeToST():
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", default='.')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')

  args = parser.parse_args(argv)

    # Parse tree
  fsDir=os.path.realpath(args.fiDir)
  arrTreef, arrTreeF =parseTree(fsDir, True)
  for row in arrTreef: row["mtime"]=math.floor(row["mtime"]) # Floor mtime

    # Parse DB
  fiMeta=args.fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  #if(err): print(err["strTrace"]); return
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: print(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args.flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  comparisonWOID=ComparisonWOID(arrTreef, arrDB)
  err=comparisonWOID.compare()
  if(err): print(err["strTrace"]); return
  strCommandName=sys._getframe().f_code.co_name
  [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional]=comparisonWOID.format(strCommandName, fsDir, fiMeta)
  writeResultInfo(StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional)


def syncTreeToTreeBrutal(): # buCopyUnlessNameSTMatch
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', "--fiDirSource", default='.')
  parser.add_argument('-t', "--fiDirTarget", required=True)
  args = parser.parse_args(argv)
  fsDirSource=os.path.realpath(args.fiDirSource)
  fsDirTarget=os.path.realpath(args.fiDirTarget)
    # Parse trees
  arrSourcef, arrSourceF =parseTree(fsDirSource, True)
  arrTargetf, arrTargetF =parseTree(fsDirTarget, False)
  for row in arrSourcef: row["mtime"]=math.floor(row["mtime"]) # Floor mtime
  for row in arrTargetf: row["mtime"]=math.floor(row["mtime"]) # Floor mtime

    # Remove untouched
  arrSourcef=sorted(arrSourcef, key=lambda x: x["strName"]);   arrTargetf=sorted(arrTargetf, key=lambda x: x["strName"])
  arrSourceUntouched, arrTargetUntouched, arrSourceRem, arrTargetRem=extractMatching(arrSourcef, arrTargetf, ['strName', 'size', 'mtime'])
  lenSource=len(arrSourceRem); lenTarget=len(arrTargetRem)
  #if(lenSource==0 and lenTarget==0): print('Nothing to do, aborting'); return

  #arrSourceRem=sorted(arrSourceRem, key=lambda x:(x["size"], x["mtime"]));   arrTargetRem=sorted(arrTargetRem, key=lambda x:(x["size"], x["mtime"]))

  #input('Deleting %d then creating %d file(s). Press enter to continue.' %(lenTarget, lenSource))
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Deleting %d then creating (copying) %d file(s). Press enter to continue.' %(lenTarget, lenSource))
  myRmFiles(arrTargetRem, fsDirTarget)
  myCopyEntries(arrSourceRem, fsDirSource, fsDirTarget)

    # Delete remaining Folders
  arrSourceF=sorted(arrSourceF, key=lambda x: x["strName"]);   arrTargetF=sorted(arrTargetF, key=lambda x: x["strName"])
  arrSourceUntouched, arrTargetUntouched, arrSourceRem, arrTargetRem=extractMatching(arrSourceF, arrTargetF, ['strName'])
  lenSource=len(arrSourceRem); lenTarget=len(arrTargetRem)

  if(lenSource==0 and lenTarget==0): return

  arrSourceRem=sorted(arrSourceRem, key=lambda x: x["strName"], reverse=True)
  arrTargetRem=sorted(arrTargetRem, key=lambda x: x["strName"], reverse=True)
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Deleting %d then creating (making sure they exist) %d Folder(s). Press enter to continue.' %(lenTarget, lenSource))
  myRmFolders(arrTargetRem, fsDirTarget)









#####################################################################################
# "sync" functions
#####################################################################################

#####################################################################################
# With Id
#####################################################################################

def syncTreeToMeta(strCommandName):
  boSync=strCommandName=='syncTreeToMeta'
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", default='.')
  parser.add_argument('-m', "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse tree
  fsDir=os.path.realpath(args.fiDir)
  arrTreef, arrTreeF =parseTree(fsDir, True)
  for row in arrTreef: row["mtime"]=math.floor(row["mtime"])  # Floor mtime

    # Parse fiMeta
  fiMeta=args.fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err):
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]   #boSync and 
    else: print(err["strTrace"]); return

  flPrepend=args.flPrepend;    nPrepend=len(flPrepend)
  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant


      # Check for duplicate ino
  arrTreef=sorted(arrTreef, key=lambda x: x["ino"]);   arrDB=sorted(arrDB, key=lambda x: x["ino"])
  _, arrTreefUniqueIno, objTreeDup=extractDuplicateKey(arrTreef,"ino")
  _, arrDBUniqueIno, objDBDup=extractDuplicateKey(arrDB,"ino")
  lenTreeDup=len(objTreeDup);   lenDBDup=len(objDBDup)
  if(lenTreeDup):  strTmp='Duplicate ino, in tree:%d (hard links? (Note! hard links are not allowed))' %(lenTreeDup);   print(strTmp);  return
  if(lenDBDup):  strTmp='Duplicate ino, in meta:%d' %(lenDBDup);   print(strTmp);  return


  comparisonWID=ComparisonWID('ino', arrTreef, arrDB)
  err=comparisonWID.compare()
  if(err): print(err["strTrace"]); return
  [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd]=comparisonWID.format(strCommandName, fsDir, fiMeta)
  writeResultInfo(StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd)

  [arrTreeUnTouched, arrDBUnTouched, arrTreeChanged, arrDBChanged, arrTreeMetaMatch, arrDBMetaMatch, arrTreeNST, arrDBNST, arrTreeMatchingId, arrDBMatchingId, arrTreeMatchingStrName, arrDBMatchingStrName, arrSourceRem, arrTargetRem]=comparisonWID.getCategoryArrays()

  arrCreate, arrDelete = arrSourceRem, arrTargetRem
  #boAllOK=len(arrCreate)==0 and len(arrDelete)==0
  #if(boAllOK): print('No changes, aborting'); return
  if(not boSync): return


    # Change arrDBChanged
  for i, row in enumerate(arrTreeChanged):
    rowDB=arrDBChanged[i]
    print("Calculating hash for changed file: %s" %(row["strName"]))
    strHash=myMD5(fsDir+'/'+row["strName"]).decode("utf-8")
    rowDB.update({"strHash":strHash, "size":row["size"], "mtime":row["mtime"]})

    # Rename arrDBMetaMatch
  for i, row in enumerate(arrTreeMetaMatch):
    rowDB=arrDBMetaMatch[i]
    rowDB["strName"]=row["strName"]

    # Rename Copy renamed to origin
  for i, row in enumerate(arrTreeNST):
    rowDB=arrDBNST[i]
    rowDB["ino"]=row["ino"]

    # Matching ino
  for i, row in enumerate(arrTreeMatchingId):
    rowDB=arrDBMatchingId[i]
    print("Calculating hash for changed+renamed file: %s" %(row["strName"]))
    strHash=myMD5(fsDir+'/'+row["strName"]).decode("utf-8")
    rowDB.update({"strHash":strHash, "size":row["size"], "mtime":row["mtime"], "strName":row["strName"]})

    # Matching strName
  for i, row in enumerate(arrTreeMatchingStrName):
    rowDB=arrDBMatchingStrName[i]
    print("Calculating hash for deleted+recreated file: %s" %(row["strName"]))
    strHash=myMD5(fsDir+'/'+row["strName"]).decode("utf-8")
    rowDB.update({"ino":row["ino"], "strHash":strHash, "size":row["size"], "mtime":row["mtime"]})

      # Remaining
  for i, row in enumerate(arrCreate):
    print("Calculating hash for created file: %s" %(row["strName"]))
    strHash=myMD5(fsDir+'/'+row["strName"]).decode("utf-8")
    row.update({"strHash":strHash}) #, "uuid":myUUID()


  arrDBNew=arrDBUnTouched+arrDBChanged+arrDBMetaMatch+arrDBNST+arrDBMatchingId+arrDBMatchingStrName+arrCreate
    # Add flPrepend to strName if appropriate
  if(nPrepend>0): 
    for row in arrDBNew: row["strName"]=flPrepend+row["strName"]

    # Add Non-relevant entries
  arrDBNew=arrDBNew+arrDBNonRelevant
  arrDBNew=sorted(arrDBNew, key=lambda x: x["strName"])

  #for i, row in enumerate(arrDBNew):  if("uuid" not in row): row["uuid"]=myUUID()
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMeta)






#######################################################################################
# compare functions
#######################################################################################





#####################################################################################
# renameFinish functions
#####################################################################################

def renameFinishToTree(boFold=False, strStartToken=None):
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", required=True)
  parser.add_argument('-f', "--file")

  args = parser.parse_args(argv)
  fsRenameFold=os.path.realpath(args.fiDir)

  if(args.file): leafFile=args.file
  elif(boFold): leafFile=leafRenameSuggestionsAncestorOnly
  else: leafFile=leafRenameSuggestionsOTO
  #fsFile=os.path.realpath(leafFile)
  

  err, arrRename=parseRenameInput(leafFile, strStartToken)
  if(err): print(err["strTrace"]); return
  arrRename=sorted(arrRename, key=lambda x: x['strOld'])

  #input('Renaming %d files. Press enter to continue.' %(len(arrRename)))
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Renaming %d entry/entries. Press enter to continue.' %(len(arrRename)))
  err=renameFiles(fsRenameFold, arrRename)
  if(err): print(err["strTrace"]); return
  return


def renameFinishToMeta():
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  args = parser.parse_args(argv)

    # Parse leafRenameSuggestionsOTO
  err, arrRename=parseRenameInput(leafRenameSuggestionsOTO)
  if(err): print(err["strTrace"]); return
  arrRename=sorted(arrRename, key=lambda x: x['strOld'])

    # Parse fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: print(err["strTrace"]); return
  arrDB=sorted(arrDB, key=lambda x: x["strName"])

  arrRenameMatch, arrDBMatch, arrRenameRem, arrDBRem=extractMatching(arrRename, arrDB, ['strOld'], ['strName'])

    # Rename arrDBMatch
  for i, row in enumerate(arrRenameMatch):
    rowDB=arrDBMatch[i]
    rowDB["strName"]=row["strNew"]

  arrDBNew=arrDBRem+arrDBMatch
  arrDBNew=sorted(arrDBNew, key=lambda x: x["strName"])
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMeta)

  print('done')

def renameFinishToMetaByFolder():
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  args = parser.parse_args(argv)

    # Parse leafRenameSuggestionsAncestorOnly
  err, arrRename=parseRenameInput(leafRenameSuggestionsAncestorOnly, "RelevantAncestor")
  if(err): print(err["strTrace"]); return
  #arrRename=sorted(arrRename, key=lambda x: x['strOld'])

    # Parse fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: print(err["strTrace"]); return
  arrDB=sorted(arrDB, key=lambda x: x["strName"])


  def funVal(val): return val['strOld']
  def funB(rowB, l): return rowB['strName'][:l]
  def funExtra(val): return len(val['strOld'])
  arrRenameMatch, arrDBMatch, arrRenameRem, arrDBRem=extractMatchingOneToManyUnsortedFW(arrRename, arrDB, funVal, funB, funExtra)

  if(len(arrRenameMatch)!=len(arrDBMatch)): print("Error: len(arrRenameMatch)!=len(arrDBMatch)"); return

    # Rename arrDBMatch
  for i, row in enumerate(arrRenameMatch):
    rowDB=arrDBMatch[i]
    strOld=row['strOld']; l=len(strOld);
    rowDB["strName"]=row["strNew"]+rowDB["strName"][l:]

  arrDBNew=arrDBRem+arrDBMatch
  arrDBNew=sorted(arrDBNew, key=lambda x: x["strName"])
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMeta)

  print('done')





#######################################################################################
# testFilter
#######################################################################################
def testFilter():
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', "--fiDirSource", default='.')
  args = parser.parse_args(argv)
  fsDirSource=os.path.realpath(args.fiDirSource)
  arrRsf, arrRsF, arrRsOther=getRsyncList(fsDirSource)

  arrSourcef, arrSourceF =parseTree(fsDirSource, True)

  arrSourcef=sorted(arrSourcef, key=lambda x:x["strName"])
  arrSourceF=sorted(arrSourceF, key=lambda x:x["strName"])
  arrRsf=sorted(arrRsf, key=lambda x:x["strName"])
  arrRsF=sorted(arrRsF, key=lambda x:x["strName"])
  nRsf=len(arrRsf); nRsF=len(arrRsF)
  nf=len(arrSourcef); nF=len(arrSourceF)
  leafResult='resultFrTestFilter.txt'
  leafResultRs='resultFrTestFilterRs.txt'
  fo=open(leafResult,'w'); foRs=open(leafResultRs,'w')
  for i, row in enumerate(arrSourcef): fo.write(row["strName"]+'\n')
  for i, row in enumerate(arrSourceF): fo.write(row["strName"]+'\n')
  for i, row in enumerate(arrRsf): foRs.write(row["strName"]+'\n')
  for i, row in enumerate(arrRsF): foRs.write(row["strName"]+'\n')
  foRs.write('  arrRsOther:\n')
  for i, row in enumerate(arrRsOther): foRs.write(row+'\n')
  fo.close();   foRs.close()
  print('%s and %s written' %(leafResult, leafResultRs))



def convertHashcodeFileToMeta(): # Add inode and create uuid
  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--fiDir", default='.')
  parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse tree
  fsDir=os.path.realpath(args.fiDir)
  arrTreef, arrTreeF =parseTree(fsDir, True) # boUseFilter should perhaps be False (although it might be slow)
  for row in arrTreef: row["mtime"]=math.floor(row["mtime"]) # Floor mtime

    # Parse fiHash
  fsHash=os.path.realpath(args.fiHash)
  err, arrDB=parseHashFile(fsHash)
  if(err): print(err["strTrace"]); return

    # fiMeta
  fsMeta=os.path.realpath(args.fiMeta)

  # arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args.flPrepend)
  # arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);   arrDB=sorted(arrDB, key=lambda x: x["strName"])
  arrTreeMatch, arrDBMatch, arrTreeRem, arrDBRem=extractMatching(arrTreef, arrDB, ['strName'], ['strName'])

  #if(len(arrTreeRem) or len(arrDBRem)): return "Error: "+"len(arrTreeRem) OR len(arrDBRem)"
  if(len(arrTreeRem)): return "Error: "+"len(arrTreeRem)"

  for i, rowDB in enumerate(arrDBMatch):
    #if("uuid" not in rowDB): rowDB["uuid"]=myUUID() # Add uuid if it doesn't exist
    row=arrTreeMatch[i]
    rowDB["ino"]=row["ino"] # Copy ino

  arrDBNew=arrDBMatch
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMeta)
  print('done')



def convertMetaToHashcodeFile(): # Add inode and create uuid
  parser = argparse.ArgumentParser()
  parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): print(err["strTrace"]); return

    # Parse fiHash
  fsHash=os.path.realpath(args.fiHash)

  # arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args.flPrepend)
  # arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrDBNew=arrDB
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to hash-file. Press enter to continue.' %(len(arrDBNew)))
  writeHashFile(arrDBNew, fsHash)
  print('done')



def moveMeta(): 
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--fiMetaS", default='buvt-meta.txt')
  parser.add_argument("-o", "--fiMetaOther", required=True)
  parser.add_argument("-d", "--fiDirT", required=True)
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse fiMetaS
  fsMetaS=os.path.realpath(args.fiMetaS)
  err, arrDBS=parseSSVCustom(fsMetaS)
  if(err): print(err["strTrace"]); return

    # Parse fiMetaOther
  fsMetaOther=os.path.realpath(args.fiMetaOther)
  err, arrDBOther=parseSSVCustom(fsMetaOther)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDBOther=[]
    else: print(err["strTrace"]); return

    # Parse tree
  fsDir=os.path.realpath(args.fiDirT)
  arrTreef, arrTreeF =parseTree(fsDir, True)
  for row in arrTreef: row["mtime"]=math.floor(row["mtime"]) # Floor mtime

  flPrepend=args.flPrepend;    nPrepend=len(flPrepend)
  arrDBOtherNonRelevant, arrDBOtherRelevant =selectFrArrDB(arrDBOther, flPrepend)
  arrDBOtherOrg=arrDBOther;   arrDBOther=arrDBOtherRelevant

  # arrTreefNonRelevant, arrTreefRelevant =selectFrArrDB(arrTreef, flPrepend)
  # arrTreefOrg=arrTreef;   arrTreef=arrTreefRelevant


  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);   arrDBS=sorted(arrDBS, key=lambda x: x["strName"])
  arrTreeMatch, arrDBSMatch, arrTreeRem, arrDBSRem=extractMatching(arrTreef, arrDBS, ['strName'], ['strName'])

  #if(len(arrTreeRem) or len(arrDBRem)): return "Error: "+"len(arrTreeRem) OR len(arrDBRem)"
  #if(len(arrTreeRem)): return "Error: "+"len(arrTreeRem)"

  for i, rowDBS in enumerate(arrDBSMatch):
    rowTree=arrTreeMatch[i]
    rowDBS["ino"]=rowTree["ino"]

  arrDBOtherNew=arrDBSMatch
  if(nPrepend>0): 
    for row in arrDBOtherNew: row["strName"]=flPrepend+row["strName"]

  arrDBOtherNew=arrDBOtherNonRelevant+arrDBOtherNew
  arrDBOtherNew=sorted(arrDBOtherNew, key=lambda x: x["strName"])
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBOtherNew)))
  writeMetaFile(arrDBOtherNew, fsMetaOther)



def sortHashcodeFile(): # 
  parser = argparse.ArgumentParser()
  parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse fiHash
  fsHash=os.path.realpath(args.fiHash)
  err, arrDB=parseHashFile(fsHash)
  if(err): print(err["strTrace"]); return

  arrDB=sorted(arrDB, key=lambda x: x["strName"])

  writeHashFile(arrDB, fsHash)
  print('done')


def changeIno(): 
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", default='.')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)
  fsDir=os.path.realpath(args.fiDir)

    # Parse tree
  arrTreef, arrTreeF =parseTree(fsDir, True)
  for row in arrTreef: row["mtime"]=math.floor(row["mtime"]) # Floor mtime

    # Parse fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): print(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args.flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);  arrDB=sorted(arrDB, key=lambda x: x["strName"])
  arrTreeMatch, arrDBMatch, arrTreeRem, arrDBRem=extractMatching(arrTreef, arrDB, ['strName'], ['strName'])


  for i, rowDB in enumerate(arrDBMatch):
    rowTree=arrTreeMatch[i]
    #if("uuid" not in rowDB): rowDB["uuid"]=myUUID()
    rowDB["ino"]=rowTree["ino"]

  arrDBNew=arrDBMatch
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMeta)

  print('done')

def utilityMatchTreeAndMeta():  # For running different experiments 
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", default='.')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)
  fsDir=os.path.realpath(args.fiDir)

    # Parse tree
  arrTreef, arrTreeF =parseTree(fsDir, True)
  for row in arrTreef: row["mtime"]=math.floor(row["mtime"]) # Floor mtime

    # Parse fiMeta
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): print(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args.flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);  arrDB=sorted(arrDB, key=lambda x: x["strName"])
  arrTreeMatch, arrDBMatch, arrTreeRem, arrDBRem=extractMatching(arrTreef, arrDB, ['strName'], ['strName'])


  for i, rowDB in enumerate(arrDBMatch):
    rowTree=arrTreeMatch[i]
    #if("uuid" not in rowDB): rowDB["uuid"]=myUUID()
    rowDB["ino"]=rowTree["ino"]

  arrDBNew=arrDB
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMeta)

  print('done')


def utilityMatchMetaAndMeta():  # For running different experiments 
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--fiMetaS", default='buvt-meta.txt')
  parser.add_argument('-t', "--fiMetaT", required=True)
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse fiMetaS
  fsMetaS=os.path.realpath(args.fiMetaS)
  err, arrDBS=parseSSVCustom(fsMetaS)
  if(err): print(err["strTrace"]); return

    # Parse fiMetaT
  fsMetaT=os.path.realpath(args.fiMetaT)
  err, arrDBT=parseSSVCustom(fsMetaT)
  if(err): print(err["strTrace"]); return

  arrDBTNonRelevant, arrDBTRelevant =selectFrArrDB(arrDBT, args.flPrepend)
  arrDBTOrg=arrDBT;   arrDBT=arrDBTRelevant


  arrDBS=sorted(arrDBS, key=lambda x: x["strName"]);   arrDBT=sorted(arrDBT, key=lambda x: x["strName"])
  arrDBSMatch, arrDBTMatch, arrDBSRem, arrDBTRem=extractMatching(arrDBS, arrDBT, ['strName'])

    # Move uuid to arrDBMatch
  # for i, row in enumerate(arrDBSMatch):
  #   rowT=arrDBTMatch[i]
  #   rowT["uuid"]=row["uuid"]

  for i, row in enumerate(arrDBT):
    row["strName"]=args.flPrepend+row["strName"]

  arrDBNew=arrDBTNonRelevant+arrDBTMatch+arrDBTRem
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDBNew)))
  writeMetaFile(arrDBNew, fsMetaT)

  print('done')

def utilityAddToMetaStrName():  # For running different experiments 
  parser = argparse.ArgumentParser()
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument("--flPrepend", default='')
  args = parser.parse_args(argv)

    # Parse fiMetaS
  fsMeta=os.path.realpath(args.fiMeta)
  err, arrDB=parseSSVCustom(fsMeta)
  if(err): print(err["strTrace"]); return
  arrDB=sorted(arrDB, key=lambda x: x["strName"])

  flPrepend=args.flPrepend; nPrepend=len(flPrepend)


  #flPrependTmp=flPrepend+"/" if(nPrepend) else ""
  for i, row in enumerate(arrDB):
    row["strName"]=flPrepend+row["strName"]
  
  #if(boDryRun): print("(Dry run) exiting"); return
  if(boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else: input('Writing %d entries to meta-file. Press enter to continue.' %(len(arrDB)))
  writeMetaFile(arrDB, fsMeta)

  print('done')


def check(): # buCopyUnlessNameSTMatch
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", default='.')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  parser.add_argument( "--start", default=0)
  args = parser.parse_args(argv)
  fsDir=os.path.realpath(args.fiDir)
  fsMeta=os.path.realpath(args.fiMeta)
  intStart=int(args.start)
  checkInterior(fsMeta, fsDir, intStart)

def checkSummarizeMissing(): 
  parser = argparse.ArgumentParser()
  parser.add_argument('-d', "--fiDir", default='.')
  parser.add_argument("-m", "--fiMeta", default='buvt-meta.txt')
  args = parser.parse_args(argv)
  fsDir=os.path.realpath(args.fiDir)
  fsMeta=os.path.realpath(args.fiMeta)
  checkSummarizeMissingInterior(fsMeta, fsDir)

def deleteResultFiles(): 
  arr=[leafResultCompare, leafRenameSuggestionsAncestorOnly, leafDuplicateInitial, leafDuplicateFinal, leafRenameSuggestionsAdditional, leafRenameSuggestionsOTO]
  for leafTmp in arr:
    try: os.remove(leafTmp); print("Deleted: "+leafTmp)
    except FileNotFoundError as e:
      print("Couldn't delete: "+leafTmp)  

#######################################################################################
# Main
#######################################################################################
#tStart=time.time()
def main():
  global tStart
  global argv; #argv=copy.copy(sys.argv); del argv[0]
  argv=sys.argv[1:]
    # boDryRun
  global boDryRun; boDryRun=False
  indShort=myIndexOf(argv, '-n')
  ind=myIndexOf(argv, '--boDryRun')
  if(indShort>=0 and ind>=0): print("Use -n OR --boDryRun, not both. "); return
  if(indShort>=0): boDryRun=True; del argv[indShort]
  if(ind>=0): boDryRun=True; del argv[ind]

    # leafBuvtFilter
  global leafFilter; leafFilter=".buvt-filter"
  global leafFilterFirst; leafFilterFirst=leafFilter
  ind=myIndexOf(argv, '--leafFilterFirst')
  if(ind>=0):
    if(ind+1>=len(argv)): print("--leafFilterFirst should be followed by one more argument"); return
    leafFilterFirst=argv[ind+1]; del argv[ind+1]; del argv[ind]

  modeMain=argv[0]
  del argv[0]
  StrModeMain=['compareTreeToTree', 'compareTreeToST', 'syncTreeToTreeBrutal', 
  'compareTreeToMeta', 'syncTreeToMeta', 
  'renameFinishToTree', 'renameFinishToTreeByFolder', 'renameFinishToMeta', 'renameFinishToMetaByFolder', 
  'moveMeta', 'testFilter', 'convertHashcodeFileToMeta', 'convertMetaToHashcodeFile', 'sortHashcodeFile', 'changeIno', 'utilityMatchTreeAndMeta', 'utilityMatchMetaAndMeta', 'utilityAddToMetaStrName', 'check', 'checkSummarizeMissing', 'deleteResultFiles', 'complete']
  StrModeMainWOComplete=StrModeMain[:-1]
  if(modeMain not in StrModeMain): print("Error: The first argument should be any of: "+', '.join(StrModeMain)); return

  if(modeMain=='compareTreeToTree'): compareTreeToTree()
  elif(modeMain=='compareTreeToST'): compareTreeToST()
  elif(modeMain=='syncTreeToTreeBrutal'): syncTreeToTreeBrutal()

  elif(modeMain=='compareTreeToMeta'): syncTreeToMeta(modeMain)
  elif(modeMain=='syncTreeToMeta'): syncTreeToMeta(modeMain)
  
  elif(modeMain=='renameFinishToTree'): renameFinishToTree()
  elif(modeMain=='renameFinishToTreeByFolder'): renameFinishToTree(True, "RelevantAncestor")
  elif(modeMain=='renameFinishToMeta'): renameFinishToMeta()
  elif(modeMain=='renameFinishToMetaByFolder'): renameFinishToMetaByFolder()

  elif(modeMain=='moveMeta'): moveMeta()
  elif(modeMain=='testFilter'): testFilter()
  elif(modeMain=='convertHashcodeFileToMeta'): convertHashcodeFileToMeta()
  elif(modeMain=='convertMetaToHashcodeFile'): convertMetaToHashcodeFile()
  elif(modeMain=='sortHashcodeFile'): sortHashcodeFile()
  elif(modeMain=='changeIno'): changeIno()
  elif(modeMain=='utilityMatchTreeAndMeta'): utilityMatchTreeAndMeta()
  elif(modeMain=='utilityMatchMetaAndMeta'): utilityMatchMetaAndMeta()
  elif(modeMain=='utilityAddToMetaStrName'): utilityAddToMetaStrName()
  elif(modeMain=='check'): check()
  elif(modeMain=='checkSummarizeMissing'): checkSummarizeMissing()
  elif(modeMain=='deleteResultFiles'): deleteResultFiles()

  elif(modeMain=='complete'): 
    lenArg=len(argv)
    if(lenArg==0): print('\n'.join(StrModeMainWOComplete)); return
    strIn=argv[0]; lenIn=len(strIn)
    StrModeOut=[]
    for strMode in StrModeMainWOComplete:
      if(strIn==strMode[:lenIn]): StrModeOut.append(strMode)
    print('\n'.join(StrModeOut))


  if(modeMain!='complete'): 
    tStop=time.time();   print('elapsed time '+str(round((tStop-tStart)*1000))+'ms')



if __name__ == '__main__':
  main()



#      .bash_completion - file (should be placed in home directory (run "source .bash_completion" to activate it immediately))
#
# function _mycomplete_()
# {
#   # COMP_LINE: (whole line)
#   # COMP_WORDS: myfoo
#   # COMP_CWORD: (number of words)
#   local cmd="${1##*/}"   # myfoo
#   local word=${COMP_WORDS[COMP_CWORD]}
#   local line=${COMP_LINE}
#   local xpat='!*.foo'
#   varA=$(pwd)
#   array=()
#   while read line ; do
#     array+=($line)
#   #done < <(renamerArg.py $varA)
#   done < <(buvt.py complete $word)
#   #done < <(buvtComplete.py  $word)
#   #echo ${array[@]}
#   local n=${#array[@]}
#   #echo $n
#   #COMPREPLY=($(compgen -f -X "$xpat" -- "${word}"))
#   #COMPREPLY=("abc","def")
#   #COMPREPLY=("${array[@]}")
#   if [[ $n -eq q ]]
#   then
#     COMPREPLY="${array[@]}"
#   else
#     COMPREPLY=("${array[@]}")
#   fi
# }
# complete -F _mycomplete_ buvt.py
