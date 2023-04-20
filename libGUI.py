#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk
from idlelib.tooltip import Hovertip
import webbrowser
import json
import settings
import globvar
from libMainFunctions import *
from libMyTkinter import *




class windowRoot(tk.Tk):
  def __init__(self, *args, **kwargs):
    root=self
    tk.Tk.__init__(root, *args, **kwargs)
    root.wm_title("Buvt")


      # frameTop
    frameTop = tk.Frame(root)
    frameTop.pack(fill=tk.X)

    combobox = ttk.Combobox(frameTop, state="readonly")
    myTip = Hovertip(combobox, 'input variables\nsource/target folder etc (read from sourceTargetCombos.json)')
    combobox.pack( side = tk.LEFT, fill=tk.NONE)

    arrLabel=[]
    for row in globvar.localStorageST.obj:
      arrLabel.append(row["label"])
    #combobox['values'] = ["a","b","c"]
    combobox['values'] = arrLabel 
    combobox.current(globvar.localStorageOther.obj["iSelected"])
    def comboboxChange(event):
      iSelected=combobox.current()
      globvar.localStorageOther.obj["iSelected"]=iSelected
      globvar.localStorageOther.writeStored()
      #print(combobox.get())
      
    combobox.bind("<<ComboboxSelected>>", comboboxChange)

    butClear = tk.Button(frameTop, text="Clear (?)", command=lambda: textbox.delete('1.0', tk.END))
    myTip = Hovertip(butClear, 'Clear output below')
    butClear.pack( side = tk.RIGHT, fill=tk.NONE)

    link = tk.Label(frameTop, text="Website info", fg="blue", cursor="hand2")
    link.pack(fill=tk.Y)
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://emagnusandersson.com/buvt"))


        # frameNote
    # frameNote = tk.Frame(root)
    # frameNote.pack(fill=tk.BOTH)
    # label = tk.Label(frameNote, text='NOTE!!! the "Sync" and "Rename"-buttons below will rewrite data WITHOUT a popup warning.' )
    # #myTip = Hovertip(label, 'Not needed for normal usage.')
    # label.pack(side = tk.LEFT)
    # label.configure(background='red')

        # frameDeveloper
    frameDeveloper = tk.Frame(root)
    frameDeveloper.pack(fill=tk.BOTH)
    label = tk.Label(frameDeveloper, text="Extra:" )
    #myTip = Hovertip(label, 'Not needed for normal usage.')
    label.pack(side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      hardLinkCheck(**globvar.localStorageST.obj[iSelected])
    butHardLinkCheck = tk.Button(frameDeveloper, text="Check for hard links (?)", command=cb)
    myTip = Hovertip(butHardLinkCheck, 'Check source tree for hard links (Note: all functions relying on the absence of hard links also checks for hard links, so this button is not needed really.)')
    butHardLinkCheck.pack( side = tk.LEFT )


      # frameWID
    frameWID = tk.Frame(root)
    frameWID.pack(fill=tk.BOTH)
    label = tk.Label(frameWID, text="Tree(S) to meta-file(S) (W Id)" )
    myTip = Hovertip(label, 'Match source tree meta data (size, mod-time AND FileId/inode) to the meta-file in the source directory. Then:\n•Compare: display the result \n•Sync: update the meta-file.')
    label.pack( side = tk.LEFT )
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=copy.copy(globvar.localStorageST.obj[iSelected]);  objST["leafFilterFirst"]=objST["leafFilterFirst_MS"] #or '.buvt-filterM'
      syncTreeToMeta('compareTreeToMeta', **objST, **{"fiDir":objST["fiDirSource"]})
    butCompareTreeToMeta = tk.Button(frameWID, text="Compare", command=cb)
    #myTip = Hovertip(butCompareTreeToMeta, '')
    butCompareTreeToMeta.pack( side = tk.LEFT )
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=copy.copy(globvar.localStorageST.obj[iSelected]);  objST["leafFilterFirst"]=objST["leafFilterFirst_MS"] #or '.buvt-filterM'
      syncTreeToMeta('syncTreeToMeta', **objST, **{"fiDir":objST["fiDirSource"]})
    butSyncTreeToMeta = tk.Button(frameWID, text="Sync", command=cb)
    #myTip = Hovertip(butSyncTreeToMeta, 'Matching source tree meta data (size, mod-time AND FileId) to meta-file and update the meta-file')
    butSyncTreeToMeta.pack( side = tk.LEFT )


      # frameRename
    frameRename = tk.Frame(root)
    frameRename.pack(fill=tk.BOTH)
    label = tk.Label(frameRename, text="Rename (?)" )
    myTip = Hovertip(label, f'Rename according to {settings.leafRenameSuggestionsOTO} or {settings.leafRenameSuggestionsAdditional}')
    label.pack( side = tk.LEFT )
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      renameFinishToMeta(**globvar.localStorageST.obj[iSelected], **{"leafFile":settings.leafRenameSuggestionsOTO})
    butRenameFinishToMeta = tk.Button(frameRename, text="Rename OTO to meta-file(S) (?)", command=cb)
    myTip = Hovertip(butRenameFinishToMeta, f'The entries in source meta-file are renamed according to {settings.leafRenameSuggestionsOTO}.')
    butRenameFinishToMeta.pack( side = tk.LEFT )
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=globvar.localStorageST.obj[iSelected]
      renameFinishToTree(**objST, **{"fiDir":objST["fiDirTarget"], "leafFile":settings.leafRenameSuggestionsOTO})
    butRenameFinishToTree = tk.Button(frameRename, text="Rename OTO to tree(T) (?)", command=cb)
    myTip = Hovertip(butRenameFinishToTree, f'Rename according to {settings.leafRenameSuggestionsOTO} to target tree.')
    butRenameFinishToTree.pack( side = tk.LEFT )
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=globvar.localStorageST.obj[iSelected]
      renameFinishToTree(**objST, **{"fiDir":objST["fiDirTarget"], "leafFile":settings.leafRenameSuggestionsAdditional})
    butRenameFinishToTreeAdditional = tk.Button(frameRename, text='Rename "additional" to tree(T) (?)', command=cb)
    myTip = Hovertip(butRenameFinishToTreeAdditional, f'Rename according to {settings.leafRenameSuggestionsAdditional} to target tree')
    butRenameFinishToTreeAdditional.pack( side = tk.LEFT )


        # frameTreeToTree
    frameTreeToTree = tk.Frame(root)
    frameTreeToTree.pack(fill=tk.BOTH)
    label = tk.Label(frameTreeToTree, text="Tree(S) to tree(T) (WO Id) (?)" )
    myTip = Hovertip(label, 'Match source tree meta data (size, mod-time (NOT FileId/inode)) to target tree meta data, then:\n•Compare: display the result \n•Sync: update the target tree. (like rsync (skipping files with matching file-name, size and mod-time))')
    label.pack(side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      objOther=globvar.localStorageOther.obj; iSelected=objOther["iSelected"]
      compareTreeToTree(**globvar.localStorageST.obj[iSelected], **objOther)
    butCompareTreeToTree = tk.Button(frameTreeToTree, text="Compare", command=cb)
    #myTip = Hovertip(butCompareTreeToTree,'Compare source tree to target tree')
    butCompareTreeToTree.pack( side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      syncTreeToTreeBrutal(**globvar.localStorageST.obj[iSelected])
    butSyncTreeToTreeBrutal = tk.Button(frameTreeToTree, text="Sync (like rsync)", command=cb)
    #myTip = Hovertip(butSyncTreeToTreeBrutal, 'Files with the same name, size and mod-time are left untouched.\nOthers are overwritten\n(Renamed files are overwritten.)')
    butSyncTreeToTreeBrutal.pack( side = tk.LEFT)


        # frameTargetCompare
    frameTargetCompare = tk.Frame(root)
    frameTargetCompare.pack(fill=tk.BOTH)
    label = tk.Label(frameTargetCompare, text="Tree(T) to meta-file(T) (WO Id) (?)" )
    myTip = Hovertip(label, 'Match target tree meta data (size, mod-time (NOT FileId/inode)) to the meta-file in the target directory. Then:\n•Compare: display the result.')
    label.pack(side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=copy.copy(globvar.localStorageST.obj[iSelected]);  objST["leafFilterFirst"]=objST["leafFilterFirst_MT"] #or '.buvt-filterM'
      compareTreeToMetaSTOnly(**objST, **{"fiDir":objST["fiDirTarget"]}) 
    butCompareTreeToMetaSTOnly = tk.Button(frameTargetCompare, text="Compare", command=cb)
    #myTip = Hovertip(butCompareTreeToMetaSTOnly, 'Compare target tree to meta-file, size and mod-time only (WO file-id)')
    butCompareTreeToMetaSTOnly.pack( side = tk.LEFT)


        # frameCheck
    frameCheck = tk.Frame(root)
    frameCheck.pack(fill=tk.BOTH)
    label = tk.Label(frameCheck, text="Checking (calculate hashcodes) (?)" )
    myTip = Hovertip(label, 'Going through all the files in meta-file.')
    label.pack(side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=globvar.localStorageST.obj[iSelected]
      checkSummarizeMissing(**objST, **{"fiDir":objST["fiDirSource"]})
    butCheckSummarizeMissing = tk.Button(frameCheck, text="...Summarize missing files in source (?)", command=cb)
    myTip = Hovertip(butCheckSummarizeMissing, 'Going through all the files in meta-file.')
    butCheckSummarizeMissing.pack( side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      iSelected=globvar.localStorageOther.obj["iSelected"]
      objST=globvar.localStorageST.obj[iSelected]
      checkSummarizeMissing(**objST, **{"fiDir":objST["fiDirTarget"]})
    butCheckSummarizeMissing = tk.Button(frameCheck, text="...Summarize missing files in target (?)", command=cb)
    myTip = Hovertip(butCheckSummarizeMissing, 'Going through all the files in meta-file.')
    butCheckSummarizeMissing.pack( side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      objOther=globvar.localStorageOther.obj; iSelected=objOther["iSelected"]
      objST=globvar.localStorageST.obj[iSelected]
      check(**objST, **{"fiDir":objST["fiDirSource"]}, **objOther)
    butCheck = tk.Button(frameCheck, text="...Check source (?)", command=cb)
    myTip = Hovertip(butCheck, 'Calculate hashcodes')
    butCheck.pack( side = tk.LEFT)
    def cb():
      textbox.delete('1.0', tk.END)
      objOther=globvar.localStorageOther.obj; iSelected=objOther["iSelected"]
      objST=globvar.localStorageST.obj[iSelected]
      check(**objST, **{"fiDir":objST["fiDirTarget"]}, **objOther)
    butCheck = tk.Button(frameCheck, text="...Check target (?)", command=cb)
    myTip = Hovertip(butCheck, 'Calculate hashcodes')
    butCheck.pack( side = tk.LEFT)


      # iStart
    def saveIStart():
      iStart=int(entryIStart.get())
      globvar.localStorageOther.obj["iStart"]=iStart
      globvar.localStorageOther.writeStored()
      entryIStart.configure(background="white")
      butSaveIStart.pack_forget()
    butSaveIStart = tk.Button(frameCheck, text="Save", command=saveIStart)
    # def do_validation():
    #   value = entry.get()
    #   if value == "" or value.isnumeric(): return True
    #   return False
    # entry = tk.Entry(frameCheck, validate='key', validatecommand=do_validation)
    label = tk.Label(frameCheck, text="iStart: (?)" )
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
      if(boChanged): butSaveIStart.pack()
      else: butSaveIStart.pack_forget()
      
    #sv.trace("w", changef)
    #sv.set('0')
    sv.set(globvar.localStorageOther.obj["iStart"])
    sv.trace("w", lambda name, index, mode, sv=sv: changef(sv))
    entryIStart = tk.Entry(frameCheck, validate='key', validatecommand=vcmd, textvariable=sv)
    entryIStart.pack(side = tk.LEFT)
    myTip = Hovertip(entryIStart, 'iStart, start on this row of the meta-file -file')
    #entryIStart.bind('<FocusIn>', lambda ev:entryIStart.configure(background="green"))
    #entryIStart.bind('<FocusOut>', lambda ev:entryIStart.configure(background="white"))
  

    textbox = tk.Text(master=root, width=100, state=tk.NORMAL)
    textbox.pack(fill=tk.BOTH,expand=True)
    #textbox.grid(row=0, column=0)
    #textbox.insert("0.0", "new text to insert\n")  # insert at line 0 character 0
    self.myConsole=MyConsoleGui(textbox)

    # frameBottom = tk.Frame(root)
    # frameBottom.pack(fill=tk.BOTH, side=tk.BOTTOM)






