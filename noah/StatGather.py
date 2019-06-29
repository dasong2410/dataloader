#! /usr/bin/env python
#_*_encoding:utf-8_*_
import re
import os
import glob
import time
import datetime
import shutil
import subprocess

class StatGather:
  def __init__(self, protocolBodyDict, statLogger, statLogDir, bcpDir, localDbid, toolkit, statDelay):
    self.protocolBodyDict = protocolBodyDict
    self.statLogger = statLogger
    self.statLogDir = statLogDir
    self.bcpDir = bcpDir
    self.localDbid = localDbid
    self.toolkit = toolkit
    self.statDelay = statDelay

  """
    生成统计信息bcp记录，字段格式为
    proname,upareaid,datasource,count,badcount,datetime,year,month,day,hour,datatype
    字段用\t分隔
  """
  def writeRec(self, statName, sqlldrLogFile):
    fields = os.path.basename(sqlldrLogFile).split('_')
    upAreaId = fields[-3]
    datasource = fields[-2]
    
    #打开sqlsldr日志文件
    f = open(sqlldrLogFile, 'r')
    reader = f.read()
    
    #获取成功和失败条数
    try:
      succRows = re.findall(r'\d* Row[s]? successfully', reader)[0].split(' ')[0]
      failRows= re.findall(r'\d* Row[s]? not loaded due to data errors', reader)[0].split(' ')[0]
    except Exception,ex:
      succRows = 0
      failRows = 0
    
    #关闭日志文件
    f.close()

    #获取时间
    #sec = int(fields[1])
    #dt = self.toolkit.sec2date(sec)
    #date = datetime.datetime.strftime(dt, '%Y%m%d')
    #year = datetime.datetime.strftime(dt, '%Y')
    #month = datetime.datetime.strftime(dt, '%m')
    #day = datetime.datetime.strftime(dt, '%d')
    #hour = datetime.datetime.strftime(dt, '%H')
    
    #获取当前时间
    dt = time.localtime(time.time())
    date = time.strftime('%Y%m%d%H',dt)
    year = time.strftime('%Y',dt)
    month = time.strftime('%m',dt)
    day = time.strftime('%d',dt)
    hour = time.strftime('%H',dt)
    
    #组织bcp记录
    rec = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(statName, upAreaId, datasource, succRows, failRows, date, year, month, day, hour, 'TABLE')

    subprocess.call("echo -e \"%s\" >> %s.tmp"%(rec, self.statBcpFile), shell=True)
  
  #移动bcp文件到入库目录
  def moveFile(self):
    try:
      #将bcp文件移到入库目录
      if os.path.exists(self.statBcpFile + '.tmp'):
        shutil.move(self.statBcpFile + ".tmp", self.bcpDir + "/" + self.localDbid)
        shutil.move("%s/%s/%s.tmp"%(self.bcpDir, self.localDbid, os.path.basename(self.statBcpFile)), "%s/%s/%s.bcp"%(self.bcpDir, self.localDbid, os.path.basename(self.statBcpFile)))
        self.statLogger.info("生成文件：%s.bcp"%(os.path.basename(self.statBcpFile)))
    except Exception,ex:
      self.statLogger.info("文件名：%s.bcp 错误信息（移动文件到localDbid目录）：%s"%(os.path.basename(self.statBcpFile), ex))
  
  def genBcp(self, statBcpFile):
    self.statBcpFile = statBcpFile
    
    #获取当前时间
    #today = datetime.date.today()
    #year = today.year
    #month = today.month
    #day = today.day
    
    #计算统计数据过期临界点
    #keepPt = datetime.datetime(year, month, day)-datetime.timedelta(seconds=self.statDelay)

    #根据协议名扫描日志文件
    for prot, protocolBody in self.protocolBodyDict.items():
      try:
        statName = protocolBody.getStat()
        #判断是否需要统计
        if statName is not None:
          sqlldrLogFiles = glob.glob("%s/%s.log"%(self.statLogDir, protocolBody.getBcp()))
          
          #处理扫描到的日志文件
          for sqlldrLogFile in sqlldrLogFiles:
            try:
              if os.path.exists(sqlldrLogFile):
                #sec = os.path.basename(sqlldrLogFile).split('_')[1]
                
                #过期的统计数据不入库
                #if self.toolkit.sec2date(int(sec))>=keepPt:
                #写bcp记录
                self.writeRec(statName, sqlldrLogFile)
                
                #删除处理过的日志文件
                os.remove(sqlldrLogFile)
                self.statLogger.info("日志文件已处理，并删除：%s"%(os.path.basename(sqlldrLogFile)))
                #else:
                #  self.statLogger.info("日志文件过期，不生成统计信息：%s"%(os.path.basename(sqlldrLogFile)))
            except Exception,ex:
              self.statLogger.info("协议：%s 日志文件：%s 错误信息：%s"%(prot.upper(), sqlldrLogFile, ex))
      except Exception,ex:
        self.statLogger.info("获取协议%s对应日志文件失败：%s"%(prot.upper(), ex))
