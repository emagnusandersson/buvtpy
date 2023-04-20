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

# T\S    Null    One     Many
# Null           Created Created
# One    Deleted OTO     MTO
# Many   Deleted OTM     MTM


# Changed, Deleted, Created are written in resultCompare.txt

#####################################################################




def hardLinkCheck(**args):  #fiDirSource, leafFilterFirst=leafFilter):
  fsDirSource=myRealPathf(args["fiDirSource"]) 
  treeParser=TreeParser(args["charTRes"])
  arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, True, args["leafFilterFirst"])

  arrSourcef=sorted(arrSourcef, key=lambda x: x["ino"]);   arrSourceF=sorted(arrSourceF, key=lambda x: x["ino"])

  arrUniq, objDupf, arrUniqifiedf=extractUniques(arrSourcef,"ino")
  arrUniq, objDupF, arrUniqifiedF=extractUniques(arrSourceF,"ino")
  Str=[]
  Str.append(f"Hard linked files (inodes with multiple names): {len(objDupf)}")
  Str.append(f"(inodes: {len(arrUniqifiedf)}, filenames: {len(arrSourcef)}), ")
  Str.append(f"Hard linked folders (inodes with multiple names): {len(objDupF)}")
  Str.append(f"(inodes: {len(arrUniqifiedF)}, dirnames: {len(arrSourceF)}) ")
  globvar.myConsole.printNL('\n'.join(Str))


def compareTreeToTree(**args):
      # Parse trees
  fsDirSource=myRealPathf(args["fiDirSource"]) 
  fsDirTarget=myRealPathf(args["fiDirTarget"])
  treeParser=TreeParser(args["charTRes"])
  arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, True, args["leafFilterFirst"])
  arrTargetf, arrTargetF =treeParser.parseTree(fsDirTarget, False)

  comparisonWOID=ComparisonWOID(arrSourcef, arrTargetf)
  comparisonWOID.compare()
  #if(err): globvar.myConsole.error(err["strTrace"]); return
  strCommandName=sys._getframe().f_code.co_name
  [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional]=comparisonWOID.format(strCommandName, fsDirTarget, settings.leafMeta)
  writeResultInfo(StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional)


def compareTreeToMetaSTOnly(**args):
    # Parse tree
  fsDir=myRealPathf(args["fiDir"])
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, True, args["leafFilterFirst"])

    # Parse fsMeta
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta) 
  err, arrDB=parseMeta(fsMeta)
  if(err):
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: globvar.myConsole.error(err["strTrace"]); return
  
  flPrepend=args["flPrepend"];    nPrepend=len(flPrepend)
  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant


  comparisonWOID=ComparisonWOID(arrTreef, arrDB)
  comparisonWOID.compare()
  #if(err): globvar.myConsole.error(err["strTrace"]); return
  strCommandName=sys._getframe().f_code.co_name
  [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional]=comparisonWOID.format(strCommandName, fsDir, fsMeta)
  writeResultInfo(StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd, StrDuplicateInitial, StrDuplicateFinal, StrRenameAdditional)


