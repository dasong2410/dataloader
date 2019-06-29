#! /usr/bin/env python
#_*_encoding:utf-8_*_
import ConfigParser

class CfgReader:

  def __init__(self, cfgFiles):
    self.conf = ConfigParser.ConfigParser()
    
    for cfg in cfgFiles:
      self.conf.read(cfg)

  #获取一个section下所有参数
  def getItems(self, section):
    items = self.conf.items(section)
    return items

  #获取多个参数值
  def getParams(self, section, params):
    self.section = section
    self.params = params
    self.arrayVal =[]

    paramArray = self.params.split(',')
    for i in range(0, len(arrayVal)):
      self.arrayVal.append(conf.get(self.section, paramArray[i]))
      return self.arrayVal

  #获取单个参数值
  def getParam(self, section, param):
    val = self.conf.get(section, param)
    return val

  #获取单个参数值
  def getParamInt(self, section, param):
    intVal = self.conf.getint(section, param)
    return intVal
    
  #获取单个参数值
  def getParamFloat(self, section, param):
    floatVal = self.conf.getfloat(section, param)
    return floatVal