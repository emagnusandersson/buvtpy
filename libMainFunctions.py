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
#           compareTreeToMetaSTOnly, syncTreeToHashcodeFileBrutal, renameFinishToHashcodeFile, renameFinishToHashcodeFileByFolder
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
# compareTreeToMetaSTOnly




from distutils.log import debug
import math
import os
import argparse
import time
import sys
from glob import glob
from os.path import relpath
from importlib import import_module
from operator import itemgetter
import subprocess
from lib import *
#from settings import *
import settings
import globvar
from libCheck import *
from libBag import *
from libBagFs import *
from libParse import *
from libFs import *
import tempfile
import errno
import traceback
from types import SimpleNamespace

from pathlib import *

#from libGUI import *
#from buvt import *

# class PosixPath(PosixPath):
#   #@staticmethod
#   def sayHi(self):
#     globvar.myConsole.error('hi')

# p=Path()




# Matching:         match: NAME MTIME SIZE
# RenameCandidates: match:  -   MTIME SIZE
# NameMtime:        match: NAME MTIME  -
# NameSize:         match: NAME   -   SIZE
# Name:             match: NAME   -    -
# Mtime:            match:  -   MTIME  -
# Size:             match:  -     -   SIZE
# Rest:             match:  -     -    -






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

# T\S    0       1       Many
# 0              Created Created
# 1      Deleted OTO     MTO
# Many   Deleted OTM     MTM


# Changed, Deleted, Created are written in resultMore.txt

#####################################################################




def hardLinkCheck(**args):
  fsDirSource=myRealPathf(args["fiDirSource"])
  charTRes=args.get("charTRes") or settings.charTRes
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  treeParser=TreeParser()
  err, arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, charTRes, leafFilterFirst)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDirSource}')
    else: globvar.myConsole.error(err["strTrace"])
    return

  arrSourcef.sort(key=lambda x: x["ino"]);   arrSourceF.sort(key=lambda x: x["ino"])

  arrUniq, objDupf, arrUniqifiedf=extractUniques(arrSourcef,"ino")
  arrUniq, objDupF, arrUniqifiedF=extractUniques(arrSourceF,"ino")
  Str=[]
  Str.append(f"Hard linked files (inodes with multiple names): {len(objDupf)}")
  Str.append(f"(inodes: {len(arrUniqifiedf)}, filenames: {len(arrSourcef)}), ")
  Str.append(f"Hard linked folders (inodes with multiple names): {len(objDupF)}")
  Str.append(f"(inodes: {len(arrUniqifiedF)}, dirnames: {len(arrSourceF)}) ")
  #globvar.myConsole.printNL('\n'.join(Str))



  funMatch=lambda s: '  fileId %20d' %(s["ino"]);  funUnique=lambda s: '    %s' %(s["strName"])
  StrTmpf=formatMatchingDataWDupSingleDataSet(objDupf, funMatch, funUnique)
  StrTmpF=formatMatchingDataWDupSingleDataSet(objDupF, funMatch, funUnique)
  myReporter=MyReporter(settings.StrStemT2M)
  myReporter.Str['screen'].extend(Str)
  myReporter.Str['T2M_sum'].extend(Str)
  myReporter.Str['T2M_HL'].extend(StrTmpF+StrTmpf)
  myReporter.writeToFile()







#####################################################################################
# T2M
#####################################################################################