def syncTreeToTreeBrutal(**args):

  fsDirSource=myRealPathf(args["fiDirSource"])
  fsDirTarget=myRealPathf(args["fiDirTarget"])
    # Parse trees
  treeParser=TreeParser(args["charTRes"])
  arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, True, args["leafFilterFirst"])
  arrTargetf, arrTargetF =treeParser.parseTree(fsDirTarget, False)

    # Separate out untouched files
  arrSourcef=sorted(arrSourcef, key=lambda x: x["strName"]);   arrTargetf=sorted(arrTargetf, key=lambda x: x["strName"])
  arrSourceUntouched, arrTargetUntouched, arrSourcefRem, arrTargetfRem=extractMatching(arrSourcef, arrTargetf, ['strName', 'size', 'mtime'])
  lenSourcef=len(arrSourcefRem); lenTargetf=len(arrTargetfRem)

    # Separate out existing Folders
  arrSourceF=sorted(arrSourceF, key=lambda x: x["strName"]);   arrTargetF=sorted(arrTargetF, key=lambda x: x["strName"])
  arrSourceUntouched, arrTargetUntouched, arrSourceFRem, arrTargetFRem=extractMatching(arrSourceF, arrTargetF, ['strName'])
  lenSourceF=len(arrSourceFRem); lenTargetF=len(arrTargetFRem)

  #if(lenSourcef==0 and lenTargetf==0): globvar.myConsole.printNL('Nothing to do, aborting'); return

  #arrSourcefRem=sorted(arrSourcefRem, key=lambda x:(x["size"], x["mtime"]));   arrTargetfRem=sorted(arrTargetfRem, key=lambda x:(x["size"], x["mtime"]))


  arrSourceFRem=sorted(arrSourceFRem, key=lambda x: x["strName"])
  arrTargetFRem=sorted(arrTargetFRem, key=lambda x: x["strName"], reverse=True)

  strFinalWarning='🗎 Deleting %d file(s).\n🗀 Creating %d folder(s).\n🗎 Creating (copying) %d file(s).\n🗀 Deleting %d folder(s).' %(lenTargetf, lenSourceF, lenSourcef, lenTargetF)
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  myRmFiles(arrTargetfRem, fsDirTarget)
  myMkFolders(arrSourceFRem, fsDirTarget)
  myCopyEntries(arrSourcefRem, fsDirSource, fsDirTarget)
  myRmFolders(arrTargetFRem, fsDirTarget)











#####################################################################################
# syncTreeToMeta
#####################################################################################

def syncTreeToMeta(strCommandName, **args):
  boSync=strCommandName=='syncTreeToMeta'
  
    # Parse tree
  fsDir=myRealPathf(args["fiDir"])
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, True, args["leafFilterFirst"])

    # Parse fsMeta
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta) 
  err, arrDB=parseMeta(fsMeta)
  if(err):
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: globvar.myConsole.error(err["strTrace"]); return
  
  flPrepend=args["flPrepend"];    nPrepend=len(flPrepend)
  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, flPrepend)
  arrDBOrg=arrDB;   arrDB=arrDBRelevant


      # Check for duplicate ino
  arrTreef=sorted(arrTreef, key=lambda x: x["ino"]);   arrDB=sorted(arrDB, key=lambda x: x["ino"])
  arrTreefUniqueIno, objTreeDup, _=extractUniques(arrTreef,"ino")
  arrDBUniqueIno, objDBDup, _=extractUniques(arrDB,"ino")
  lenTreeDup=len(objTreeDup);   lenDBDup=len(objDBDup)
  if(lenTreeDup):
    strTmp='Duplicate ino, in tree:%d (hard links? (Note! hard links are not allowed))' %(lenTreeDup);   globvar.myConsole.error(strTmp);  return
  if(lenDBDup):  strTmp='Duplicate ino, in meta:%d' %(lenDBDup);   globvar.myConsole.error(strTmp);  return


  comparisonWID=ComparisonWID('ino', arrTreef, arrDB)
  comparisonWID.compare()
  #if(err): globvar.myConsole.error(err["strTrace"]); return
  [StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd]=comparisonWID.format(strCommandName, fsDir, fsMeta)
  writeResultInfo(StrScreen, StrResultFile, StrRenameOTO, StrRenameAncestorOnly, StrRenameAncestorOnlyCmd)

  [arrTreeUnTouched, arrDBUnTouched, arrTreeChanged, arrDBChanged, arrTreeMetaMatch, arrDBMetaMatch, arrTreeNST, arrDBNST, arrTreeMatchingStrName, arrDBMatchingStrName, arrTreeMatchingId, arrDBMatchingId, arrSourceRem, arrTargetRem]=comparisonWID.getCategoryArrays()

  arrCreate, arrDelete = arrSourceRem, arrTargetRem
  #boAllOK=len(arrCreate)==0 and len(arrDelete)==0
  #if(boAllOK): globvar.myConsole.printNL('No changes, aborting'); return
  if(not boSync): return

  arrDBReuse=arrDBUnTouched+arrDBChanged+arrDBMetaMatch+arrDBNST+arrDBMatchingId+arrDBMatchingStrName
  arrTreeReuse=arrTreeUnTouched+arrTreeChanged+arrTreeMetaMatch+arrTreeNST+arrTreeMatchingId+arrTreeMatchingStrName
    # Update:
    #   mtime_ns: incase lower resolution was used on the old meta-file
    #   strType: incase it was not set in old meta-file
    #   strName:
    #     incase it directory-format (linux or windows) was different in old meta-file
    #     for MetaMatch-cases (changed name)
  arrOutReuse=arrDBReuse
  for i, row in enumerate(arrTreeReuse):
    arrOutReuse[i].update({"mtime_ns":row["mtime_ns"], "mtime":row["mtime"], "size":row["size"], "strType":row["strType"], "strName":row["strName"]})  


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
  arrDBNew=sorted(arrDBNew, key=lambda x: x["strName"])

  #for i, row in enumerate(arrDBNew):  if("uuid" not in row): row["uuid"]=myUUID()
  
  #if(boDryRun): globvar.myConsole.printNL("(Dry run) exiting"); return
  lOld=len(arrDB); lNew=len(arrDBNew); lUntouched=len(arrDBUnTouched); lChanged=len(arrDBChanged); lMetaMatch=len(arrDBMetaMatch); lNST=len(arrDBNST); lMatchingStrName=len(arrDBMatchingStrName); lMatchingId=len(arrDBMatchingId); lCreate=len(arrCreate); lDelete=len(arrDelete)
  strFinalWarning=f'Old meta-file had {lOld} entries. The new one will have {lNew} entries: (untouched:{lUntouched}, changed:{lChanged}, metaMatch:{lMetaMatch}, NST:{lNST}, matchingStrName:{lMatchingStrName}, matchingId:{lMatchingId}, created:{lCreate}, deleted:{lDelete})'
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)




