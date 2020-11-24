# -*- coding: UTF-8 -*-
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

import os
from os import path

project_path = path.abspath(os.curdir)
data_path = path.join(project_path, 'data/全市场作为对照样本相应的数据')
factors_path = path.join(data_path, 'factors')
resset_path = path.join(data_path, 'RESSET数据库')
wind_path = path.join(data_path, 'Wind数据库')