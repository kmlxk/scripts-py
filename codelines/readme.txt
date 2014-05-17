
简介
~~~~~~~~~~~~~~~~~
codelines.py用于统计项目中的代码量
Author: kmlxk0[at]gmail.com


使用方法
~~~~~~~~~~~~~~~~~

python codeline.py -d 项目路径
-h,--help: 打印帮助
-d,--dirpath : 项目文件夹路径

示例
~~~~~~~~~~~~~~~~~
python codeline.py  -d F:\workspace\vs2010\PISWeb

备注
~~~~~~~~~~~~~~~~~
特性：
1、使用了logging, getopt, re等模块
2、执行过程中的信息很多，详情可以查看codelines.log

待改善的地方：
1、判断注释行并排除
2、排除路劲参数化

