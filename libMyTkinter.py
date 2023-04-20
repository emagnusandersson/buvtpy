
import tkinter as tk
from tkinter import ttk
import settings
import globvar


  
class MyConsoleGui:
  def __init__(self, textbox):
    self.textbox=textbox; self.yMark=1; self.xMark=0
  def clear(self): self.textbox.delete('1.0', tk.END); self.yMark=1; self.xMark=0
  def save(self):
    y,x=self.textbox.index(tk.INSERT).split('.');
    self.yMark=int(y); self.xMark=int(x); return self
  def restore(self):
    self.textbox.mark_set(tk.INSERT, f"{self.yMark}.{self.xMark}"); return self
  def clearBelow(self):
    strIns=self.textbox.index(tk.INSERT)
    self.textbox.delete(strIns, 'end-1c'); return self
  def cursorUp(self):
    yT, xT=self.textbox.index(tk.INSERT).split('.'); yT=int(yT); xT=int(xT)
    if(yT>1): yT-=1
    self.textbox.mark_set(tk.INSERT, f"{yT}.{xT}")
    return self
  def makeSpaceNSave(self):
    #self.print('\n\n'); self.cursorUp(); self.cursorUp();
    self.save(); return self
  def myReset(self):
    self.restore(); self.clearBelow(); return self
  #def setCur(self): self.textbox.insert(tk.END,""); return self   #place_info() text.see(END)
  def print(self, strA):
    self.textbox.insert(tk.INSERT, strA); return self
  def printNL(self, strA): self.print(strA+'\n'); return self
  def log(self, strA):self.print(strA+'\n'); return self
  def error(self, strA): 
    # if(isinstance(strA, Error)):  strA=strA.message
    # el
    if(type(strA)=='dict' and 'message' in strA): strA=strA.message
    self.print("ERROR: "+strA+'\n')
    return self

