#! /usr/bin/env python
#_*_encoding:utf-8_*_
import logging
import time
from logging.handlers import TimedRotatingFileHandler

class SysLogger:

  def __init__(self, logFileDir, logPrefix):
    self.logger = logging.getLogger(logPrefix)
    logFile = '%s/%s.log'%(logFileDir, logPrefix)
    fh = TimedRotatingFileHandler(logFile, 'midnight', 1, 7)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    fh.setFormatter(formatter)
    self.logger.addHandler(fh)
  
  #设置日志级别
  def setLogLevel(self, logLevel):
    #10: DEBUG
    #20: INFO, default
    #30: WARNING
    #40: ERROR
    #50: CRITICAL

    self.logger.setLevel(logLevel)

  def debug(self, msg):
    self.logger.debug(msg)

  def info(self, msg):
    self.logger.info(msg)

  def warning(self, msg):
    self.logger.warning(msg)

  def error(self, msg):
    self.logger.error(msg)

  def critical(self, msg):
    self.logger.critical(msg)