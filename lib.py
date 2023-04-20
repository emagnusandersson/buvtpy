import subprocess
import os
import sys
import traceback
import inspect
import math


def utf8len(s):
  return len(s.encode('utf-8'))
  
def myMD5(strFileName):
  strhash=subprocess.check_output(['md5sum', strFileName])
  return strhash.split(None, 1)[0]

def myErrorStack(strErr):
  exc_type, exc_value, exc_traceback = sys.exc_info()
  res=traceback.extract_stack(inspect.currentframe().f_back, limit=5)
  arr=traceback.format_list(res)
  strT='\n'.join(arr)
  return strT+'\n'+strErr

def bound(value, opt_min=None, opt_max=None):
  if(opt_min != None): value = max(value, opt_min);
  if(opt_max != None): value = min(value, opt_max);
  return value;

def myIndexOf(Arr,val):
  try: ind=Arr.index(val)
  except: ind=-1
  return ind

#######################################################################################
# parseSSV   Parse "space separated data"
#######################################################################################
  #   The header (first line) determines the number of columns. (Header-fields may not contain spaces)
  #   The remaining rows are expected to have at least as many space-separations as the first line.
  #   Last column contains all remaining data of the row (so it may contain spaces (but not newlines))
def parseSSV(fsDBFile):  
  try: fi=open(fsDBFile,'r')
  except FileNotFoundError as e:
    return {"e":e, "strTrace":myErrorStack(e.strerror)}, None    #"strErr":e.strerror, 
  strData=fi.read(); fi.close()
  arrOut=[]
  arrInp=strData.split('\n')

  nData=len(arrInp)
  if(nData<=1): return None,  []

  strHead=arrInp[0].strip()
  arrCol=strHead.split(None)
  nCol=len(arrCol)
  nSplit=nCol-1

  for strRow in arrInp[1:]:
    strRow=strRow.strip()
    if(len(strRow)==0): continue
    if(strRow.startswith('#')): continue
    arrPart=strRow.split(None, nSplit)
    obj={}
    for i, strCol in enumerate(arrCol): obj[strCol]=arrPart[i]
    arrOut.append(obj)
  
  return None, arrOut


#######################################################################################
# formatColumnData
#######################################################################################
def createFormatInfo(arrKey, objType={}):
  for key in arrKey:
    if(key[:2]=='bo' and key[2].isupper()): strType='boolean'
    elif(key[:3]=='int' and key[3].isupper()): strType='number'
    elif(key[0]=='n' and key[1].isupper()): strType='number'
    elif(key[0]=='t' and key[1].isupper()): strType='number'
    else: strType='string'
    objType[key]=strType
  return objType

def formatColumnData(arrData, objType):
  for iRow, row in enumerate(arrData):
    for key, val in row.items():
      if(key not in objType): pass
      elif(objType[key]=='boolean'): val=val.lower()=='true'
      elif(objType[key]=='number'): val=int(val)
      row[key]=val
# objType=createFormatInfo([*arrDB[0]]);   objType.update({"size":"number", "ino":"number", "mtime":"number", "inode0":"number"})

  

def calcFileNameWithCounter(filename):  # Example calcFileNameWithCounter("file{}.pdf")
  counter = 0
  #filename = "file{}.pdf"
  ind=filename.find('.')
  filenameProt=mySplice(filename, "{}", ind)
  while os.path.isfile(filenameProt.format(counter)):
    counter += 1
  filenameN = filenameProt.format(counter)
  return filenameN

def mySplice(source_str, insert_str, pos):
  return source_str[:pos]+insert_str+source_str[pos:]





def formatTDiff(tDiff):
  boPos=True if(tDiff>0) else False
  tDiffAbs=abs(tDiff)
  tDay=math.floor(tDiffAbs/86400)
  ttmp=tDiffAbs%86400         # number of seconds into current day
  tHour=math.floor(ttmp/3600) # number of hours into current day
  #
  ttmp=ttmp%3600              # number of seconds into current hour
  tMin=math.floor(ttmp/60)    # number of minutes into current hour
  #
  ttmp=ttmp%60                # number of seconds into current minute (float)
  tSec=math.floor(ttmp)       # number of seconds into current minute (int)
  #
  ttmp=ttmp%1                 # number of seconds into current second (0<=ttmp<1)
  tFrac=ttmp
  ttmp=ttmp*1000              # number of ms into current second (float)
  tms=math.floor(ttmp)        # number of ms into current second (int)
  #
  ttmp=ttmp%1                 # number of ms into current ms (0<=ttmp<1)
  ttmp=ttmp*1000              # number of us into current ms (float)
  tus=math.floor(ttmp)        # number of us into current us (int)
  #
  ttmp=ttmp%1                 # number of us into current us (0<=ttmp<1)
  ttmp=ttmp*1000              # number of ns into current us (float)
  #tns=math.floor(ttmp)        # number of ns into current us (int)
  tns=ttmp
  #
  return tDay,tHour,tMin,tSec,tms,tus,tns
  #return tDay,tHour,tMin,tSec,tFrac

def formatTDiffStr(tDiff):
  tDay,tHour,tMin,tSec,tms,tus,tns=formatTDiff(tDiff)
  #tDay,tHour,tMin,tSec,tFrac=formatTdiff(tDiff)
  return "%d %02d:%02d:%02d.%03d %03d %03d" %(tDay,tHour,tMin,tSec,tms,tus,tns)
  #return "%d %d:%d:%d.%s" %(tDay,tHour,tMin,tSec,tFrac)


######################################

def my_bisect_right(a, x, lo=0, hi=None, *, key=None, argExtra=None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e <= x, and all e in
    a[i:] have e > x.  So if x already appears in the list, a.insert(i, x) will
    insert just after the rightmost x already there.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    if key is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if x < a[mid]:
                hi = mid
            else:
                lo = mid + 1
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            #if x < key(a[mid]):
            #     hi = mid
            # else:
            #     lo = mid + 1
            if key(x, a[mid], argExtra)>0:
                hi = mid
            else:
                lo = mid + 1
    return lo


def my_bisect_left(a, x, lo=0, hi=None, *, key=None, argExtra=None):
    """Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
    insert just before the leftmost x already there.
    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    if key is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            #if key(a[mid]) < x:
            #     lo = mid + 1
            # else:
            #     hi = mid
            if key(x, a[mid], argExtra)>=0:
                hi = mid
            else:
                lo = mid + 1
    return lo