class SyncTreeToMeta():
  def __init__(self, strCommandName, **args):
    self.strCommandName=strCommandName
    self.fsDir=myRealPathf(args["fiDir"])
    self.charTRes=args.get("charTRes") or settings.charTRes
    self.leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
    self.leafMeta=args.get("leafMeta") or settings.leafMeta
    self.flPrepend=args.get("flPrepend") or "";    self.nPrepend=len(self.flPrepend)

  def compare(self):
    strCommandName=self.strCommandName; fsDir=self.fsDir; charTRes=self.charTRes; leafFilterFirst=self.leafFilterFirst; leafMeta=self.leafMeta; flPrepend=self.flPrepend; nPrepend=self.nPrepend
    
      # Parse tree
    treeParser=TreeParser()
    err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst)
    removeLeafMetaFromArrTreef(arrTreef, leafMeta)
    if(err): 
      if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
      else: globvar.myConsole.error(err["strTrace"])
      return

      # Parse fsMeta
    fsMeta=self.fsMeta=myRealPathf(fsDir+charF+leafMeta) 
    err, arrDB=parseMeta(fsMeta, charTRes)
    if(err):
      if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
      else: globvar.myConsole.error(err["strTrace"]); return
    
    arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
    arrDBOrg=arrDB;   arrDB=arrDBRelevant
    self.arrDB=arrDB
    self.arrDBNonRelevant=arrDBNonRelevant


        # Check for duplicate ino
    arrTreef.sort(key=lambda x: x["ino"]);   arrDB.sort(key=lambda x: x["ino"])
    arrTreefUniqueIno, objTreeDup, _=extractUniques(arrTreef,"ino")
    arrDBUniqueIno, objDBDup, _=extractUniques(arrDB,"ino")
    lenTreeDup=len(objTreeDup);   lenDBDup=len(objDBDup)
    if(lenTreeDup):
      strTmp='Duplicate ino, in tree:%d (hard links? (Note! hard links are not allowed))' %(lenTreeDup);   globvar.myConsole.error(strTmp);  return
    if(lenDBDup):  strTmp='Duplicate ino, in meta:%d' %(lenDBDup);   globvar.myConsole.error(strTmp);  return

    
    myReporter=MyReporter(settings.StrStemT2M)
    comparisonWID=ComparisonWID('ino', arrTreef, arrDB, strCommandName, myReporter)
    comparisonWID.compare()
    #if(err): globvar.myConsole.error(err["strTrace"]); return
    comparisonWID.format()
    myReporter.writeToFile()

    #[arrTreeUnTouched, arrDBUnTouched, arrTreeChanged, arrDBChanged, arrTreeMetaMatch, arrDBMetaMatch, arrTreeNST, arrDBNST, arrTreeMatchingStrName, arrDBMatchingStrName, arrTreeMatchingId, arrDBMatchingId, arrSourceRem, arrTargetRem]=comparisonWID.getCategoryArrays()

    self.storedArrays=comparisonWID.getCategoryArrays()

    #if(not boSync): return
  def createSyncData(self):  # Calculate hashcodes etc
    strCommandName=self.strCommandName; fsDir=self.fsDir; leafFilterFirst=self.leafFilterFirst; leafMeta=self.leafMeta; flPrepend=self.flPrepend; nPrepend=self.nPrepend; arrDB=self.arrDB; arrDBNonRelevant=self.arrDBNonRelevant
    [arrTreeUnTouched, arrDBUnTouched, arrTreeChanged, arrDBChanged, arrTreeMetaMatch, arrDBMetaMatch, arrTreeNST, arrDBNST, arrTreeMatchingStrName, arrDBMatchingStrName, arrTreeMatchingId, arrDBMatchingId, arrSourceRem, arrTargetRem]=self.storedArrays
    arrCreate, arrDelete = arrSourceRem, arrTargetRem

    arrDBReuse=arrDBUnTouched+arrDBChanged+arrDBMetaMatch+arrDBNST+arrDBMatchingId+arrDBMatchingStrName
    arrTreeReuse=arrTreeUnTouched+arrTreeChanged+arrTreeMetaMatch+arrTreeNST+arrTreeMatchingId+arrTreeMatchingStrName
      # Update:
      #   mtime_ns64: incase lower resolution was used on the old meta-file
      #   strType: incase it was not set in old meta-file
      #   strName:
      #     incase it directory-format (linux or windows) was different in old meta-file
      #     for MetaMatch-cases (changed name)
    arrOutReuse=arrDBReuse
    for i, row in enumerate(arrTreeReuse):
      arrOutReuse[i].update({"mtime_ns64":row["mtime_ns64"], "size":row["size"], "strType":row["strType"], "strName":row["strName"]})   #, "mtime":row["mtime"]


    # Change arrDBChanged
    for i, row in enumerate(arrTreeChanged):
      rowDB=arrDBChanged[i]
      globvar.myConsole.printNL("Calculating hash for changed file: %s" %(row["strName"]))
      strHash=myMD5W(row, fsDir)
      rowDB.update({"strHash":strHash})

      # Rename arrDBMetaMatch (strName is already overwritten above)

      # Change ino of copied file that has been renamed back to origin
    for i, row in enumerate(arrTreeNST):
      rowDB=arrDBNST[i]
      rowDB.update({ "ino":row["ino"]})

      # Matching strName
    for i, row in enumerate(arrTreeMatchingStrName):
      rowDB=arrDBMatchingStrName[i]
      globvar.myConsole.printNL("Calculating hash for deleted+recreated file: %s" %(row["strName"]))
      strHash=myMD5W(row, fsDir)
      rowDB.update({"ino":row["ino"], "strHash":strHash})

      # Matching ino
    for i, row in enumerate(arrTreeMatchingId):
      rowDB=arrDBMatchingId[i]
      globvar.myConsole.printNL("Calculating hash for changed+renamed file: %s" %(row["strName"]))
      strHash=myMD5W(row, fsDir)
      rowDB.update({"strHash":strHash})

        # Remaining
    for i, row in enumerate(arrCreate):
      globvar.myConsole.printNL("Calculating hash for created file: %s" %(row["strName"]))
      strHash=myMD5W(row, fsDir)
      row.update({"strHash":strHash}) #, "uuid":myUUID()


    arrDBNew=arrOutReuse+arrCreate
    
      # Add flPrepend to strName if appropriate
    if(nPrepend>0): 
      for row in arrDBNew: row["strName"]=flPrepend+row["strName"]

      # Add Non-relevant entries
    arrDBNew=arrDBNew+arrDBNonRelevant
    arrDBNew.sort(key=lambda x: x["strName"])

    #for i, row in enumerate(arrDBNew):  if("uuid" not in row): row["uuid"]=myUUID()
    
    #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
    lOld=len(arrDB); lNew=len(arrDBNew); lUntouched=len(arrDBUnTouched); lChanged=len(arrDBChanged); lMetaMatch=len(arrDBMetaMatch); lNST=len(arrDBNST); lMatchingStrName=len(arrDBMatchingStrName); lMatchingId=len(arrDBMatchingId); lCreate=len(arrCreate); lDelete=len(arrDelete)

    boChanged=lChanged!=0 or lMetaMatch!=0 or lNST!=0 or lMatchingStrName!=0 or lMatchingId!=0 or lCreate!=0 or lDelete!=0
    if(not boChanged):
      globvar.myConsole.printNL('Nothing to do, aborting')
      return boChanged

    strFinalWarning=f'Old meta-file had {lOld} entries. The new one will have {lNew} entries: (untouched:{lUntouched}, changed:{lChanged}, metaMatch:{lMetaMatch}, NST:{lNST}, matchingStrName:{lMatchingStrName}, matchingId:{lMatchingId}, created:{lCreate}, deleted:{lDelete})'
    globvar.myConsole.printNL(strFinalWarning)
    globvar.myConsole.printNL('Write to meta-file by clicking "Continue" below ...')
    self.arrDBNew=arrDBNew
    return boChanged
  def makeChanges(self):
    writeMetaFile(self.arrDBNew, self.fsMeta)
    globvar.myConsole.printNL('Done')



