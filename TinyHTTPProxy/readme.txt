
TinyHttpPoxy是一個簡單的Http代理程式，但是有一個不足的地方是不支持二級代理，
文章http://www.cnblogs.com/lexus/archive/2013/01/08/2851565.html中提到的代码支持带验证的二级代理

但是没法支持带验证信息的代理，
于是在HTTP请求中增加了用户名密码信息，发送到一级代理即可
根据同样的方法，HTTPS二级代理也是类似，
一增加的步骤是在CONNECT阶段增加用户名密码信息，发送到一级代理即可
Author: kmlxk0[at]gmail.com