#####################################################################################
# renameFinish functions
#####################################################################################

def renameFinishToTree(boDir=False, strStartToken=None, **args):  # strStartToken is None (is defaulted to MatchingData) or RelevantAncestor
  fsRenameFold=myRealPathf(args["fiDir"])

  if(args["leafFile"]): leafFile=args["leafFile"]
  elif(boDir): leafFile=settings.leafRenameSuggestionsAncestorOnly
  else: leafFile=settings.leafRenameSuggestionsOTO
  #fsFile=myRealPathf(leafFile)
  

  err, arrRename=parseRenameInput(leafFile, strStartToken)
  if(err): globvar.myConsole.error(err["strTrace"]); return
  arrRename=sorted(arrRename, key=lambda x: x['strOld'])

  strFinalWarning=f'Renaming {len(arrRename)} entry/entries.'
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  err=renameFiles(fsRenameFold, arrRename)
  if(err): globvar.myConsole.error(err["strTrace"]); return
  return


def renameFinishToMeta(**args): 
    # Parse leafRenameSuggestionsOTO
  err, arrRename=parseRenameInput(settings.leafRenameSuggestionsOTO)
  if(err): globvar.myConsole.error(err["strTrace"]); return
  arrRename=sorted(arrRename, key=lambda x: x['strOld'])

    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: globvar.myConsole.error(err["strTrace"]); return
  arrDB=sorted(arrDB, key=lambda x: x["strName"])

  arrRenameMatch, arrDBMatch, arrRenameRem, arrDBRem=extractMatching(arrRename, arrDB, ['strOld'], ['strName'])

    # Rename arrDBMatch
  for i, row in enumerate(arrRenameMatch):
    rowDB=arrDBMatch[i]
    rowDB["strName"]=row["strNew"]

  arrDBNew=arrDBRem+arrDBMatch
  arrDBNew=sorted(arrDBNew, key=lambda x: x["strName"])
  
  strFinalWarning=f'Writing {len(arrDBNew)} entries to meta-file of which {len(arrRenameMatch)} has changed its name.'
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite): 
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)

  globvar.myConsole.printNL('done')

