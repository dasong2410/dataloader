#! /usr/bin/env python
#_*_encoding:utf-8_*_
import getopt
import os
import datetime
#import cx_Oracle
import commands
import shutil

class Toolkit:

  def __init__(self, logger):
    self.logger = logger

  #检查数据库状态是否正常
  #def checkDbStatus(self, userpwd):
  #  try:
  #    dbConn = cx_Oracle.connect(userpwd)
  #  except Exception, ex:
  #    self.logger.info("数据库状态异常：%s %s" %(userpwd, ex))
  #    return 0
  #  else:
  #    self.logger.info("数据库状态正常：%s" %(userpwd))
  #    return 1
      
  #判断配置文件是否存在
  #0：存在
  #>0：不存在
  def checkFileExist(self, cfgFiles):
    cnt = 0
    for cfg in cfgFiles:
      if os.path.exists(cfg):
        self.logger.info("%s 存在" %(cfg))
      else:
        self.logger.info("%s 不存在" %(cfg))
        cnt += 1
    
    return cnt
        
  #脚本参数的异常处理
  def getOpts(self, options):
    try:
      opts, args = getopt.getopt(options, "vhd:", ["help", "version"])
      return opts
    except getopt.GetoptError:
      self.logger.info("%s 参数不支持" %(options))
      sys.exit(2)

  #脚本参数的异常处理
  def mkdirs(self, dir):
    if os.path.exists(dir):
      self.logger.info("%s 存在" %(dir))
    else:
      os.makedirs(dir)
      self.logger.info("%s 创建成功" %(dir))
    
    return dir

  #绝对秒数转为日期
  def sec2date(self, sec):
    epoch = datetime.datetime(1970, 1, 1, 8)
    incr = datetime.timedelta(seconds=sec)
    return epoch + incr

  #日期转绝对秒数
  def date2sec(self, dt):
    epoch = datetime.datetime(1970, 1, 1, 8)
    dest = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    diff = dest - epoch
    sec = diff.days*86400 + diff.seconds
    return sec
  
  #判断所给进程是否已在运行
  def isRunning(self, progName):
    procCnt = commands.getoutput("ps -ef | grep %s | grep -cv grep"%(progName))
    return int(procCnt)

  #删除文件
  def remove(self, dest):
    try:
      os.remove(dest)
    except Exception,ex:
      print ex
  
  #copy，只用于copy文件
  def copy(self, src, dest):
    self.remove(dest)
    try:
      shutil.copy(src, dest)
    except Exception,ex:
      print ex
  
  #move，只用于move文件
  def move(self, src, dest):
    self.remove(dest)
    try:
      shutil.move(src, dest)
    except Exception,ex:
      print ex