class RenameFinishToMeta():
  def __init__(self, **args):
    #fiMeta=args["fiMeta"] if("fiMeta" in args) else args["fiDirSource"]+'/'+settings.leafMeta
    #fiDirSource=args["fiDirSource"]
    #fiMeta=args.get("fiMeta") or fiDirSource+'/'+settings.leafMeta
    fiMeta=args["fiMeta"]
    self.fsMeta=myRealPathf(fiMeta)
    self.charTRes=args["charTRes"]

  def read(self):
    fsMeta=self.fsMeta; charTRes=self.charTRes
  #def renameFinishToMeta(**args): 
      # Parse leafRenameSuggestionsOTO
    err, arrRename=parseRenameInput(settings.arrPath["T2M_renameOTO"])
    if(err): globvar.myConsole.error(err["strTrace"]); return
    arrRename.sort(key=lambda x: x['strOld'])

      # Parse fiMeta
    err, arrDB=parseMeta(fsMeta, charTRes)
    if(err): 
      if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
      else: globvar.myConsole.error(err["strTrace"]); return
    arrDB.sort(key=lambda x: x["strName"])

    arrRenameMatch, arrDBMatch, arrRenameRem, arrDBRem=extractMatching(arrRename, arrDB, ['strOld'], ['strName'])

      # Rename arrDBMatch
    for i, row in enumerate(arrRenameMatch):
      rowDB=arrDBMatch[i]
      rowDB["strName"]=row["strNew"]

    arrDBNew=arrDBRem+arrDBMatch
    arrDBNew.sort(key=lambda x: x["strName"])

    lRename=len(arrRenameMatch)
    boChanged=lRename!=0
    if(not boChanged):
      globvar.myConsole.printNL('Nothing to do, aborting')
      return boChanged
    
    strFinalWarning=f'Writing {len(arrDBNew)} entries to meta-file of which {len(arrRenameMatch)} has changed its name.'
    globvar.myConsole.printNL(strFinalWarning)
    globvar.myConsole.printNL('Write to meta-file by clicking  "Continue" below ...')
    self.arrDBNew=arrDBNew
    return boChanged
  def makeChanges(self):
    arrDBNew=self.arrDBNew; fsMeta=self.fsMeta
    writeMetaFile(arrDBNew, fsMeta)
    globvar.myConsole.printNL('Done')