def renameFinishToMetaByFolder(**args):
    # Parse leafRenameSuggestionsAncestorOnly
  err, arrRename=parseRenameInput(settings.leafRenameSuggestionsAncestorOnly, "RelevantAncestor")
  if(err): globvar.myConsole.error(err["strTrace"]); return
  #arrRename=sorted(arrRename, key=lambda x: x['strOld'])

    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDB=[]
    else: globvar.myConsole.error(err["strTrace"]); return
  arrDB=sorted(arrDB, key=lambda x: x["strName"])


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
  arrDBNew=sorted(arrDBNew, key=lambda x: x["strName"])
  
  strFinalWarning='Writing %d entries to meta-file. ' %(len(arrDBNew))
  globvar.myConsole.printNL(strFinalWarning)
  if(settings.boAskBeforeWrite):
    if('pydevd' in sys.modules): breakpoint()
    else:
      globvar.myConsole.printNL(settings.strMessPressEnter)
      print(strFinalWarning)
      input('Press enter to continue.')
  writeMetaFile(arrDBNew, fsMeta)

  globvar.myConsole.printNL('done')


#######################################################################################
# parseTreeNDump
#######################################################################################
def castToBool(s):
  if(isinstance(s, str)): return s.lower() in ['true', '1', 't', 'y', 'yes']
  elif(isinstance(s, bool)): return s
  return bool(int(s))

def parseTreeNDump(**args):
  fsDir=myRealPathf(args["fiDir"])

  boUseFilter=castToBool(args["boUseFilter"])
    # Parse tree
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, boUseFilter, args["leafFilterFirst"])

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);  

  for row in arrTreef:
    strType=row["strType"]
    globvar.myConsole.printNL('%s %s %s %s@%s' %(strType, row["ino"], row["mtime_ns"], row["size"], row["strName"]))
  
  globvar.myConsole.printNL('@')
  for row in arrTreeF:
    globvar.myConsole.printNL('%s %s@%s' %(row["ino"], row["mtime_ns"], row["strName"]))

  


#######################################################################################
# moveMeta
#######################################################################################
def moveMeta(**args):
    # Parse fiMetaS
  fsMetaS=myRealPathf(args["fiMetaS"])
  err, arrDBS=parseMeta(fsMetaS)
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # Parse fiMetaOther
  fsMetaOther=myRealPathf(args["fiMetaOther"])
  err, arrDBOther=parseMeta(fsMetaOther)
  if(err): 
    if(err["e"].errno==errno.ENOENT): err=None; arrDBOther=[]
    else: globvar.myConsole.error(err["strTrace"]); return

    # Parse tree
  fsDir=myRealPathf(args["fiDirT"])
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, True, args["leafFilterFirst"])

  flPrepend=args["flPrepend"];    nPrepend=len(flPrepend)
  arrDBOtherNonRelevant, arrDBOtherRelevant =selectFrArrDB(arrDBOther, flPrepend)
  arrDBOtherOrg=arrDBOther;   arrDBOther=arrDBOtherRelevant

  # arrTreefNonRelevant, arrTreefRelevant =selectFrArrDB(arrTreef, flPrepend)
  # arrTreefOrg=arrTreef;   arrTreef=arrTreefRelevant


  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);   arrDBS=sorted(arrDBS, key=lambda x: x["strName"])
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
  arrDBOtherNew=sorted(arrDBOtherNew, key=lambda x: x["strName"])
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
  fsDirSource=myRealPathf(args["fiDirSource"])
  arrRsf, arrRsF, arrRsOther=getRsyncList(fsDirSource)

  treeParser=TreeParser(args["charTRes"])
  arrSourcef, arrSourceF =treeParser.parseTree(fsDirSource, True, args["leafFilterFirst"])

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
  globvar.myConsole.printNL('%s and %s written' %(leafResult, leafResultRs))



def convertHashcodeFileToMeta(**args):  # Add inode and create uuid
    # Parse tree
  fsDir=myRealPathf(args["fiDir"])
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, True, args["leafFilterFirst"]) # boUseFilter should perhaps be False (although it might be slow)

    # Parse fiHash
  fsHash=myRealPathf(args["fiHash"])
  err, arrDB=parseHashFile(fsHash)
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # fiMeta
  fsMeta=myRealPathf(args["fiMeta"])

  # arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args["flPrepend"])
  # arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);   arrDB=sorted(arrDB, key=lambda x: x["strName"])
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
  globvar.myConsole.printNL('done')



def convertMetaToHashcodeFile(**args):   # Add inode and create uuid
    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta)
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
  globvar.myConsole.printNL('done')




