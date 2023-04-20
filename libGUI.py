#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from idlelib.tooltip import Hovertip
import webbrowser
import json
import settings
import globvar
from libMainFunctions import *
from libMyTkinter import *

import asyncio

async def tk_main(root):
  while True:
    root.update()
    await asyncio.sleep(0.05)

class windowRoot(tk.Tk):
  def __init__(self, *args, **kwargs):
    root=self
    tk.Tk.__init__(root, *args, **kwargs)
    root.wm_title("Buvt")
    root.minsize(900,500)

      # frameTop
    frameTop = tk.Frame(root)
    #frameTop.pack(fill=tk.X)
    frameTop.grid(sticky="we", columnspan = 1)

    combobox = ttk.Combobox(frameTop, state="readonly")
    myTip = Hovertip(combobox, 'input variables\nsource/target folder etc (read from sourceTargetCombos.json)')
    combobox.pack( side = tk.LEFT, fill=tk.NONE)

    arrLabel=[]
    for row in globvar.localStorageST.obj:
      arrLabel.append(row["label"])
    #combobox['values'] = ["a","b","c"]
    combobox['values'] = arrLabel
    iSelected=globvar.localStorageOther.obj["iSelected"]
    if(iSelected<len(arrLabel)): combobox.current(iSelected)
    def comboboxChange(event):
      iSelected=combobox.current()
      globvar.localStorageOther.obj["iSelected"]=iSelected
      globvar.localStorageOther.writeStored()
      #print(combobox.get())
      
    combobox.bind("<<ComboboxSelected>>", comboboxChange)

    link = tk.Label(frameTop, text="Web info", fg="blue", cursor="hand2" )
    link.pack(fill=tk.Y)
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://emagnusandersson.com/buvt"))





    frT2M = tk.Frame(root, borderwidth=1, relief="solid") # , background="blue"
    frT2M.grid(row = 1, column = 0, sticky = "nwes", pady = 1, padx = 1)
    frT2M.grid_columnconfigure((0,1), weight=1) #, uniform="column"

    cRowT2M=0
    labT2M = tk.Label(frT2M, text = "Tree to meta-file")
    labT2M.grid(sticky="nwe", row = cRowT2M, column = 0, columnspan = 2)
    labT2M.config(font=('Helvatical bold',14))

    cRowT2M+=1
    labSource = tk.Label(frT2M, text = "Source")
    labSource.grid(sticky="nwe", row = cRowT2M, column = 0 )
    labSource.config(font=('Helvatical bold',12))
    labTarget = tk.Label(frT2M, text = "Target")
    labTarget.config(font=('Helvatical bold',12))
    labTarget.grid(sticky="nwe", row = cRowT2M, column = 1 )


        # HardLinkCheck
    cRowT2M+=1
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, ["fiDirSource", "charTRes"]);
      args["leafFilterFirst"]=objSel.get("leafFilterFirstTree") or objSel.get("leafFilterFirst") or settings.leafFilter
      hardLinkCheck(**args)
    butHardLinkCheck = tk.Button(frT2M, text="Check for hard links (?)", command=cb)
    myTip = Hovertip(butHardLinkCheck, f'Check source tree for hard links. (Note: all functions relying on the absence of hard links also checks for hard links) \n(Found hard links are written to {settings.arrPath["T2M_HL"].name} in the settings directory.)')
    butHardLinkCheck.grid(sticky="w", row = cRowT2M, column = 0)


      # Compare (T2M)
    cRowT2M+=1
    syncTreeToMeta=None
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, ["charTRes", "leafFilterFirst", "flPrepend"]);
      args["fiDir"]=objSel["fiDirSource"]
      #if("leafFilterFirst_M" in objST and objST["leafFilterFirst_M"]): objST["leafFilterFirst"]=objST["leafFilterFirst_M"] 
      global syncTreeToMeta
      syncTreeToMeta=SyncTreeToMeta('compareTreeToMeta', **args)
      syncTreeToMeta.compare()
      syncTreeToMeta=None
    butCompareTreeToMeta = tk.Button(frT2M, text="Compare", command=cb)
    butCompareTreeToMeta.grid(sticky="w", row = cRowT2M, column = 0)


      # Sync (T2M)
    cRowT2M+=1
    def cbSyncTreeToMeta():
      textbox.delete('1.0', tk.END); #root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, ["charTRes", "leafFilterFirst", "flPrepend"])
      args["fiDir"]=objSel["fiDirSource"]
      global syncTreeToMeta
      syncTreeToMeta=SyncTreeToMeta('syncTreeToMeta', **args)
      syncTreeToMeta.compare()
      boChanged=syncTreeToMeta.createSyncData()
      if(not boChanged): return
      root.update()
      global cbContinue
      #frameContinue.pack(side=tk.BOTTOM)
      frameContinue.grid(columnspan = 2)
      cbContinue=cbSyncTreeToMetaB
    def cbSyncTreeToMetaB():
      global syncTreeToMeta
      syncTreeToMeta.makeChanges()
      syncTreeToMeta=None
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    butSyncTreeToMeta = tk.Button(frT2M, text="Sync", command=cbSyncTreeToMeta)
    #myTip = Hovertip(butSyncTreeToMeta, 'Matching source tree meta data (size, mod-time AND FileId) to meta-file and update the meta-file')
    butSyncTreeToMeta.grid(sticky="w", row = cRowT2M, column = 0)

       # frameTargetCompare
    # def cb():
    #   textbox.delete('1.0', tk.END); root.update()
    #   iSelected=globvar.localStorageOther.obj["iSelected"];   objSel=globvar.localStorageST.obj[iSelected]
    #   args=copySome({}, objSel, ["charTRes", "flPrepend"])
    #   args["fiDir"]=objSel["fiDirTarget"]
    #   args["leafFilterFirst"]=objSel.get("leafFilterFirstTree") or objSel.get("leafFilterFirst") or settings.leafFilter
    #   compareTreeToMetaSTOnly(**args) 
    # butCompareTreeToMetaSTOnly = tk.Button(frT2M, text="Compare", command=cb)
    # #myTip = Hovertip(butCompareTreeToMetaSTOnly, 'Compare target tree to meta-file, size and mod-time only (WO file-id)')
    # butCompareTreeToMetaSTOnly.grid(sticky="w", row=cRowT2M, column=1)


      # RenameFinishToMeta
    #cRowT2M+=1
    renameFinishToMeta=None
    def cbRenameFinishToMeta():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      #args=copySome({}, objSel, ["fiDirSource"])
      fiMeta=objSel["fiDirSource"]+'/'+settings.leafMeta
      args={fiMeta:fiMeta}
      global renameFinishToMeta
      renameFinishToMeta=RenameFinishToMeta(**args)
      boChanged=renameFinishToMeta.read()
      if(not boChanged): return
      root.update()
      global cbContinue
      #frameContinue.pack(side=tk.BOTTOM)
      frameContinue.grid(columnspan = 2)
      cbContinue=cbRenameFinishToMetaB
    def cbRenameFinishToMetaB():
      global renameFinishToMeta
      renameFinishToMeta.makeChanges()
      renameFinishToMeta=None
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    butRenameFinishToMeta = tk.Button(frT2M, text="Rename OTO to meta-file(S) (?)", command=cbRenameFinishToMeta)
    myTip = Hovertip(butRenameFinishToMeta, f'The entries in source meta-file are renamed according to {settings.arrPath["T2M_renameOTO"].name}.')
    #butRenameFinishToMeta.grid(sticky="w", row = cRowT2M, column = 0)


 

      #
      # frT2T
      #

    frT2T = tk.Frame(root, borderwidth=1, relief="solid") #, background="grey"
    labT2T = tk.Label(frT2T, text= "Tree to tree")
    labT2T.grid() #sticky="we"
    labT2T.config(font=('Helvatical bold',14))
    #myTip = Hovertip(labT2T, 'Match source tree meta data (size, mod-time (NOT FileId/inode)) to target tree meta data, then:\n•Compare: display the result \n•Sync: update the target tree. (like rsync (skipping files with matching file-name, size and mod-time))')
    frT2T.grid(row = 1, column = 1, sticky ="nwes", pady = 1, padx = 1)

    # frameTreeToTree = tk.Frame(frT2T)
    # frameTreeToTree.grid(sticky="w")
    # label = tk.Label(frameTreeToTree, text="Tree(S) to tree(T) (WO Id) (?)" )
    # myTip = Hovertip(label, 'Match source tree meta data (size, mod-time (NOT FileId/inode)) to target tree meta data, then:\n•Compare: display the result \n•Sync: update the target tree. (like rsync (skipping files with matching file-name, size and mod-time))')
    # label.pack(side = tk.LEFT)
      # Compare (tree-to-tree) button
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      objOther=globvar.localStorageOther.obj;   iSelected=objOther["iSelected"];   objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, ["fiDirSource", "fiDirTarget", "charTRes"])
      args["leafFilterFirst"]=objSel.get("leafFilterFirstTree") or objSel.get("leafFilterFirst") or settings.leafFilter
      compareTreeToTree(**args)
    butCompareTreeToTree = tk.Button(frT2T, text="Compare", command=cb)
    #myTip = Hovertip(butCompareTreeToTree,'Compare source tree to target tree')
    butCompareTreeToTree.grid( sticky ="w")

      # Rename OTO button
    renameFinishToTree=None
    def cbRenameFinishToTree():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args={}
      args["fiDir"]=objSel["fiDirTarget"]
      args["pRenameFile"]=settings.arrPath["T2T_renameOTO"]
      global renameFinishToTree
      renameFinishToTree=RenameFinishToTree(**args)
      boChanged=renameFinishToTree.read()
      if(not boChanged): return
      root.update()
      global cbContinue
      #frameContinue.pack(side=tk.BOTTOM)
      frameContinue.grid(columnspan = 2)
      cbContinue=cbRenameFinishToTreeB
    def cbRenameFinishToTreeB():
      global renameFinishToTree
      renameFinishToTree.makeChanges()
      renameFinishToTree=None
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    butRenameFinishToTree = tk.Button(frT2T, text="Rename OTO to tree(T) (?)", command=cbRenameFinishToTree)
    myTip = Hovertip(butRenameFinishToTree, f'Rename according to \n{settings.arrPath["T2T_renameOTO"].name} \nto target tree.')
    butRenameFinishToTree.grid( sticky ="w", padx = 10 )

      # Rename additional button
    renameFinishToTree=None
    def cbRenameFinishToTreeAdd():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args={}
      args["fiDir"]=objSel["fiDirTarget"]
      args["pRenameFile"]=settings.arrPath["T2T_renameAdditional"]
      global renameFinishToTree
      renameFinishToTree=RenameFinishToTree(**args)
      boChanged=renameFinishToTree.read()
      if(not boChanged): return
      root.update()
      global cbContinue
      #frameContinue.pack(side=tk.BOTTOM)
      frameContinue.grid(columnspan = 2)
      cbContinue=cbRenameFinishToTreeAddB
    def cbRenameFinishToTreeAddB():
      global renameFinishToTree
      renameFinishToTree.makeChanges()
      renameFinishToTree=None
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    butRenameFinishToTreeAdditional = tk.Button(frT2T, text='Rename "additional" to tree(T) (?)', command=cbRenameFinishToTreeAdd)
    myTip = Hovertip(butRenameFinishToTreeAdditional, f'Rename according to \n{settings.arrPath["T2T_renameAdditional"].name} \nto target tree')
    butRenameFinishToTreeAdditional.grid( sticky ="w", padx = 10 )

      # Sync-button
    syncTreeToTreeBrutal=None
    def cbSyncTreeToTreeBrutal():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"];   objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, ["fiDirSource", "fiDirTarget", "charTRes", "flPrepend"])
      args["leafFilterFirst"]=objSel.get("leafFilterFirstTree") or objSel.get("leafFilterFirst") or settings.leafFilter
      global syncTreeToTreeBrutal
      syncTreeToTreeBrutal=SyncTreeToTreeBrutal(**args)
      boChanged=syncTreeToTreeBrutal.compare()
      if(not boChanged): return
      root.update()
      global cbContinue
      #frameContinue.pack(side=tk.BOTTOM)
      frameContinue.grid(columnspan = 2)
      cbContinue=cbSyncTreeToTreeBrutalB
    def cbSyncTreeToTreeBrutalB():
      global syncTreeToTreeBrutal
      syncTreeToTreeBrutal.makeChanges()
      syncTreeToTreeBrutal=None
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    butSyncTreeToTreeBrutal = tk.Button(frT2T, text="Sync (like rsync) (?)", command=cbSyncTreeToTreeBrutal)
    myTip = Hovertip(butSyncTreeToTreeBrutal, 'Files with the same name, size \nand mod-time are left untouched.\nOthers are overwritten\n(Renamed files are overwritten.)')
    butSyncTreeToTreeBrutal.grid( sticky ="w")


      #
      # Checking
      #

    frameChecking = tk.Frame(root, borderwidth=1, relief="solid")
    #frameButOpen.pack(fill=tk.X)
    frameChecking.grid(row = 2, sticky="we", columnspan = 2, pady = 1, padx = 1)

      # Check file existance
    cRowT2M+=1
    labCheckExistance = tk.Label(frameChecking, text= "Check file existance:")
    labCheckExistance.config(font=('Helvatical bold',12))
    labCheckExistance.pack(side = tk.LEFT) #sticky="we"

    cRowT2M+=1
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, [])
      args["fiDir"]=objSel["fiDirSource"]
      checkSummarizeMissing(**args)
    butCheckSummarizeMissing = tk.Button(frameChecking, text="Source (?)", command=cb)
    myTip = Hovertip(butCheckSummarizeMissing, 'Going through all the files in meta-file and check that they exist.')
    butCheckSummarizeMissing.pack(side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      iSelected=globvar.localStorageOther.obj["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objSel, [])
      args["fiDir"]=objSel["fiDirTarget"]
      checkSummarizeMissing(**args)
    butCheckSummarizeMissing = tk.Button(frameChecking, text="Target (?)", command=cb)
    myTip = Hovertip(butCheckSummarizeMissing, 'Going through all the files in meta-file (on the target side) and check that they exist.')
    butCheckSummarizeMissing.pack(side = tk.LEFT)
    

      # Check hashcodes
    cRowT2M+=1
    frameCheckHashLabel = tk.Frame(frameChecking) #, background='red'
    frameCheckHashLabel.pack(side = tk.LEFT) #sticky="e", 
    
    labCheckHash = tk.Label(frameCheckHashLabel, text= "Check hashcodes:")
    labCheckHash.pack(side = tk.LEFT) #sticky="we"
    labCheckHash.config(font=('Helvatical bold',12))

      # iStart
    def saveIStart():
      iStart=int(entryIStart.get())
      globvar.localStorageOther.obj["iStart"]=iStart
      globvar.localStorageOther.writeStored()
      entryIStart.configure(background="white")
      butSaveIStart.pack_forget()
    butSaveIStart = tk.Button(frameCheckHashLabel, text="Save", command=saveIStart)
    # def do_validation():
    #   value = entry.get()
    #   if value == "" or value.isnumeric(): return True
    #   return False
    # entry = tk.Entry(frameCheck, validate='key', validatecommand=do_validation)
    label = tk.Label(frameCheckHashLabel, text="iStart: (?)" )
    myTip = Hovertip(label, 'Start on this row of the meta-file -file')
    label.pack(side = tk.LEFT)
    def do_validation(new_value):
      return new_value == "" or new_value.isnumeric()
    vcmd = (root.register(do_validation), '%P')
    sv=tk.StringVar()
    def changef(sv):
      strVal=sv.get()
      if(strVal==''): boChanged=False
      else:
        new_value=int(strVal);   boChanged=new_value!=globvar.localStorageOther.obj["iStart"]
      strCol="green" if(boChanged) else "white";     entryIStart.configure(background=strCol)
      if(boChanged): butSaveIStart.pack(side = tk.LEFT)
      else: butSaveIStart.pack_forget()
      
    #sv.trace("w", changef)
    #sv.set('0')
    sv.set(globvar.localStorageOther.obj["iStart"])
    sv.trace("w", lambda name, index, mode, sv=sv: changef(sv))
    entryIStart = tk.Entry(frameCheckHashLabel, validate='key', validatecommand=vcmd, textvariable=sv)
    entryIStart.pack(side = tk.LEFT)
    myTip = Hovertip(entryIStart, 'iStart, start on this row of the meta-file -file')
    #entryIStart.bind('<FocusIn>', lambda ev:entryIStart.configure(background="green"))
    #entryIStart.bind('<FocusOut>', lambda ev:entryIStart.configure(background="white"))
  

      # CheckHash buttons
    cRowT2M+=1
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      objOther=globvar.localStorageOther.obj; iSelected=objOther["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objOther, ["iStart"])
      copySome(args, objSel, ["charTRes"])
      args["fiDir"]=objSel["fiDirSource"]
      check(**args)
    butCheck = tk.Button(frameChecking, text="Source (?)", command=cb)
    myTip = Hovertip(butCheck, 'Going through all the files in meta-file and calculate hashcodes.')
    butCheck.pack(side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END); root.update()
      objOther=globvar.localStorageOther.obj; iSelected=objOther["iSelected"]; objSel=globvar.localStorageST.obj[iSelected]
      args=copySome({}, objOther, ["iStart"])
      copySome(args, objSel, ["charTRes"])
      args["fiDir"]=objSel["fiDirTarget"]
      check(**args)
    butCheck = tk.Button(frameChecking, text="Target (?)", command=cb)
    myTip = Hovertip(butCheck, 'Going through all the files in meta-file (on the target side) and calculate hashcodes.')
    butCheck.pack(side = tk.LEFT)



      #
      # frameButOpen
      #

    frameButOpen = tk.Frame(root, borderwidth=1, relief="solid")
    #frameButOpen.pack(fill=tk.X)
    frameButOpen.grid(row=3, sticky="we", columnspan = 2, pady = 1, padx = 1)

    def open():
      if(sys.platform=="linux"): strStart="xdg-open"
      elif(sys.platform=="win32"): strStart="start"
      os.system(strStart+" "+settings.flStorageDir)
    butOpen= tk.Button(frameButOpen, text="Open settings / rename-lists folder", command=open)
    butOpen.pack( side = tk.LEFT )

    def openCompare():
      if(sys.platform=="linux"): strStart="meld"
      elif(sys.platform=="win32"): strStart="meld"
      strA=str(settings.arrPath["T2M_renameOTO"].resolve()); strB=str(settings.arrPath["T2T_renameOTO"].resolve())
      os.system(strStart+" "+strA+" "+strB)
    butOpenCompare= tk.Button(frameButOpen, text="Compare OTO", command=openCompare)
    butOpenCompare.pack( side = tk.LEFT )


      # textbox
    textbox = tk.Text(master=root, state=tk.NORMAL, height=21) #, width=100
    #textbox.pack(fill=tk.BOTH,expand=True)
    textbox.grid(row=4, sticky="nsew", columnspan = 2)
    #textbox.grid(row=0, column=0)
    #textbox.insert("0.0", "new text to insert\n")  # insert at line 0 character 0
    self.myConsole=MyConsoleGui(textbox)


      # frameContinue
    frameContinue = tk.Frame(root)
    #frameContinue.pack(fill=tk.BOTH) #fill=tk.BOTH, side=tk.BOTTOM
    #frameContinue.pack(side=tk.BOTTOM) #fill=tk.BOTH, side=tk.BOTTOM
    #frameContinue.pack(fill=tk.BOTH, anchor=tk.CENTER, expand=True, padx=20, pady=20) #fill=tk.BOTH, side=tk.BOTTOM
    #frameContinue.grid_columnconfigure((0,1), weight=1, uniform="column")
    #frameContinue.grid()
    # root.grid_rowconfigure((0,1,2,3,4,5,6,8),weight=0)
    # root.grid_rowconfigure(7,weight=1)
    root.grid_rowconfigure((0,1,2),weight=0)
    root.grid_rowconfigure(3,weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    cbContinue=None
    def cb():
      global cbContinue
      cbContinue()
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    butContinue = tk.Button(frameContinue, text="Continue", command=cb); butContinue.config(fg="#fff", bg="#f11", activeforeground="#000", activebackground="#f00");
    #butContinue.pack(side = tk.LEFT)
    butContinue.grid(row=0, column=0)
    def cb():
      #frameContinue.pack_forget()
      frameContinue.grid_forget()
    #def cb(): frameContinue.place_forget()
    butCancel = tk.Button(frameContinue, text="Cancel", command=cb)
    #butCancel.pack(side = tk.LEFT)
    butCancel.grid(row=0, column=1)

    # frameBottom = tk.Frame(root)
    # frameBottom.pack(fill=tk.BOTH, side=tk.BOTTOM)





