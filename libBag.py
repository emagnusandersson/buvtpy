
import bisect
import copy
import globvar

from types import SimpleNamespace
from difflib import SequenceMatcher
import re

from lib import *




  # Some cb functions for testing
def funStrShortest(rowA,rowB):
  strA=rowA; l=len(strA); strB=rowB[:l]
  if(strA<strB): return 1
  elif(strA>strB): return -1
  elif(strA==strB): return 0
  else: globvar.myConsole.error("not lt, not gt and not equal???")
def funInt(a,b):
  if(a<b): return 1
  elif(a>b): return -1
  elif(a==b): return 0
  else: globvar.myConsole.error("not lt, not gt and not equal???")


#######################################################################################
# extractMatchingF: Comparing two arrays
#   Inputs:
#     funM101: (function-Minus1-0-1) A function that compares two array elements (from arrA and arrB (see below)). The output of funM101(element0, element1) ∈ [-1,0,1] where
#       -1: descending slope (element0 > element1)
#        0: equal (element0 == element1)
#        1: ascending slope (element0 < element1)
#     arrA and arrB: Arrays. 
#       arrA and arrB are strictly increasing (ascending) (That is: funM101(arrA[n],arrA[n+1]) is always 1).
#   The extractMatchingF-function compares the elements in arrA with elements in arrB and puts matching pairs in arrAMatching and arrBMatching (which will be of equal length). The remaining elements are equally put in containers arrARem and arrBRem
#######################################################################################


#######################################################################################
# extractMatching: (Wrapper for extractMatchingF)
#   Works as extractMatchingF although each element is an object and the comparission is made using the object-properties given in KeyA and KeyB (which should be of equal length):
#   In the below text: X ∈ [A, B]
#   Uniqueness: Object within arrX must be unique (with respect to they proprties in KeyX) (See example below).
#   Sorted strictly ascendingly: The first key (within KeyX) that is different must be larger in the preceding object.
#     So in other words, the elements of KeyX have falling priority.
#   If KeyB is omitted, KeyA will be used in its place. 
#   Ex: Assume KeyA=['m','n'] then
#     arrA=[{m:0,n:0}, {m:0,n:0}] is NOT OK (not unique (nor strictly ascending))
#     arrA=[{m:0,n:0}, {m:0,n:1}] is OK
#     arrA=[{m:1,n:0}, {m:0,n:1}] is NOT OK (not ascending, because m has higher priority)
#     arrA=[{m:0,n:1}, {m:1,n:0}] is OK
#       
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
    else: globvar.myConsole.error("error when comparing strings")
  return arrAMatching, arrBMatching, arrARem, arrBRem

def extractMatching(arrA, arrB, arrKeyA, arrKeyB=None):
  if(arrKeyB==None): arrKeyB=arrKeyA
  lenKeyA=len(arrKeyA);  lenKeyB=len(arrKeyB);  
  if(lenKeyA!=lenKeyB):  globvar.myConsole.error("lenKeyA!=lenKeyB"); return 
  if(lenKeyA==0 or lenKeyB==0):  globvar.myConsole.error("lenKeyA==0 or lenKeyB==0"); return

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
      arrAMatching.append(rowA);
      breakpoint() #Note to self, shouldn't the next line be  arrBMatching.extend(arrBWork[iBStart:iBEnd])
      arrBMatching.append(arrBWork[iBStart:iBEnd])
      arrBWork=arrBWork[:iBStart]+arrBWork[iBEnd:]
    else: arrARem.append(rowA)
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


# Note 1!! The below test fails: funB is called with three arguments in my_bisect_left/my_bisect_right
# Note 2!! extractMatchingOneToManyUnsortedF(W) is only used in renameFinishToMetaByFolder (which is not used in any launch.json-commands)

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
    else: globvar.myConsole.error("error when comparing strings")
    
  return arrAMatching, arrBMatching, arrARem, arrBRem

