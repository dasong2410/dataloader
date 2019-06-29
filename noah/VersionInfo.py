#! /usr/bin/env python
#_*_encoding:utf-8_*_

class VersionInfo:

  def __init__(self, program, version, date, author):
    self.program = program
    self.version = version
    self.date = date
    self.author = author

  #打印版本信息
  def info(self):
    print """
  Name: \033[33;2m%s\033[0m
  Version: \033[33;2m%s\033[0m
  Date: \033[33;2m%s\033[0m
  Author: \033[33;2m%s\033[0m
    """ %(self.program, self.version, self.date, self.author)

  #打印帮助信息
  def usage(self):
    print """
  Usage: %s
    -v 打印版本信息
    -h 打印帮助信息
    """%(self.program)