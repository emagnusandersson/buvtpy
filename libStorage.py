
import json
#import settings
#import globvar

class MyLocalStorage:
  def __init__(self, path):
    self.path=path
    self.obj=None
  def getStored(self, objDefault):
    boFileNotFound=False
    try:
      f = open(self.path)
      data = f.read()
    except FileNotFoundError as e:
      print("Creating file: "+str(self.path))
      boFileNotFound=True
      self.obj=objDefault
      self.writeStored()
      return

      # Parse data
    try:
      self.obj = json.loads(data)
    except:
      print("Parsing failed: "+str(self.path)+', using default')
      self.obj=objDefault
    #return stored
  def writeStored(self):
    jsonData = json.dumps(self.obj, indent=2)
    with open(self.path, "w") as outfile:
      outfile.write(jsonData)