def renameFinishToMetaByFolder(**args):
  fiMeta=args.fiMeta; charTRes=args.charTRes
    # Parse leafRenameSuggestionsAncestorOnly
  err, arrRename=parseRenameInput(settings.arrPath["T2T_ancestrallyOTORenamedAncestor"], "RelevantAncestor")
  if(err): globvar.myConsole.error(err["strTrace"]); return
  #arrRename.sort(key=lambda x: x['strOld'])

    # Parse fiMeta
  fsMeta=myRealPathf(fiMeta)
  err, arrDB=parseMeta(fsMeta, charTRes)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: globvar.myConsole.error(err["strTrace"]); return
  arrDB.sort(key=lambda x: x["strName"])


  def funVal(val): return val['strOld']
  def funB(rowB, l): return rowB['strName'][:l]
  def funExtra(val): return len(val['strOld'])
  arrRenameMatch, arrDBMatch, arrRenameRem, arrDBRem=extractMatchingOneToManyUnsortedFW(arrRename, arrDB, funVal, funB, funExtra)

  if(len(arrRenameMatch)!=len(arrDBMatch)): globvar.myConsole.error("len(arrRenameMatch)!=len(arrDBMatch)"); return

    # Rename arrDBMatch
  for i, row in enumerate(arrRenameMatch):
    rowDB=arrDBMatch[i]
    strOld=row['strOld']; l=len(strOld);
    rowDB["strName"]=row["strNew"]+rowDB["strName"][l:]

  arrDBNew=arrDBRem+arrDBMatch
  arrDBNew.sort(key=lambda x: x["strName"])
  
  strFinalWarning='Writing %d entries to meta-file. ' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)

  globvar.myConsole.printNL('Done')


#####################################################################################
# check
#####################################################################################

def check(**args):
  # fsDir=myRealPathf(args["fiDir"])
  # leafMeta=args.get("leafMeta", settings.leafMeta)
  # fsMeta=myRealPathf(fsDir+charF+leafMeta) 
  # iStart=int(args["iStart"])
  # charTRes=args["charTRes"]
  #checkHash(fsDir, fsMeta, charTRes, iStart)
  checkInterior(**args)

def checkSummarizeMissing(**args): 
  # fsDir=myRealPathf(args["fiDir"])
  # leafMeta=args.get("leafMeta", settings.leafMeta)
  # fsMeta=myRealPathf(fsDir+charF+leafMeta)
  #checkSummarizeMissingInterior(fsDir, fsMeta)
  checkSummarizeMissingInterior(**args)


#####################################################################################
# T2T
#####################################################################################

def compareTreeToTree(**args):
      # Parse trees
  fsDirSource=myRealPathf(args["fiDirSource"]) 
  fsDirTarget=myRealPathf(args["fiDirTarget"])
  charTRes=args.get("charTRes") or settings.charTRes
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  treeParser=TreeParser()
  err, arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, charTRes, leafFilterFirst)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDirSource}')
    else: globvar.myConsole.error(err["strTrace"])
    return
  err, arrTargetf, arrTargetF =treeParser.parseTree(fsDirTarget, charTRes)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDirTarget}')
    else: globvar.myConsole.error(err["strTrace"])
    return

  strCommandName=sys._getframe().f_code.co_name
  myReporter=MyReporter(settings.StrStemT2T)
  comparisonWOID=ComparisonWOID(arrSourcef, arrTargetf, strCommandName, myReporter)
  comparisonWOID.compare()
  #if(err): globvar.myConsole.error(err["strTrace"]); return
  comparisonWOID.format(fsDirTarget, settings.leafMeta)
  myReporter.writeToFile()


class RenameFinishToTree():
  def __init__(self, boDir=False, strStartToken=None, **args):
    self.fsDir=myRealPathf(args["fiDir"])
    if(args.get("pRenameFile")): pRenameFile=args["pRenameFile"]
    elif(boDir): pRenameFile=settings.arrPath["T2T_ancestrallyOTORenamedAncestor"]
    else: pRenameFile=settings.arrPath["T2T_renameOTO"]
    #if(isinstance(pRenameFile, str)): pRenameFile=pathlib.Path(pRenameFile)
    self.pRenameFile=pRenameFile
    self.strStartToken=strStartToken

  def read(self):
    fsDir=self.fsDir; pRenameFile=self.pRenameFile; strStartToken=self.strStartToken

    err, arrRename=parseRenameInput(pRenameFile, strStartToken)
    if(err): globvar.myConsole.error(err["strTrace"]); return
    arrRename.sort(key=lambda x: x['strOld'])

    lRename=len(arrRename)
    boChanged=lRename!=0
    if(not boChanged):
      globvar.myConsole.printNL('Nothing to do, aborting')
      return boChanged

    n=len(arrRename) #; strPlur='entry' if(n==1) else 'entries'
    strPlur=pluralS(n, 'entry', 'entries')
    strFinalWarning=f'Renaming {n} {strPlur}.'
    globvar.myConsole.printNL(strFinalWarning)
    globvar.myConsole.printNL('Make actual changes to disk by clicking "Continue" below ...')
    self.arrRename=arrRename
    return boChanged
  def makeChanges(self):
    fsDir=self.fsDir; arrRename=self.arrRename
    err=renameFiles(fsDir, arrRename)
    if(err): globvar.myConsole.error(err["strTrace"]); return
    globvar.myConsole.printNL('Done')


