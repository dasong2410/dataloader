#! /usr/bin/env python
#_*_encoding:utf-8_*_
import os
import glob
import sys
from xml.etree import ElementTree
from noah import VersionInfo
from noah import Toolkit
from noah import CfgReader
from noah import SysLogger
from noah import ProtocolBody

#程序根据目录
ROOT_DIR = os.path.split(os.path.realpath(__file__))[0]

#日志文件名
sysLogDir = ROOT_DIR + '/log/sys'

commomCfg = ROOT_DIR + "/etc/common.xml"

#日志级别
#log level
#10: DEBUG
#20: INFO, default
#30: WARNING
#40: ERROR
#50: CRITICAL
logLevel = 20

#bcp数据入库日志
dataLogger = SysLogger.SysLogger(sysLogDir, 'dataloader')
dataLogger.setLogLevel(logLevel)

#生成统计bcp文件日志
statLogger = SysLogger.SysLogger(sysLogDir, 'statloader')
statLogger.setLogLevel(logLevel)

#初始化工具类
toolkit = Toolkit.Toolkit(dataLogger)

#检查配置文件是否存在
if (toolkit.checkFileExist([commomCfg]) != 0):
  dataLogger.info("配置文件common.xml不存在")
  print "配置文件common.xml不存在"
  sys.exit()

#配置文件common.xml解析，解析失败程序会退出
try:
  #根结点
  root = ElementTree.parse(commomCfg)
  
  #版本信息
  program = root.find("versions/program").text
  version = root.find("versions/version").text
  date = root.find("versions/date").text
  author = root.find("versions/author").text
  
  #通用配置
  #pf_usrpwd = root.find("common/data_interval").text
  dataInterval = int(root.find("common/data_interval").text)
  statInterval = int(root.find("common/stat_interval").text)
  statDelay = int(root.find("common/stat_delay").text)
  protQueueLen = int(root.find("common/prot_queue_len").text)
  bcpDir = root.find("common/bcp_dir").text
  homeDir = root.find("common/home_dir").text
  localDbid = root.find("common/local_dbid").text
except Exception,ex:
  dataLogger.info("配置文件common.xml格式可能有错误，请联系开发人员")
  print "配置文件common.xml格式可能有错误，请联系开发人员"
  sys.exit()

#版本信息
versionInfo = VersionInfo.VersionInfo(program, version, date, author)

#db列表
dbs = root.findall("dbs/db")

#协议配置文件
protFiles = glob.glob(ROOT_DIR + "/etc/protocols/*.xml")
dataLogger.debug("协议配置文件数据：%s"%(len(protFiles)))

#协议列表
protocolBodyDict = {}
threads = {}
protCnt = 0
for protFile in protFiles:
  try:
    protRoot = ElementTree.parse(protFile)
    prots = protRoot.findall("protocol")
    
    #协议配置文件包含协议数
    dataLogger.debug("协议配置文件：%s 协议数：%s"%(protFile, len(prots)))
    
    for prot in prots:
      protName = prot.get("name")
      
      #打印协议配置文件中每种协议
      dataLogger.debug("协议配置文件：%s 协议：%s"%(protFile, protName))
      
      #生成入库线程名，如果协议中配置了协议名，则使用配置的协议名；否则按协议队列大小，生成线程名
      threadName = prot.get("thread")
      if threadName is None:
        #线程名
        threadName = "thread%s"%(protCnt/protQueueLen+1)
        
        #协议数累加
        protCnt += 1
      
      protocolBody = ProtocolBody.ProtocolBody(protName)
      protocolBody.setDirect(prot.get("direct"))
      protocolBody.setThread(threadName)
      protocolBody.setTable(prot.find("table").text)
      protocolBody.setCols(prot.find("cols").text)
      protocolBody.setBcp(prot.find("bcp").text)
      protocolBody.setStat(prot.find("stat").text)
      protocolBody.setInStat(int(prot.find("instat").text))
      
      if protName in protocolBodyDict:
        dataLogger.info("协议名重复，文件：%s 协议：%s"%(protFile, protName))
      else:
        protocolBodyDict[protName] = protocolBody
  
        #生成线程与协议对应关系
        if threadName in threads:
          if protName not in threads[threadName]:
            threads[threadName].append(protName)
        else:
          threads[threadName] = [protName]
  except Exception,ex:
    dataLogger.info("协议配置文件错误：%s"%(protFile))

#线程日志列表
threadLogList = {}

#创建各线程所对应的日志文件
#文件名格式为：[dbid]_[线程名].log
for db in dbs:
  dbid = db.get("id")
  
  for thread in threads:
    thdName = dbid + "_" + thread
    threadLogList[thdName] = SysLogger.SysLogger(sysLogDir, thdName)
    threadLogList[thdName].setLogLevel(logLevel)

#日志目录
logDir = toolkit.mkdirs(ROOT_DIR + '/log')
sqlldrLogDir = toolkit.mkdirs(logDir + '/log')
statLogDir = toolkit.mkdirs(logDir + '/stat/log')
statBcpDir = toolkit.mkdirs(logDir + '/stat/bcp')
badLogRoot = toolkit.mkdirs(logDir + '/bad')

#控制文件目录
ctlDir = toolkit.mkdirs(ROOT_DIR + '/ctl')

#坏文件目录
badFileRoot = toolkit.mkdirs(ROOT_DIR + '/bad')