
import pathlib
#from platformdirs import *
appname = "buvt"
appauthor = "Gavott"
from platformdirs import PlatformDirs
dirs = PlatformDirs(appname, appauthor)

boAskBeforeWrite=True
IntTDiv={'n':1e9, 'u':1e6, 'm':1e3}
charTRes='u'  # 'n', 'u', 'm', '1' or '2'

boIncludeLinks=True

leafFilter=".buvt-filter"
leafMeta="buvt-meta.txt"

flStorageDir='.storage'
flStorageDir=dirs.user_data_dir



StrStemStored=["storedOther", "storedST"]
StrStemT2M=["T2M_sum", "T2M_HL", "T2M_resultMore", "T2M_renameOTO"]
StrStemT2T=["T2T_sum",
"T2T_resultMore",
"T2T_renameOTO",
"T2T_ancestrallyOTORenamedAncestor",
"T2T_renameDuplicateInitial",
"T2T_renameDuplicateFinal",
"T2T_renameAdditional"] 

LeafFileStored=[]
for strStem in StrStemStored: LeafFileStored.append(strStem+'.json')

LeafFileT2M=[]
for strStem in StrStemT2M: LeafFileT2M.append(strStem+'.txt')

LeafFileT2T=[]
for strStem in StrStemT2T: LeafFileT2T.append(strStem+'.txt')


LeafFile=LeafFileStored+LeafFileT2M+LeafFileT2T
StrStem=[]

arrPath={}
for leafFile in LeafFile:
  fsTmp=flStorageDir+'/'+leafFile
  p=pathlib.Path(fsTmp)
  stem=p.stem
  StrStem.append(stem)
  arrPath[stem]=p



myConsole=None


strMessPressEnter='Press enter (not here, but in the console from where the program was started) to continue. (Sorry for the awkward interface, a popupbox would have been more suitable. Perhaps it will come in future versions.)'
