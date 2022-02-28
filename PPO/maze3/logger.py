#!/usr/bin/env python
# encoding: utf-8
"""
@author: HHD
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited. 
@contact: 2529342549@qq.com
@software: pycharm
@file: logger.py
@time: 2022/2/12 下午5:07
@desc:
"""
import logging


class Log(object):
    def __init__(self, logger=None):
        '''
         指定保存日志的文件路径，日志级别，以及调用文件
         将日志存入到指定的文件中
        '''
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.INFO)
        # 创建一个handler，用于写入日志文件
        self.log_name = './data/output1.log'
        fh = logging.FileHandler(self.log_name, mode='a')  # 追加模式 这个是python2的
        # fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8') # 这个是python3的
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s, %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def getlog(self):
        return self.logger
