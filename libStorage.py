
import json
import settings
import globvar

class MyLocalStorage:
  def __init__(self, flStored):
    self.flStored=flStored
    self.obj=None
  def getStored(self, objDefault):
    try:
      f = open(self.flStored)
      self.obj = json.load(f)
    #except FileNotFoundError as e:
    except:
      self.obj=objDefault
    #return stored
  def writeStored(self):
    jsonData = json.dumps(self.obj, indent=2)
    with open(self.flStored, "w") as outfile:
      outfile.write(jsonData)