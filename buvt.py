#!/usr/bin/env python

import sys
import argparse
from libMainFunctions import *
from libGUI import *
import settings
import globvar
from libStorage import *



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
  
  leafMeta=settings.leafMeta; leafFilter=settings.leafFilter
  dictCharTRes={"charTRes":settings.charTRes}
  if(modeMain=='gui'):
    globvar.localStorageST=MyLocalStorage(settings.flStoredST);    globvar.localStorageST.getStored({"iSelected":0,"iStart":0})
    globvar.localStorageOther=MyLocalStorage(settings.flStoredOther);    globvar.localStorageOther.getStored([])
    root=globvar.root=windowRoot()
    globvar.myConsole=root.myConsole
    globvar.root.mainloop()

  elif(modeMain=='compareTreeToTree'): 
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--fiDirSource", default='.')
    parser.add_argument('-t', "--fiDirTarget", default='.')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    compareTreeToTree(**argsD)
    #compareTreeToTree(args)
  elif(modeMain=='compareTreeToMetaSTOnly'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    compareTreeToMetaSTOnly(**argsD)
  elif(modeMain=='syncTreeToTreeBrutal'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--fiDirSource", default='.')
    parser.add_argument('-t', "--fiDirTarget", required=True)
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    syncTreeToTreeBrutal(**argsD)

  elif(modeMain=='compareTreeToMeta' or modeMain=='syncTreeToMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    syncTreeToMeta(modeMain, **argsD)
  
  elif(modeMain=='renameFinishToTree'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", required=True)
    parser.add_argument('-f', "--leafFile")
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    renameFinishToTree(False, None, **argsD)
  elif(modeMain=='renameFinishToTreeByFolder'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", required=True)
    parser.add_argument('-f', "--leafFile")
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    renameFinishToTree(True, "RelevantAncestor", **argsD)
  elif(modeMain=='renameFinishToMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiMeta", default=leafMeta)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    renameFinishToMeta(**argsD)
  elif(modeMain=='renameFinishToMetaByFolder'):
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiMeta", default=leafMeta)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    renameFinishToMetaByFolder(**argsD)

  elif(modeMain=='parseTreeNDump'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("--boUseFilter", default=False)
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    parseTreeNDump(**argsD)

  elif(modeMain=='moveMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--fiMetaS", default=leafMeta)
    parser.add_argument("-o", "--fiMetaOther", required=True)
    parser.add_argument("-d", "--fiDirT", required=True)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    moveMeta(**argsD)
  elif(modeMain=='testFilter'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--fiDirSource", default='.')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    testFilter(**argsD)
  elif(modeMain=='convertHashcodeFileToMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--fiDir", default='.')
    parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
    parser.add_argument("--fiMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    convertHashcodeFileToMeta(**argsD)
  elif(modeMain=='convertMetaToHashcodeFile'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
    parser.add_argument("--fiMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    convertMetaToHashcodeFile(**argsD)
  elif(modeMain=='sortHashcodeFile'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--fiHash", default='hashcodes.txt')
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    sortHashcodeFile(**argsD)
  elif(modeMain=='changeIno'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("--fiMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    changeIno(**argsD)
  elif(modeMain=='utilityMatchTreeAndMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("--fiMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    parser.add_argument("--leafFilterFirst", default=leafFilter)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    utilityMatchTreeAndMeta(**argsD)
  elif(modeMain=='utilityMatchMetaAndMeta'):
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--fiMetaS", default=leafMeta)
    parser.add_argument('-t', "--fiMetaT", required=True)
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    utilityMatchMetaAndMeta(**argsD)
  elif(modeMain=='utilityAddToMetaStrName'): 
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiMeta", default=leafMeta)
    parser.add_argument("--flPrepend", default='')
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    utilityAddToMetaStrName(**argsD)
  
  elif(modeMain=='check'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=leafMeta)
    parser.add_argument( "--iStart", default=0)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
    check(**argsD)
  elif(modeMain=='checkSummarizeMissing'):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--fiDir", default='.')
    parser.add_argument("-m", "--leafMeta", default=leafMeta)
    args = parser.parse_args(globvar.argv)
    argsD=vars(args) | dictCharTRes
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


