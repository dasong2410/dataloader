#! /usr/bin/env python
#_*_encoding:utf-8_*_

import os
import re
import subprocess
from noah import CfgReader

#程序根据目录
ROOT_DIR = os.path.split(os.path.realpath(__file__))[0]

#协议文件内容模板
protModule = """<?xml version='1.0' encoding='utf-8' ?>
<protocols>
  <protocol name='%s' direct='false'%s>
    <table>%s</table>
    <cols>%s</cols>
    <bcp>%s</bcp>
    <stat>%s</stat>
    <instat>0</instat>
  </protocol>
</protocols>"""

#正则匹配表字段
p = re.compile('\s*\(\s*(.+)\s*\)\s*', re.S)

#配置文件
v1cfg = ROOT_DIR + '/etc/dbnbase.conf'
v2cfg = ROOT_DIR + '/etc/dbn.cfg'

CFG_FILES = [v1cfg, v2cfg]

#线程列表
thdProt = ['VIRTUALID','HARDCHARACTER']

#配置文件读取
cfgReader = CfgReader.CfgReader(CFG_FILES)

#输出协议文件
def output(prot, tab, cols, bcp, statName, dir):
  m = p.match(cols)
  if m:
    if prot in thdProt:
      thd = " thread='noahdb'"
    else:
      thd = ''
    
    protCfg = protModule%(prot, thd, tab, m.group(1), bcp, statName)
    subprocess.call("echo -e \"%s\" > %s/etc/%s/%s.xml"%(protCfg, ROOT_DIR, dir, tab.lower()), shell=True)

#v1版本
def conv1():
  dynamic = cfgReader.getItems('DBNDYNAMIC')
  
  #协议与bcp文件名对应关系
  protBcp = eval(cfgReader.getParam('DBNPRIVATE', 'bcppros'))
  
  #协议与统计数据名称对应关系
  protStat = eval(cfgReader.getParam('DBNPRIVATE', 'statpros'))
  
  #遍历协议，生成配置文件
  for protInfo in dynamic:
    prot = protInfo[0].upper()
    tab = eval(protInfo[1]).keys()[0]
    cols = eval(protInfo[1]).values()[0]
    bcp = protBcp[prot]
    
    if prot in protStat:
      statName = protStat[prot]
    else:
      statName = prot
    
    output(prot, tab, cols, bcp, statName, 'v1')

#v2版本
def conv2():
  #协议与表名对应关系
  protTab = eval(cfgReader.getParam('MAPPING', 'prot_tab'))
  
  #表名与字段对应关系
  tabCols = eval(cfgReader.getParam('MAPPING', 'tab_cols'))
  
  #协议与bcp文件名对应关系
  protBcp = eval(cfgReader.getParam('MAPPING', 'prot_bcp'))
  
  #协议与统计数据名称对应关系
  protStat = eval(cfgReader.getParam('MAPPING', 'prot_stat'))
  
  #遍历协议，生成配置文件
  for prot in protTab:
    tab = protTab[prot]
    bcp = protBcp[prot]
    cols = tabCols[tab]
    
    if prot in protStat:
      statName = protStat[prot]
    else:
      statName = prot
    
    output(prot, tab, cols, bcp, statName, 'v2')

#转换
if os.path.exists(v1cfg):
  conv1()

if os.path.exists(v2cfg):
  conv2()