# Note! Never used.
#extractMatchingOneToManyF(["aa","progC","qrs"], ["abc", "progC/abc", "progC/def", "progC/ghi", "ss"], funStrShortest)


      # arrA and arrB are arrays of dicts. Ex: arrA=[{a:1,b:1}, {a:1,b:1}] 
      # arrA and arrB must both be sorted, in a way so that calling "fun" on each element gives an increasing (although not necessarily strictly) order.
      # The returned values (objAMatching, objBMatching) consists of all the rows (of arrA and arrB) although arranged by their output when called through "fun".
      # That is each property key (of objAMatching and objBMatching) are the output of fun. The corresponding value is an array of the rows that outputted that key. 
      # That array may be empty, then that property key (fun-value) only exist in the opposite arrA/arrB.
      #
      # Ex:
      # arrA=[{"a":1,"b":1}, {"a":1,"b":2}, {"a":2}];  arrB=[{"a":1,"b":1}, {"a":1,"b":3}, {"a":3}]; fun=lambda row: row["a"]
      # objAMatching, objBMatching=extractMatchingManyToManyF(arrA, arrB, fun)
      # objAMatching={"1":[{"a":1,"b":1}, {"a":1,"b":2}], "2":[{"a":2}], "3":[]}
      # objBMatching={"1":[{"a":1,"b":1}, {"a":1,"b":3}], "2":[], "3":[{"a":3}]}
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
        if(valATmp==valB):
          objAMatching[valATmp].append(rowATmp)
        else: iA=iATmp; break
      while(1):
        iBTmp=iBTmp+1
        if(iBTmp==lenB): iB=iBTmp; break
        rowBTmp=arrB[iBTmp]; valBTmp=fun(rowBTmp)
        if(valA==valBTmp):
          objBMatching[valBTmp].append(rowBTmp)
        else: iB=iBTmp; break

    else: globvar.myConsole.error("error when comparing strings")
    
  return objAMatching, objBMatching



#extractMatchingManyToManyF([3,6,9], [2,3,8], lambda x: x)
#extractMatchingManyToManyF([3,6,9], [2,3,3,8], lambda x: x)
#extractMatchingManyToManyF([1,3,3,6,9], [2,3,3], lambda x: x)
#extractMatchingManyToManyF(["aa","progC","qrs"], ["abc", "progC/abc", "progC/def", "progC/ghi", "ss"], funStrShortest)


#######################################################################################
# extractUniques
#   extract uniques within a single array arr
#######################################################################################
def extractUniques(arr,arrKey):
  if(not isinstance(arrKey, list)): arrKey=[arrKey]
  objDup={};  arrUniq=[];  arrUniqified=[];
  lenArr=len(arr)
  if(lenArr==0): return arrUniq, objDup, arrUniqified
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
      #arrUniqified.append(copy.copy(row))
      arrUniqified.append(row)
      if(strAttr in objDup): objDup[strAttr].append(row)
      else: arrUniq.append(row)

  return arrUniq, objDup, arrUniqified

# arrUniq, objDup, arrUniqified= extractUniques([{"a":1}, {"a":1}, {"a":2}], "a")
# arrUniq, objDup, arrUniqified= extractUniques([{"a":1}, {"a":1}, {"a":2}, {"a":2}], "a")
# arrUniq, objDup, arrUniqified= extractUniques([{"a":1}, {"a":1}, {"a":2}, {"a":3}], "a")



# OTO=OneToOne, OTM=OneToMany, MTO=ManyToOne, MTM=ManyToMany
# T\S    0       ①       Many
# 0              Created Created
# ①      Deleted OTO     MTO
# Many   Deleted OTM     MTM


