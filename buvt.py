#!/usr/bin/env python

import sys
import argparse
from libMainFunctions import *
from libGUI import *
import settings
import globvar
from libStorage import *
import pathlib


pathlib.Path(settings.flStorageDir).mkdir(parents=True, exist_ok=True)
# Todo:

# A backup strategy can be more or less differential.
# Hard links, do we need them?



#######################################################################################
# main
#######################################################################################

def main():
  tStart=time.time()
  #argv=copy.copy(sys.argv); del argv[0]
  argv=globvar.argv=sys.argv[1:]
  if(len(argv)==0): argv=['gui']

    # boDryRun
  # global boDryRun; boDryRun=False
  # indShort=myIndexOf(argv, '-n')
  # ind=myIndexOf(argv, '--boDryRun')
  # if(indShort>=0 and ind>=0): print("Use -n OR --boDryRun, not both. "); return
  # if(indShort>=0): boDryRun=True; del argv[indShort]
  # if(ind>=0): boDryRun=True; del argv[ind]

    # leafBuvtFilter
  # ind=myIndexOf(argv, '--leafFilterFirst')
  # if(ind>=0):
  #   if(ind+1>=len(argv)): print("--leafFilterFirst should be followed by one more argument"); return
  #   settings.leafFilterFirst=argv[ind+1]; del argv[ind+1]; del argv[ind]

  globvar.modeMain=modeMain=argv[0]
  del argv[0]
  StrModeMain=['gui', 'compareTreeToTree', 'compareTreeToMetaSTOnly', 'syncTreeToTreeBrutal', 
  'compareTreeToMeta', 'syncTreeToMeta', 
  'renameFinishToTree', 'renameFinishToTreeByFolder', 'renameFinishToMeta', 'renameFinishToMetaByFolder',   'parseTreeNDump',
  'moveMeta', 'testFilter', 'convertHashcodeFileToMeta', 'convertMetaToHashcodeFile', 'sortHashcodeFile', 'changeIno', 'utilityMatchTreeAndMeta', 'utilityMatchMetaAndMeta', 'utilityAddToMetaStrName', 'check', 'checkSummarizeMissing', 'deleteResultFiles', 'complete']
  StrModeMainWOComplete=StrModeMain[:-1]
  if(modeMain not in StrModeMain): print("Error: The first argument should be any of: "+', '.join(StrModeMain)); return


  if(modeMain!='gui'): globvar.myConsole=MyConsole()
  
  if(modeMain=='gui'):
    objSTDefault=[{"label":"default", "charTRes":settings.charTRes,
    "fiDirSource":"~", "fiDirTarget":"/run/media/YOUR_USB_DRIVE_OR_WHATEVER",
    "leafFilterFirst":".buvt-filter", "leafFilterFirstTree":""}]  #, "flPrepend":""
    globvar.localStorageST=MyLocalStorage(settings.arrPath["storedST"]);    globvar.localStorageST.getStored(objSTDefault)
    objOtherDefault={"iSelected":0,"iStart":0}
    globvar.localStorageOther=MyLocalStorage(settings.arrPath["storedOther"]);    globvar.localStorageOther.getStored(objOtherDefault)
    root=globvar.root=windowRoot()
    globvar.myConsole=root.myConsole
    globvar.root.mainloop()

    # tkmain = asyncio.ensure_future(tk_main(root))
    # loop = asyncio.get_event_loop()
    # try:
    #   loop.run_forever()
    # except KeyboardInterrupt:
    #   pass

  elif(modeMain=='compareTreeToTree'): 
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--fiDirSource", default='.')
    parser.add_argument('-t', "--fiDirTarget", default='.')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    compareTreeToTree(**argsD)
    #compareTreeToTree(args)
  elif(modeMain=='compareTreeToMetaSTOnly'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    compareTreeToMetaSTOnly(**argsD)
  elif(modeMain=='syncTreeToTreeBrutal'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--fiDirSource", default='.')
    parser.add_argument('-t', "--fiDirTarget", required=True)
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    #syncTreeToTreeBrutal(**argsD)
    syncTreeToTreeBrutal=SyncTreeToTreeBrutal(**argsD)
    syncTreeToTreeBrutal.compare()
    if(settings.boAskBeforeWrite):
      if('pydevd' in sys.modules): breakpoint()
      else: input('Press enter to continue.')
    syncTreeToTreeBrutal.makeChanges()

  elif(modeMain=='compareTreeToMeta' or modeMain=='syncTreeToMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    #syncTreeToMeta(modeMain, **argsD)
    syncTreeToMeta=SyncTreeToMeta(modeMain, **argsD)
    syncTreeToMeta.compare()
    if(modeMain=='compareTreeToMeta'): return
    syncTreeToMeta.createSyncData()
    if(settings.boAskBeforeWrite):
      if('pydevd' in sys.modules): breakpoint()
      else: input('Press enter to continue.')
    syncTreeToMeta.makeChanges()
  
  elif(modeMain=='renameFinishToTree'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", required=True)
    parser.add_argument('-f', "--fiRenameFile")
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    #renameFinishToTree(False, None, **argsD)
    args={"fiDir":argsD["fiDir"], pRenameFile:pathlib.Path(argsD["fiRenameFile"])}
    renameFinishToTree=RenameFinishToTree(False, None, **args)
    renameFinishToTree.read()
    if(settings.boAskBeforeWrite):
      if('pydevd' in sys.modules): breakpoint()
      else: input('Press enter to continue.')
    renameFinishToTree.makeChanges()
  elif(modeMain=='renameFinishToTreeByFolder'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", required=True)
    parser.add_argument('-f', "--leafFile")
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    renameFinishToTree(True, "RelevantAncestor", **argsD)
  elif(modeMain=='renameFinishToMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    #renameFinishToMeta(**argsD)
    renameFinishToMeta=RenameFinishToMeta(**argsD)
    renameFinishToMeta.read()
    if(settings.boAskBeforeWrite):
      if('pydevd' in sys.modules): breakpoint()
      else: input('Press enter to continue.')
    renameFinishToMeta.makeChanges()
  elif(modeMain=='renameFinishToMetaByFolder'):
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    renameFinishToMetaByFolder(**argsD)

  elif(modeMain=='parseTreeNDump'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("--boUseFilter", default=False)
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    parseTreeNDump(**argsD)  # using "fiDir", "leafFilterFirst", "charTRes", "boUseFilter"

  elif(modeMain=='moveMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--fiMetaS", default=settings.leafMeta)
    parser.add_argument("-o", "--fiMetaOther", required=True)
    parser.add_argument("-d", "--fiDirT", required=True)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    moveMeta(**argsD)  # using: "fiMetaS", "fiMetaOther", "fiDirT", "charTRes", "leafFilterFirst", "flPrepend"
  elif(modeMain=='testFilter'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--fiDirSource", default='.')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    testFilter(**argsD)  # "leafFilterFirst", "charTRes", "fiDirSource"
  elif(modeMain=='convertHashcodeFileToMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--fiDir", default='.')
    parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    convertHashcodeFileToMeta(**argsD)  # "leafFilterFirst", "charTRes", "fiDir", "fiHash", "fiMeta", "flPrepend"
  elif(modeMain=='convertMetaToHashcodeFile'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    convertMetaToHashcodeFile(**argsD)
  elif(modeMain=='sortHashcodeFile'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    sortHashcodeFile(**argsD)
  elif(modeMain=='changeIno'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    changeIno(**argsD)  # "leafFilterFirst", "charTRes", "flPrepend", "fiDir", "fiMeta"
  elif(modeMain=='utilityMatchTreeAndMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=settings.leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    utilityMatchTreeAndMeta(**argsD) # "leafFilterFirst", "charTRes", "flPrepend", "fiDir", "fiMeta"
  elif(modeMain=='utilityMatchMetaAndMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--fiMetaS", default=settings.leafMeta)
    parser.add_argument('-t', "--fiMetaT", required=True)
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    utilityMatchMetaAndMeta(**argsD)
  elif(modeMain=='utilityAddToMetaStrName'): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiMeta", default=settings.leafMeta)
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    utilityAddToMetaStrName(**argsD)
  
  elif(modeMain=='check'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=settings.leafMeta)
    parser.add_argument( "--iStart", default=0)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    check(**argsD)
  elif(modeMain=='checkSummarizeMissing'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=settings.leafMeta)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args)
    argsD["charTRes"]=settings.charTRes
    checkSummarizeMissing(**argsD)
  elif(modeMain=='deleteResultFiles'): deleteResultFiles()

  elif(modeMain=='complete'): 
    lenArg=len(argv)
    if(lenArg==0): print('\n'.join(StrModeMainWOComplete)); return
    strIn=argv[0]; lenIn=len(strIn)
    StrModeOut=[]
    for strMode in StrModeMainWOComplete:
      if(strIn==strMode[:lenIn]): StrModeOut.append(strMode)
    print('\n'.join(StrModeOut))


  if(modeMain!='complete' and modeMain!='parseTreeNDump'): 
    tStop=time.time();   print('elapsed time '+str(round((tStop-tStart)*1000))+'ms')



if __name__ == "__main__":
  main()
else:
  pass


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