def sortHashcodeFile(**args):
    # Parse fiHash
  fsHash=myRealPathf(args["fiHash"])
  err, arrDB=parseHashFile(fsHash)
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDB=sorted(arrDB, key=lambda x: x["strName"])

  writeHashFile(arrDB, fsHash)
  globvar.myConsole.printNL('done')


def changeIno(**args):
  fsDir=myRealPathf(args["fiDir"])

    # Parse tree
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, True, args["leafFilterFirst"])

    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta)
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args["flPrepend"])
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);  arrDB=sorted(arrDB, key=lambda x: x["strName"])
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

  globvar.myConsole.printNL('done')

def utilityMatchTreeAndMeta(**args):    # For running different experiments 
  fsDir=myRealPathf(args["fiDir"])

    # Parse tree
  treeParser=TreeParser(args["charTRes"])
  arrTreef, arrTreeF =treeParser.parseTree(fsDir, True, args["leafFilterFirst"])

    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta)
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDBNonRelevant, arrDBRelevant =selectFrArrDB(arrDB, args["flPrepend"])
  arrDBOrg=arrDB;   arrDB=arrDBRelevant

  arrTreef=sorted(arrTreef, key=lambda x: x["strName"]);  arrDB=sorted(arrDB, key=lambda x: x["strName"])
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

  globvar.myConsole.printNL('done')


def utilityMatchMetaAndMeta(**args):    # For running different experiments

    # Parse fiMetaS
  fsMetaS=myRealPathf(args["fiMetaS"])
  err, arrDBS=parseMeta(fsMetaS)
  if(err): globvar.myConsole.error(err["strTrace"]); return

    # Parse fiMetaT
  fsMetaT=myRealPathf(args["fiMetaT"])
  err, arrDBT=parseMeta(fsMetaT)
  if(err): globvar.myConsole.error(err["strTrace"]); return

  arrDBTNonRelevant, arrDBTRelevant =selectFrArrDB(arrDBT, args["flPrepend"])
  arrDBTOrg=arrDBT;   arrDBT=arrDBTRelevant


  arrDBS=sorted(arrDBS, key=lambda x: x["strName"]);   arrDBT=sorted(arrDBT, key=lambda x: x["strName"])
  arrDBSMatch, arrDBTMatch, arrDBSRem, arrDBTRem=extractMatching(arrDBS, arrDBT, ['strName'])

    # Move uuid to arrDBMatch
  # for i, row in enumerate(arrDBSMatch):
  #   rowT=arrDBTMatch[i]
  #   rowT["uuid"]=row["uuid"]

  for i, row in enumerate(arrDBT):
    row["strName"]=args["flPrepend"]+row["strName"]

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

  globvar.myConsole.printNL('done')

def utilityAddToMetaStrName(**args):  # For running different experiments
    # Parse fiMeta
  fsMeta=myRealPathf(args["fiMeta"])
  err, arrDB=parseMeta(fsMeta)
  if(err): globvar.myConsole.error(err["strTrace"]); return
  arrDB=sorted(arrDB, key=lambda x: x["strName"])

  flPrepend=args["flPrepend"]; nPrepend=len(flPrepend)


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

  globvar.myConsole.printNL('done')


def check(**args):
  fsDir=myRealPathf(args["fiDir"])
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta) 
  iStart=int(args["iStart"])
  checkHash(fsMeta, fsDir, iStart)

def checkSummarizeMissing(**args): 
  fsDir=myRealPathf(args["fiDir"])
  leafMeta=args.get("leafMeta", settings.leafMeta)
  fsMeta=myRealPathf(fsDir+charF+leafMeta) 
  checkSummarizeMissingInterior(fsMeta, fsDir)

def deleteResultFiles(): 
  arr=[settings.leafResultCompare, settings.leafRenameSuggestionsAncestorOnly, settings.leafDuplicateInitial, settings.leafDuplicateFinal, settings.leafRenameSuggestionsAdditional, settings.leafRenameSuggestionsOTO]
  for leafTmp in arr:
    try: os.remove(leafTmp); globvar.myConsole.printNL("Deleted: "+leafTmp)
    except FileNotFoundError as e:
      globvar.myConsole.error("Couldn't delete: "+leafTmp)  