def objManyToManyRemoveEmpty(objA, objB):  # Modifies objA and objB
  KeyDel=[]
  for key, arrA in objA.items():
    arrB=objB[key]; lenA=len(arrA); lenB=len(arrB)
    if(lenA==0 and lenB==0): KeyDel.append(key)
  for key in KeyDel:
    del objA[key]; del objB[key] 



  # objA, objB comes from (is the output of) extractMatchingManyToManyF.
  # Thus objA, objB has the same property keys.

  # Ex:
  # Generate the input (objA and objB) using extractMatchingManyToManyF
  # arrA=[{"a":1,"b":1}, {"a":1,"b":2}, {"a":2}, {"a":2}, {"a":3}]
  # arrB=[{"a":1,"b":1}, {"a":1,"b":3}, {"a":2}, {"a":2}, {"a":4}]
  # fun=lambda row: row["a"]
  # objA, objB=extractMatchingManyToManyF(arrA, arrB, fun)
  #
  # So the input is:
  # objA={"1":[{'a': 1, 'b': 1}, {'a': 1, 'b': 2}],
  # "2":[{'a': 2}, {'a': 2}],
  # "3":[{'a': 3}],
  # "4":[]}
  # objB={"1":[{'a': 1, 'b': 1}, {'a': 1, 'b': 3}],
  # "2":[{'a': 2}, {'a': 2}],
  # "3":[],
  # "4":[{'a': 4}]}
  #
  # Output:
  # ArrAMTM:[[{'a': 1, 'b': 1}, {'a': 1, 'b': 2}], [{'a': 2}, {'a': 2}]]
  # ArrAMTNull:[]
  # ArrAMTO:[]
  # ArrAOTM:[]
  # ArrAOTNull:[[{'a': 3}]]
  # ArrAOTO:[]
  # ArrBMTM:[[{'a': 1, 'b': 1}, {'a': 1, 'b': 3}],[{'a': 2}, {'a': 2}]]
  # ArrBMTO:[]
  # ArrBNullTM:[]
  # ArrBNullTO:[[{'a': 4}]]
  # ArrBOTM:[]
  # ArrBOTO:[]
  # arrAMTM:[{'a': 1, 'b': 1}, {'a': 1, 'b': 2}, {'a': 2}, {'a': 2}]
  # arrAMTNull:[]
  # arrAMTO:[]
  # arrAOTM:[]
  # arrAOTNull:[{'a': 3}]
  # arrAOTO:[]
  # arrARem:[{'a': 3}]
  # arrBMTM:[{'a': 1, 'b': 1}, {'a': 1, 'b': 3}, {'a': 2}, {'a': 2}]
  # arrBMTO:[]
  # arrBNullTM:[]
  # arrBNullTO:[{'a': 4}]
  # arrBOTM:[]
  # arrBOTO:[]
  # arrBRem:[{'a': 4}]


