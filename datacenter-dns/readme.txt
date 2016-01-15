

##动态DNS更新脚本datacenter_dns.py##
DataCenter是基于PHP的个人数据存储中心，datacenter_dns.py用于更新客户端IP地址到DataCenter中，实现动态IP转换的功能。

- 基于python 2.x版本运行
- 不依赖第三方组件)

###使用简介###

python datacenter_dns.py -d 项目路径
-h,--help: 打印帮助
-s,--server : 服务器路径

###示例###

python datacenter_dns.py -s http://220.165.250.133:2195/datacenter/