class SyncTreeToTreeBrutal():
  def __init__(self, **args):
    self.fsDirSource=myRealPathf(args["fiDirSource"])
    self.fsDirTarget=myRealPathf(args["fiDirTarget"])
    self.charTRes=args.get("charTRes") or settings.charTRes
    self.leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
    #self.leafMeta=args.get("leafMeta", settings.leafMeta)
    #self.flPrepend=args.get("flPrepend") or "";    self.nPrepend=len(self.flPrepend)
  def compare(self):
    fsDirSource=self.fsDirSource; fsDirTarget=self.fsDirTarget; charTRes=self.charTRes; leafFilterFirst=self.leafFilterFirst 
   
      # Parse trees
    treeParser=TreeParser()
    err, arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, charTRes, leafFilterFirst)
    if(err): 
      if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDirSource}')
      else: globvar.myConsole.error(err["strTrace"])
      return
    err, arrTargetf, arrTargetF =treeParser.parseTree(fsDirTarget, charTRes)
    if(err): 
      if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDirTarget}')
      else: globvar.myConsole.error(err["strTrace"])
      return

      # Separate out untouched files
    arrSourcef.sort(key=lambda x: x["strName"]);   arrTargetf.sort(key=lambda x: x["strName"])
    #arrSourceUntouched, arrTargetUntouched, arrSourcefRem, arrTargetfRem=extractMatching(arrSourcef, arrTargetf, ['strName', 'size', 'mtime_ns64Round'])
    arrSourceUntouched, arrTargetUntouched, arrSourcefRem, arrTargetfRem=extractMatching(arrSourcef, arrTargetf, ['strName', 'st'])
    lenSourcef=len(arrSourcefRem); lenTargetf=len(arrTargetfRem)

      # Separate out existing Folders
    arrSourceF.sort(key=lambda x: x["strName"]);   arrTargetF.sort(key=lambda x: x["strName"])
    arrSourceUntouched, arrTargetUntouched, arrSourceFRem, arrTargetFRem=extractMatching(arrSourceF, arrTargetF, ['strName'])
    lenSourceF=len(arrSourceFRem); lenTargetF=len(arrTargetFRem)

    boChanged=lenSourcef!=0 or lenTargetf!=0
    #if(boNothingToDo): globvar.myConsole.printNL('Nothing to do, aborting'); return
    if(not boChanged):
      globvar.myConsole.printNL('Nothing to do, aborting')
      return boChanged

    #arrSourcefRem.sort(key=lambda x:(x["size"], x["mtime_ns64Round"]));   arrTargetfRem.sort(key=lambda x:(x["size"], x["mtime_ns64Round"]))


    arrSourceFRem.sort(key=lambda x: x["strName"])
    arrTargetFRem.sort(key=lambda x: x["strName"], reverse=True)

    strFinalWarning='🗎 Deleting %d file%s.\n🗀 Creating %d folder%s.\n🗎 Writing %d file%s.\n🗀 Deleting %d folder%s.' %(lenTargetf, pluralS(lenTargetf), lenSourceF, pluralS(lenSourceF), lenSourcef, pluralS(lenSourcef), lenTargetF, pluralS(lenTargetF))
    globvar.myConsole.printNL(strFinalWarning)
    globvar.myConsole.printNL('Make actual changes to disk by clicking "Continue" below ...')

    self.arrSourcefRem=arrSourcefRem; self.arrSourceFRem=arrSourceFRem; self.arrTargetfRem=arrTargetfRem;  self.arrTargetFRem=arrTargetFRem;
    return boChanged
  def makeChanges(self):
    fsDirSource=self.fsDirSource; fsDirTarget=self.fsDirTarget;
    arrSourcefRem=self.arrSourcefRem; arrSourceFRem=self.arrSourceFRem; arrTargetfRem=self.arrTargetfRem; arrTargetFRem=self.arrTargetFRem
    myRmFiles(arrTargetfRem, fsDirTarget)
    myMkFolders(arrSourceFRem, fsDirTarget)
    myCopyEntries(arrSourcefRem, fsDirSource, fsDirTarget)
    myRmFolders(arrTargetFRem, fsDirTarget)
    globvar.myConsole.printNL('Done')


