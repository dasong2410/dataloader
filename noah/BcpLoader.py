#! /usr/bin/env python
#_*_encoding:utf-8_*_
import glob
import os
import time
import re
import shutil
import subprocess
import threading
import StatGather

class BcpLoader(threading.Thread):

  def __init__(self, dbid, userpwd, thdName, prots):
    self.prots = prots
    self.dbid = dbid
    self.userpwd = userpwd
    self.thdName = thdName
    threading.Thread.__init__(self, name=thdName)

  #设置所需的所有变量
  def setAll(self, bcpDir, ctlDir, sqlldrLogDir, badFileRoot, badLogRoot, statLogDir, statBcpFile, localDbid, protocolBodyDict, logger, toolkit):
    self.bcpDir = bcpDir
    self.ctlDir = ctlDir
    self.sqlldrLogDir = sqlldrLogDir
    self.badFileRoot = badFileRoot
    self.badLogRoot = badLogRoot
    self.statLogDir = statLogDir
    self.statBcpFile = statBcpFile
    self.localDbid = localDbid
    self.protocolBodyDict = protocolBodyDict
    self.logger = logger
    self.toolkit = toolkit

  #创建坏文件目录
  def mkBadDir(self):
    levelList = ['WARN','FATAL']

    #当前时间
    self.today = time.strftime('%Y%m%d', time.localtime(time.time()))
    for logLevel in levelList:
      badFileDir = "%s/%s/%s"%(self.badFileRoot, logLevel, self.today)
      badLogDir = "%s/%s/%s"%(self.badLogRoot, logLevel, self.today)
      if not os.path.exists(badFileDir):
        os.makedirs(badFileDir)
      
      if not os.path.exists(badLogDir):
        os.makedirs(badLogDir)

  #导入bcp数据
  def loadData(self):
    #生成控制文件
    f = open(self.ctlFile, 'w')
    print>> f,"LOAD DATA\n"
    print>> f,"INFILE '%s'\n"%(self.srcFile)
    print>> f,"APPEND INTO TABLE %s\n"%(self.tabName)
    print>> f,"FIELDS TERMINATED BY '\\t' TRAILING NULLCOLS\n"
    print>> f,"(%s)"%(self.fields)
    f.close()
    
    self.logger.info('控制文件：%s'%(os.path.basename(self.ctlFile)))

    self.logger.info('开始入库：%s'%(os.path.basename(self.srcFile)))
    
    #sqlldr调用
    cmd = 'sqlldr %s control=%s direct=%s log=%s bad=%s rows=3000 errors=-1 date_cache=8192 bindsize=2048000 readsize=10240000'%(self.userpwd, self.ctlFile, self.direct, self.logFile, self.badFile)
    retCode = subprocess.call(cmd, shell=True)
    
    #sqlldr入库日志
    self.logger.info('入库日志：%s'%(os.path.basename(self.logFile)))
    
    #解析sqlldr日志文件
    self.parseLogFile()

  #解析sqlldr日志文件
  def parseLogFile(self):
    #打开sqlsldr日志文件
    f = open(self.logFile, 'r')
    reader = f.read()
    
    #获取成功和失败条数
    try:
      succRows = re.findall(r'\d* Row[s]? successfully', reader)[0].split(' ')[0]
      failRows= re.findall(r'\d* Row[s]? not loaded due to data errors', reader)[0].split(' ')[0]
    except Exception,ex:
      succRows = 0
      failRows = 0
      self.logger.debug("解析日志文件失败：%s"%(self.logFile))
    
    #关闭日志文件
    f.close()
    
    """
    retcode:
      0：成功，全部数据入库成功
      1：警告，部分数据入库失败
      2：失败，全部数据入库失败
    """
    #判断入库结果
    if (int(failRows) == 0) and (int(succRows) > 0):
      #入库成功
      retcode = 0
      logLevel = 'SUCCESS'
      retStatus = '成功'
    elif (int(failRows) > 0) and (int(succRows) > 0):
      #入库警告
      retcode = 1
      logLevel = 'WARN'
      retStatus = '警告'
    elif (int(succRows) == 0):
      #入库完全失败
      retcode = 2
      logLevel = 'FATAL'
      retStatus = '失败'

    #备份坏文件
    if os.path.exists(self.badFile):
      self.toolkit.move(self.badFile, "%s/%s/%s/%s"%(self.badFileRoot, logLevel, self.today, os.path.basename(self.badFile)))
      self.logger.debug("备份坏文件：%s"%(self.badFile))
    elif (retcode != 0):
      self.toolkit.copy(self.srcFile, "%s/%s/%s/%s"%(self.badFileRoot, logLevel, self.today, os.path.basename(self.srcFile)))
      self.logger.debug("备份坏文件：%s"%(self.srcFile))
    
    #删除源文件
    self.toolkit.remove(self.srcFile)
    self.logger.debug("删除源文件：%s"%(self.srcFile))
    
    #入库不完全成功，copy错误日志到相应目录
    if (retcode != 0):
      self.toolkit.copy(self.logFile, "%s/%s/%s/%s"%(self.badLogRoot, logLevel, self.today, os.path.basename(self.logFile)))
      self.logger.debug("备份错误入库日志：%s"%(self.logFile))

    #将日志文件移至stat目录，后续统计入库信息；不需要统计的则删除
    if self.stat is not None:
      self.toolkit.move(self.logFile, "%s/%s"%(self.statLogDir, os.path.basename(self.logFile)))
      self.logger.debug("移动入库日志到统计目录：%s"%(self.logFile))
    else:
      self.toolkit.remove(self.logFile)
      self.logger.debug("删除入库日志：%s"%(self.logFile))

    #输出日志
    self.logger.info('入库状态：%s'%(retStatus))
    self.logger.info('成功条数：%s'%(succRows))
    self.logger.info('失败条数：%s\n'%(failRows))

  #导入bcp
  def loadBcp(self):
    for prot in self.prots:
      try:
        protocolBody = self.protocolBodyDict[prot]
        
        #每次抓取文件个数限制
        bcpFileMask = "%s/%s/%s.bcp"%(self.bcpDir, self.dbid, protocolBody.getBcp())
        bcpFiles = glob.glob(bcpFileMask)[:1000]
        
        self.logger.debug("协议：%s，%s"%(prot, bcpFileMask))
        self.logger.debug("线程:%s，协议:%s，bcp文件数:%s\n"%(self.thdName, prot.upper(), len(bcpFiles)))
        
        self.tabName = protocolBody.getTable()
        self.fields = protocolBody.getCols()
        self.direct = protocolBody.getDirect()
        self.stat = protocolBody.getStat()
        self.inStat = protocolBody.getInStat()
        self.protocal = prot
        self.ctlFile = "%s/CTL_%s_%s.ctl"%(self.ctlDir, prot, self.thdName)
      except Exception,ex:
        self.logger.info("获取协议%s对应bcp失败：%s"%(prot.upper(), ex))
      
      for bcpFile in bcpFiles:
        try:
          if os.path.exists(bcpFile):
            #文件名
            fileName = os.path.basename(bcpFile)
            
            #生成bcp文件行数 统计信息
            if (self.inStat == 1):
              bcpSec = fileName.split('_')[1]
              subprocess.call("echo -e \"%s\t$(wc -l %s | awk -F' ' '{print $1}')\tin\tdataloader\t%s\" >> %s.tmp"%(fileName, bcpFile, bcpSec, self.statBcpFile), shell=True)
            
            #获取bcp文件前缀，bcp文件名以.bcp结尾
            fileNamePrefix = fileName.split('.')[0]
            
            #获取控件文件等所需元数据
            self.srcFile = bcpFile
            self.badFile = "%s/%s"%(self.badFileRoot, fileNamePrefix)+'.bcp'
            self.logFile = "%s/%s"%(self.badLogRoot, fileNamePrefix)+'.log'
            
            #创建坏文件目录
            self.mkBadDir()
            
            #导入bcp数据
            self.loadData()
        except Exception,ex:
          self.logger.info("协议：%s 文件名：%s 错误信息：%s"%(prot.upper(), bcpFile, ex))
  
    try:
      #move统计文件到入库目录
      if os.path.exists(self.statBcpFile + '.tmp'):
        shutil.move(self.statBcpFile + '.tmp', self.bcpDir + "/" + self.localDbid)
        shutil.move("%s/%s/%s.tmp"%(self.bcpDir, self.localDbid, os.path.basename(self.statBcpFile)), "%s/%s/%s.bcp"%(self.bcpDir, self.localDbid, os.path.basename(self.statBcpFile)))
        self.logger.info("生成文件：%s.bcp\n"%(os.path.basename(self.statBcpFile)))
    except Exception,ex:
      self.logger.info("协议：%s 文件名：%s.bcp 错误信息（移动文件到localDbid目录）：%s"%(prot.upper(), os.path.basename(self.statBcpFile), ex))
  
  def run(self):
    self.loadBcp()
