#! /usr/bin/env python
#_*_encoding:utf-8_*_
class ProtocolBody:
  def __init__(self, name):
    self.name = name
  
  def setName(self, name):
    self.name = name
  
  def getName(self):
    return self.name
  
  def setThread(self, thread):
    self.thread = thread
  
  def getThread(self):
    return self.thread
  
  def setDirect(self, direct):
    self.direct = direct
  
  def getDirect(self):
    return self.direct
  
  def setTable(self, table):
    self.table = table
  
  def getTable(self):
    return self.table
  
  def setCols(self, cols):
    self.cols = cols
  
  def getCols(self):
    return self.cols
  
  def setBcp(self, bcp):
    self.bcp = bcp
  
  def getBcp(self):
    return self.bcp
  
  def setStat(self, stat):
    self.stat = stat
  
  def getStat(self):
    return self.stat

  def setInStat(self, inStat):
    self.inStat = inStat
  
  def getInStat(self):
    return self.inStat