def compareTreeToMetaSTOnly(**args):
  fsDir=myRealPathf(args["fiDir"])
  charTRes=args.get("charTRes") or settings.charTRes
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta) 


    # Parse tree
  treeParser=TreeParser()
  err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst)
  removeLeafMetaFromArrTreef(arrTreef, leafMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
    else: globvar.myConsole.error(err["strTrace"])
    return

    # Parse fsMeta
  err, arrDB=parseMeta(fsMeta, charTRes)
  if(err):
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: globvar.myConsole.error(err["strTrace"]); return
  
  flPrepend=args.get("flPrepend") or "";    nPrepend=len(flPrepend)
  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant


  strCommandName=sys._getframe().f_code.co_name
  myReporter=MyReporter(settings.StrStemT2T)
  comparisonWOID=ComparisonWOID(arrTreef, arrDB, strCommandName, myReporter)
  comparisonWOID.compare()
  #if(err): globvar.myConsole.error(err["strTrace"]); return
  comparisonWOID.format(fsDir, fsMeta)
  myReporter.writeToFile()






#######################################################################################
# parseTreeNDump
#######################################################################################
def castToBool(s):
  if(isinstance(s, str)): return s.lower() in ['true', '1', 't', 'y', 'yes']
  elif(isinstance(s, bool)): return s
  return bool(int(s))

def parseTreeNDump(**args):
  fsDir=myRealPathf(args["fiDir"])
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  charTRes=args.get("charTRes") or settings.charTRes

  boUseFilter=castToBool(args["boUseFilter"])
  if(not boUseFilter): leafFilterFirst=None
    # Parse tree
  treeParser=TreeParser()
  err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
    else: globvar.myConsole.error(err["strTrace"])
    return

  arrTreef.sort(key=lambda x: x["strName"]);  

  for row in arrTreef:
    strType=row["strType"]
    #globvar.myConsole.printNL('%s %s %s %s@%s' %(strType, row["ino"], row["mtime_ns64"], row["size"], row["strName"]))
    #strTNS=row["mtime_ns64"] # Challenging testing the reader
    #strTNS=f'{row["mtime_ns64"]:019_}' # Kind to the reader (Canonical)
    strTNS=f'{row["mtime_ns64"]:019}' # Kind to the reader (Canonical)
    globvar.myConsole.printNL(f'{strType} {row["ino"]} {strTNS} {row["size"]}@{row["strName"]}')
  
  globvar.myConsole.printNL('@')
  for row in arrTreeF:
    #globvar.myConsole.printNL('%s %s@%s' %(row["ino"], row["mtime_ns64"], row["strName"]))
    #strTNS=row["mtime_ns64"] # Challenging testing the reader
    #strTNS=f'{row["mtime_ns64"]:019_}' # Kind to the reader (Canonical)
    strTNS=f'{row["mtime_ns64"]:019}' # Kind to the reader (Canonical)
    globvar.myConsole.printNL(f'{row["ino"]} {strTNS}@{row["strName"]}')

  # ~/progPython/buvtpy/buvt.py parseTreeNDump --boUseFilter true --leafFilterFirst .buvt-filter --fiDir "/home/magnus/progPython/buvt-SourceFs/Source"


#######################################################################################
# moveMeta
#######################################################################################
def moveMeta(**args):
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  charTRes=args.get("charTRes") or settings.charTRes

    # Parse fiMetaS
  fsMetaS=myRealPathf(args["fiMetaS"])
  leafMetaS=os.path.basename(fsMetaS)
  err, arrDBS=parseMeta(fsMetaS, charTRes)
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # Parse fiMetaOther
  fsMetaOther=myRealPathf(args["fiMetaOther"])
  leafMetaOther=os.path.basename(fsMetaOther)
  err, arrDBOther=parseMeta(fsMetaOther, charTRes)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDBOther=[]
    else: globvar.myConsole.error(err["strTrace"]); return

    # Parse tree
  fsDir=myRealPathf(args["fiDirT"])
  treeParser=TreeParser()
  err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst)
  removeLeafMetaFromArrTreef(arrTreef, leafMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
    else: globvar.myConsole.error(err["strTrace"])
    return

  flPrepend=args.get("flPrepend") or "";    nPrepend=len(flPrepend)
  arrDBOtherNonRelevant, arrDBOtherRelevant =selectFrArrDB(arrDBOther, flPrepend)
  arrDBOtherOrg=arrDBOther;   arrDBOther=arrDBOtherRelevant

  # arrTreefNonRelevant, arrTreefRelevant =selectFrArrDB(arrTreef, flPrepend)
  # arrTreefOrg=arrTreef;   arrTreef=arrTreefRelevant


  arrTreef.sort(key=lambda x: x["strName"]);   arrDBS.sort(key=lambda x: x["strName"])
  arrTreeMatch, arrDBSMatch, arrTreeRem, arrDBSRem=extractMatching(arrTreef, arrDBS, ['strName'], ['strName'])

  #if(len(arrTreeRem) or len(arrDBRem)): globvar.myConsole.error("len(arrTreeRem) OR len(arrDBRem)"); return
  #if(len(arrTreeRem)): globvar.myConsole.error("len(arrTreeRem)"); return

  for i, rowDBS in enumerate(arrDBSMatch):
    rowTree=arrTreeMatch[i]
    rowDBS["ino"]=rowTree["ino"]

  arrDBOtherNew=arrDBSMatch
  if(nPrepend>0): 
    for row in arrDBOtherNew: row["strName"]=flPrepend+row["strName"]

  arrDBOtherNew=arrDBOtherNonRelevant+arrDBOtherNew
  arrDBOtherNew.sort(key=lambda x: x["strName"])
  strFinalWarning='Writing %d entries to meta-file.' %(len(arrDBOtherNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBOtherNew, fsMetaOther)

def testFilter(**args):
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  charTRes=args.get("charTRes") or settings.charTRes

  fsDirSource=myRealPathf(args["fiDirSource"])
  arrRsf, arrRsF, arrRsOther=getRsyncList(fsDirSource)

  treeParser=TreeParser()
  err, arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, charTRes, leafFilterFirst)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDirSource}')
    else: globvar.myConsole.error(err["strTrace"])
    return

  arrSourcef.sort(key=lambda x:x["strName"])
  arrSourceF.sort(key=lambda x:x["strName"])
  arrRsf.sort(key=lambda x:x["strName"])
  arrRsF.sort(key=lambda x:x["strName"])
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
  globvar.myConsole.printNL('%s and %s written' %(leafResult, leafResultRs))