def convertObjManyToManyToMat(objA, objB):
  ArrAOTO=[]; ArrBOTO=[]; ArrAOTM=[]; ArrBOTM=[]; ArrAMTO=[]; ArrBMTO=[]; ArrAMTM=[]; ArrBMTM=[]
  ArrAOTNull=[]; ArrAMTNull=[]; ArrBNullTO=[]; ArrBNullTM=[]
  arrAOTNull=[]; arrAMTNull=[]; arrBNullTO=[]; arrBNullTM=[]
  arrAOTO=[]; arrBOTO=[]; arrAOTM=[]; arrBOTM=[]; arrAMTO=[]; arrBMTO=[]; arrAMTM=[]; arrBMTM=[]
  for key, arrA in objA.items():
    arrB=objB[key]
    lenA=len(arrA); lenB=len(arrB)
    if(lenA==0):
      if(lenB==0): globvar.myConsole.error("lenA==0 and lenB==0"); breakpoint(); #del objA[key]; objB[key] 
      elif(lenB==1): ArrBNullTO.append(arrB);  arrBNullTO.extend(arrB)
      else: ArrBNullTM.append(arrB);  arrBNullTM.extend(arrB)
    elif(lenA==1):
      if(lenB==0): ArrAOTNull.append(arrA);  arrAOTNull.extend(arrA)
      elif(lenB==1): ArrAOTO.append(arrA); ArrBOTO.append(arrB);    arrAOTO.extend(arrA); arrBOTO.extend(arrB)
      else: ArrAOTM.append(arrA); ArrBOTM.append(arrB);    arrAOTM.extend(arrA); arrBOTM.extend(arrB)
    else:
      if(lenB==0): ArrAMTNull.append(arrA);  arrAMTNull.extend(arrA)
      elif(lenB==1): ArrAMTO.append(arrA); ArrBMTO.append(arrB);    arrAMTO.extend(arrA); arrBMTO.extend(arrB)
      else: ArrAMTM.append(arrA); ArrBMTM.append(arrB);    arrAMTM.extend(arrA); arrBMTM.extend(arrB)

  arrARem=arrAMTNull+arrAOTNull
  arrBRem=arrBNullTO+arrBNullTM
  return SimpleNamespace(**{"ArrAOTO":ArrAOTO, "ArrBOTO":ArrBOTO, "ArrAOTM":ArrAOTM, "ArrBOTM":ArrBOTM, "ArrAMTO":ArrAMTO, "ArrBMTO":ArrBMTO, "ArrAMTM":ArrAMTM, "ArrBMTM":ArrBMTM, "arrARem":arrARem, "arrBRem":arrBRem, "arrAOTO":arrAOTO, "arrBOTO":arrBOTO, "arrAOTM":arrAOTM, "arrBOTM":arrBOTM, "arrAMTO":arrAMTO, "arrBMTO":arrBMTO, "arrAMTM":arrAMTM, "arrBMTM":arrBMTM,
  "ArrAOTNull":ArrAOTNull, "ArrAMTNull":ArrAMTNull, "ArrBNullTO":ArrBNullTO, "ArrBNullTM":ArrBNullTM, "arrAOTNull":arrAOTNull, "arrAMTNull":arrAMTNull, "arrBNullTO":arrBNullTO, "arrBNullTM":arrBNullTM})


# arrA=[{"a":1,"b":1}, {"a":1,"b":2}, {"a":2}, {"a":2}, {"a":3}]
# arrB=[{"a":1,"b":1}, {"a":1,"b":3}, {"a":2}, {"a":2}, {"a":4}]
# fun=lambda row: row["a"]
# objA, objB=extractMatchingManyToManyF(arrA, arrB, fun)
# objA={"1":[{'a': 1, 'b': 1}, {'a': 1, 'b': 2}],"2":[{'a': 2}, {'a': 2}],"3":[{'a': 3}],"4":[]}
# objB={"1":[{'a': 1, 'b': 1}, {'a': 1, 'b': 3}],"2":[{'a': 2}, {'a': 2}],"3":[],"4":[{'a': 4}]}
# # objA={"1":[{"a":1,"b":1}, {"a":1,"b":2}], "2":[{"a":2}], "3":[]}
# # objB={"1":[{"a":1,"b":1}, {"a":1,"b":3}], "2":[], "3":[{"a":3}]}
# Mat=convertObjManyToManyToMat(objA, objB)


def similar(a, b):
  return SequenceMatcher(None, a, b).ratio()


def markRelBest(ArrA, ArrB):
  for i, arrA in enumerate(ArrA):
    arrB=ArrB[i]; lenA=len(arrA); lenB=len(arrB)
    jBest=-1; kBest=-1; fitBest=0
    for j, elA in enumerate(arrA):
      #bestAByB=[None]*lenB
      for k, elB in enumerate(arrB):
        strNameA=elA["strName"]; strNameB=elB["strName"]
        rat=similar(strNameA, strNameB)
        if(rat>fitBest): fitBest=rat; jBest=j; kBest=k
    if(jBest>0): elABest=arrA.pop(jBest);  arrA.insert(0, elABest)
    if(kBest>0): elBBest=arrB.pop(kBest);  arrB.insert(0, elBBest)



# def rmFrArr(arrA, strPat):
#   regPat=re.compile(strPat)
#   for i, el in reversed(list(enumerate(arrA))):
#     res=regPat.match(el["strName"])
#     boMatch=bool(res)
#     if(boMatch): del arrA[i]
