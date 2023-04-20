
import bisect
import copy
from lib import *


#######################################################################################
# extractMatching
#   Each row must be unique with respect to the properties (given in arrKeyA/arrKeyB).
#     That is no row of arrA (or arrB) can equal an other row of arrA (or arrB) when viewed through the properites (given in arrKeyA/arrKeyB).
#       Ex: arrA[0][arrKeyA[0]] can be equal to arrA[1][arrKeyA[0]] but not all properties of arrKeyA in arrA[0] and arrA[1] can be equal.
#   arrA/arrB must be sorted (in an acending order) with respect to the keys (given in arrKeyA/arrKeyB).
#   The elements of arrKeyA/arrKeyB have falling priority.
#######################################################################################

def extractMatchingF(arrA, arrB, fun): 
  iA=0; iB=0
  lenA=len(arrA); lenB=len(arrB)
  arrAMatching=[]; arrBMatching=[]
  arrARem=[]; arrBRem=[]
  while(1):
    boEndA=iA==lenA; boEndB=iB==lenB
    if(boEndA and not boEndB): arrBRem.extend(arrB[iB:]); break
    elif(not boEndA and  boEndB): arrARem.extend(arrA[iA:]); break
    elif(boEndA and  boEndB): break
    rowA=arrA[iA]; rowB=arrB[iB]
    intVal=fun(rowA,rowB)
    if(intVal>0): arrARem.append(rowA); iA+=1     # The row exist in arrA but not in arrB
    elif(intVal<0): arrBRem.append(rowB); iB+=1   # The row exist in arrB but not in arrA
    elif(intVal==0): arrAMatching.append(rowA); arrBMatching.append(rowB); iB+=1; iA+=1
    else: print("error when comparing strings")
  return arrAMatching, arrBMatching, arrARem, arrBRem

def extractMatching(arrA, arrB, arrKeyA, arrKeyB=None):
  if(arrKeyB==None): arrKeyB=arrKeyA
  lenKeyA=len(arrKeyA);  lenKeyB=len(arrKeyB);  
  if(lenKeyA!=lenKeyB):  print("lenKeyA!=lenKeyB"); return 
  if(lenKeyA==0 or lenKeyB==0):  print("lenKeyA==0 or lenKeyB==0"); return

  lenA=len(arrA); lenB=len(arrB)
  boADict=isinstance(arrA[0], dict) if(lenA) else False 
  boBDict=isinstance(arrB[0], dict) if(lenB) else False 
  def fun(rowA,rowB):
    for j, key in enumerate(arrKeyA):
      keyB=arrKeyB[j]
      vA=rowA[key] if boADict else getattr(rowA, key)
      vB=rowB[keyB] if boBDict else getattr(rowB, keyB)
      if(vA<vB): return 1
      elif(vA>vB): return -1
    return 0
  return extractMatchingF(arrA, arrB, fun)

#extractMatchingF([3,6,9], [2,3,8], funInt)


      # An arrA element may match multiple arrB elements (but not the other way around)
      # arrA may be unsorted (arrB must be sorted)
def extractMatchingOneToManyUnsortedF(arrA, arrB, funVal, funB, funExtra):
  lenA=len(arrA); lenB=len(arrB)
  arrBWork=copy.copy(arrB)
  arrAMatching=[]; arrBMatching=[]
  arrARem=[];  # arrBRem=[]
  for rowA in arrA:
    lenBWork=len(arrBWork)
    #l=len(rowA['strOld']); x['strName'][:l]
    valA=funVal(rowA) if(funVal) else rowA
    argExtra=funExtra(rowA)
    # iBStart = bisect.bisect_left(arrBWork, rowA['strOld'], 0, lenB, key=lambda x: x['strName'][:l])
    # iBEnd = bisect.bisect_right(arrBWork, rowA['strOld'], iBStart, lenB, key=lambda x: x['strName'][:l])
    iBStart = my_bisect_left(arrBWork, valA, 0, lenBWork, key=funB, argExtra=argExtra)
    iBEnd = my_bisect_right(arrBWork, valA, iBStart, lenBWork, key=funB, argExtra=argExtra)
    if(iBStart!=iBEnd):
      arrAMatching.append(rowA);  arrBMatching.append(arrBWork[iBStart:iBEnd]); arrBWork=arrBWork[:iBStart]+arrBWork[iBEnd:]
    else: arrARem.append(rowA);
  arrBRem=arrBWork
  return arrAMatching, arrBMatching, arrARem, arrBRem
  
# l=len()
# def fun(x): return x['strName'][:l]

def extractMatchingOneToManyUnsortedFW(arrA, arrB, funVal, funB, funExtra):
  arrAMatching, arrBMatching, arrARem, arrBRem=extractMatchingOneToManyUnsortedF(arrA, arrB, funVal, funB, funExtra)
  arrAMatchingMod=[]; arrBMatchingMod=[]
  for i, row in enumerate(arrAMatching):
    rowB=arrBMatching[i]; l=len(rowB)
    arrAMatchingMod.extend([row]*l)
    arrBMatchingMod.extend(rowB)
  return arrAMatchingMod, arrBMatchingMod, arrARem, arrBRem


# def funB(strB, l): 
#   return strB[:l]
# def funExtra(strA): return len(strA)
# arrRenameMatch, arrDBMatch, arrRenameRem, arrDBRem=extractMatchingOneToManyUnsortedFW(["qrs", "aa","progC"], ["abc", "progC/abc", "progC/def", "progC/ghi", "ss"], None, funB, funExtra)



      # An arrA element  may match multiple arrB elements (but not the other way around)
      # arrA and arrB must both be sorted