def convertHashcodeFileToMeta(**args):  # Add inode and create uuid
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  charTRes=args.get("charTRes") or settings.charTRes

  fsMeta=myRealPathf(args["fiMeta"])
  leafMeta=os.path.basename(fsMeta)

    # Parse tree
  fsDir=myRealPathf(args["fiDir"])
  treeParser=TreeParser()
  err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst) # boUseFilter should perhaps be False (although it might be slow)
  removeLeafMetaFromArrTreef(arrTreef, leafMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
    else: globvar.myConsole.error(err["strTrace"])
    return

    # Parse fiHash
  fsHash=myRealPathf(args["fiHash"])
  err, arrDB=parseHashFile(fsHash)
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # fiMeta

  # arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args["flPrepend"])
  # arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef.sort(key=lambda x: x["strName"]);   arrDB.sort(key=lambda x: x["strName"])
  arrTreeMatch, arrDBMatch, arrTreeRem, arrDBRem=extractMatching(arrTreef, arrDB, ['strName'], ['strName'])

  #if(len(arrTreeRem) or len(arrDBRem)): globvar.myConsole.error("len(arrTreeRem) OR len(arrDBRem)"); return
  if(len(arrTreeRem)): globvar.myConsole.error("len(arrTreeRem)"); return

  for i, rowDB in enumerate(arrDBMatch):
    #if("uuid" not in rowDB): rowDB["uuid"]=myUUID() # Add uuid if it doesn't exist
    row=arrTreeMatch[i]
    rowDB["ino"]=row["ino"] # Copy ino

  arrDBNew=arrDBMatch
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  strFinalWarning='Writing %d entries to meta-file. ' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)
  globvar.myConsole.printNL('Done')



def convertMetaToHashcodeFile(**args):   # Add inode and create uuid
    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta, args["charTRes"])
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # Parse fiHash
  fsHash=myRealPathf(args["fiHash"])

  # arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args["flPrepend"])
  # arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrDBNew=arrDB
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  strFinalWarning='Writing %d entries to hash-file.' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeHashFile(arrDBNew, fsHash)
  globvar.myConsole.printNL('Done')




def sortHashcodeFile(**args):
    # Parse fiHash
  fsHash=myRealPathf(args["fiHash"])
  err, arrDB=parseHashFile(fsHash)
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDB.sort(key=lambda x: x["strName"])

  writeHashFile(arrDB, fsHash)
  globvar.myConsole.printNL('Done')


def changeIno(**args):
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  charTRes=args.get("charTRes") or settings.charTRes
  flPrepend=args.get("flPrepend") or ""

  fsDir=myRealPathf(args["fiDir"])

  fsMeta=myRealPathf(args["fiMeta"])
  leafMeta=os.path.basename(fsMeta)

    # Parse tree
  treeParser=TreeParser()
  err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst)
  removeLeafMetaFromArrTreef(arrTreef, leafMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
    else: globvar.myConsole.error(err["strTrace"])
    return

    # Parse fiMeta
  err, arrDB=parseMeta(fsMeta, args["charTRes"])
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef.sort(key=lambda x: x["strName"]);  arrDB.sort(key=lambda x: x["strName"])
  arrTreeMatch, arrDBMatch, arrTreeRem, arrDBRem=extractMatching(arrTreef, arrDB, ['strName'], ['strName'])


  for i, rowDB in enumerate(arrDBMatch):
    rowTree=arrTreeMatch[i]
    #if("uuid" not in rowDB): rowDB["uuid"]=myUUID()
    rowDB["ino"]=rowTree["ino"]

  arrDBNew=arrDBMatch
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  strFinalWarning='Writing %d entries to meta-file.' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)

  globvar.myConsole.printNL('Done')

def utilityMatchTreeAndMeta(**args):    # For running different experiments 
  leafFilterFirst=args.get("leafFilterFirst") or settings.leafFilter
  charTRes=args.get("charTRes") or settings.charTRes
  flPrepend=args.get("flPrepend") or ""

  fsDir=myRealPathf(args["fiDir"])

  fsMeta=myRealPathf(args["fiMeta"])
  leafMeta=os.path.basename(fsMeta)

    # Parse tree
  treeParser=TreeParser()
  err, arrTreef, arrTreeF =treeParser.parseTree(fsDir, charTRes, leafFilterFirst)
  removeLeafMetaFromArrTreef(arrTreef, leafMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): globvar.myConsole.printNL(f'No such folder: {fsDir}')
    else: globvar.myConsole.error(err["strTrace"])
    return

    # Parse fiMeta
  err, arrDB=parseMeta(fsMeta, charTRes)
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef.sort(key=lambda x: x["strName"]);  arrDB.sort(key=lambda x: x["strName"])
  arrTreeMatch, arrDBMatch, arrTreeRem, arrDBRem=extractMatching(arrTreef, arrDB, ['strName'], ['strName'])


  for i, rowDB in enumerate(arrDBMatch):
    rowTree=arrTreeMatch[i]
    #if("uuid" not in rowDB): rowDB["uuid"]=myUUID()
    rowDB["ino"]=rowTree["ino"]

  arrDBNew=arrDB
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  strFinalWarning='Writing %d entries to meta-file.' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)

  globvar.myConsole.printNL('Done')


def utilityMatchMetaAndMeta(**args):    # For running different experiments
  flPrepend=args.get("flPrepend") or ""; nPrepend=len(flPrepend)

    # Parse fiMetaS
  fsMetaS=myRealPathf(args["fiMetaS"])
  err, arrDBS=parseMeta(fsMetaS, args["charTRes"])
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # Parse fiMetaT
  fsMetaT=myRealPathf(args["fiMetaT"])
  err, arrDBT=parseMeta(fsMetaT, args["charTRes"])
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDBTNonRelevant, arrDBTRelevant =selectFrArrDB(arrDBT, flPrepend)
  arrDBTOrg=arrDBT;   arrDBT=arrDBTRelevant


  arrDBS.sort(key=lambda x: x["strName"]);   arrDBT.sort(key=lambda x: x["strName"])
  arrDBSMatch, arrDBTMatch, arrDBSRem, arrDBTRem=extractMatching(arrDBS, arrDBT, ['strName'])

    # Move uuid to arrDBMatch
  # for i, row in enumerate(arrDBSMatch):
  #   rowT=arrDBTMatch[i]
  #   rowT["uuid"]=row["uuid"]

  for i, row in enumerate(arrDBT):
    row["strName"]=flPrepend+row["strName"]

  arrDBNew=arrDBTNonRelevant+arrDBTMatch+arrDBTRem
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  strFinalWarning='Writing %d entries to meta-file.' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMetaT)

  globvar.myConsole.printNL('Done')

def utilityAddToMetaStrName(**args):  # For running different experiments
    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta, args["charTRes"])
  if(err): globvar.myConsole.error(err["strTrace"]); return
  arrDB.sort(key=lambda x: x["strName"])

  flPrepend=args.get("flPrepend") or ""; nPrepend=len(flPrepend)


  #flPrependTmp=flPrepend+charF if(nPrepend) else ""
  for i, row in enumerate(arrDB):
    row["strName"]=flPrepend+row["strName"]
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  strFinalWarning='Writing %d entries to meta-file.' %(len(arrDB))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDB, fsMeta)

  globvar.myConsole.printNL('Done')



def deleteResultFiles():
  #arr=[settings.leafResultMore, settings.leafRenameSuggestionsAncestorOnly, settings.leafDuplicateInitial, settings.leafDuplicateFinal, settings.leafRenameSuggestionsAdditional, settings.leafRenameSuggestionsOTO]
  #arr=["resultMoreT2M", "renameAncestorOnly", "duplicateInitial", "duplicateFinal", "renameAdditional", "renameOTO"]

  for strTmp in StrStemReport:
    p=arrPath[strTmp]
    try: os.remove(p); globvar.myConsole.printNL("Deleted: "+p.name)
    except FileNotFoundError as e:
      globvar.myConsole.error("Couldn't delete: "+p.name)  