def extractMatchingOneToManyF(arrA, arrB, fun):
  iA=0; iB=0
  lenA=len(arrA); lenB=len(arrB)
  
  arrAMatching=[]; arrBMatching=[]
  arrARem=[]; arrBRem=[]
  while(1):
    boEndA=iA==lenA; boEndB=iB==lenB
    if(boEndA and not boEndB): arrBRem.extend(arrB[iB:]); break
    elif(not boEndA and  boEndB): arrARem.extend(arrA[iA:]); break
    elif(boEndA and  boEndB): break

    rowA=arrA[iA]; rowB=arrB[iB]
    intVal=fun(rowA,rowB)
    if(intVal>0): arrARem.append(rowA); iA+=1     # B is ahead of A
    elif(intVal<0): arrBRem.append(rowB); iB+=1   # A is ahead of B
    elif(intVal==0): arrAMatching.append(rowA); arrBMatching.append(rowB); iB+=1; #iA+=1
    else: print("error when comparing strings")
    
  return arrAMatching, arrBMatching, arrARem, arrBRem

#extractMatchingOneToManyF(["aa","progC","qrs"], ["abc", "progC/abc", "progC/def", "progC/ghi", "ss"], funStrShortest)


      # arrA and arrB are arrays of dicts. Ex: arrA=[{a:1,b:1}, {a:1,b:1}] 
      # arrA and arrB must both be sorted, in a way so that calling "fun" on each element gives an increasing (although not necessarily strictly) order.
      # The returned values (objAMatching, objBMatching) consists of all the rows (of arrA and arrB) although arranged by their output when called through "fun".
      # That is each property key (of objAMatching and objBMatching) are the output of fun. The corresponding value is an array of the rows that outputted that key. 
      # That array may be empty, then that property key (fun-value) only exist in the opposite arrA/arrB.
      # Ex: objAMatching={blahblah:[{a:1,b:1}, {a:1,b:1}], blahblahblah:[]}
def extractMatchingManyToManyF(arrA, arrB, fun):
  iA=0; iB=0
  lenA=len(arrA); lenB=len(arrB)
  objAMatching={}; objBMatching={}
  #arrARem=[]; arrBRem=[]
  while(1):
      # If the end of any array has been reached, then everything ends here (this below part should really be outside the loop. (on todo list))
    boEndA=iA==lenA; boEndB=iB==lenB
    if(boEndA and not boEndB):
      iBTmp=iB
      while(1):
        rowBTmp=arrB[iBTmp];  valB=fun(rowBTmp)
        if(valB not in objAMatching): objAMatching[valB]=[]
        if(valB not in objBMatching): objBMatching[valB]=[]
        objBMatching[valB].append(rowBTmp)
        iBTmp=iBTmp+1
        if(iBTmp==lenB): iB=iBTmp; break
      break
    elif(not boEndA and  boEndB):
      iATmp=iA
      while(1):
        rowATmp=arrA[iATmp];  valA=fun(rowATmp)
        if(valA not in objAMatching): objAMatching[valA]=[]
        if(valA not in objBMatching): objBMatching[valA]=[]
        objAMatching[valA].append(rowATmp)
        iATmp=iATmp+1
        if(iATmp==lenA): iA=iATmp; break
      break
    elif(boEndA and  boEndB): break

    rowA=arrA[iA]; rowB=arrB[iB];  valA=fun(rowA); valB=fun(rowB)
    if(valA not in objAMatching): objAMatching[valA]=[]
    if(valA not in objBMatching): objBMatching[valA]=[]
    if(valB not in objAMatching): objAMatching[valB]=[]
    if(valB not in objBMatching): objBMatching[valB]=[]
    if(valA<valB):   # B is ahead of A
      objAMatching[valA].append(rowA); iA+=1     
    elif(valA>valB):  # A is ahead of B
      objBMatching[valB].append(rowB); iB+=1  
    elif(valA==valB):
      objAMatching[valA].append(rowA); objBMatching[valB].append(rowB)
      iATmp=iA; iBTmp=iB
      while(1):
        iATmp=iATmp+1
        if(iATmp==lenA): iA=iATmp; break
        rowATmp=arrA[iATmp]; valATmp=fun(rowATmp)
        if(valATmp==valB): objAMatching[valATmp].append(rowATmp)
        else: iA=iATmp; break
      while(1):
        iBTmp=iBTmp+1
        if(iBTmp==lenB): iB=iBTmp; break
        rowBTmp=arrB[iBTmp]; valBTmp=fun(rowBTmp)
        if(valA==valBTmp): objBMatching[valBTmp].append(rowBTmp)
        else: iB=iBTmp; break

    else: print("error when comparing strings")
    
  return objAMatching, objBMatching


# def funStrShortest(rowA,rowB):
#   strA=rowA; l=len(strA); strB=rowB[:l]
#   if(strA<strB): return 1
#   elif(strA>strB): return -1
#   elif(strA==strB): return 0
#   else: print("Error not lt, not gt and not equal???")
def funInt(a,b):
  if(a<b): return 1
  elif(a>b): return -1
  elif(a==b): return 0
  else: print("Error not lt, not gt and not equal???")


#extractMatchingManyToManyF([3,6,9], [2,3,8], lambda x: x)
#extractMatchingManyToManyF([3,6,9], [2,3,3,8], lambda x: x)
#extractMatchingManyToManyF([1,3,3,6,9], [2,3,3], lambda x: x)
#extractMatchingManyToManyF(["aa","progC","qrs"], ["abc", "progC/abc", "progC/def", "progC/ghi", "ss"], funStrShortest)
