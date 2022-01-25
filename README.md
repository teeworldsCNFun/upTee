![upTee](https://raw.github.com/upTee/upTee/master/uptee/static/simpleblue/img/logo_75.png)
upTee - Readme
=============================
upTee是一个开源的软件来帮助玩家在仅在网站上就可以轻松地启动[Teeworlds](https://teeworlds.com)游戏服务器
该软件用 [django](https://www.djangoproject.com/) 编写，还使用了许多其他的python模块。  
该项目由Sascha "SushiTee" Weichel创立，用于加快[teeworlds](https://teeworlds.com)地图的开发。他说服 David "Fisico" Gruber 美化网站。

基础需要
--------------------
* [python 2.7](http://www.python.org/) - 一种值得你好好探索的程序语言
* [setuptools](http://pypi.python.org/pypi/setuptools) - python的模块，用于下载包 <sup>[1]</sup>

制作要求
-----------------------
* [nginx](http://nginx.org/) - 高效的HTTP服务器 <sup>[2]</sup>
* [uwsgi](http://projects.unbit.it/uwsgi/) - 应用程序容器的服务器 <sup>[2]</sup>
* [PostgreSQL](http://www.postgresql.org/) - 世界上最先进的开源数据库 <sup>[2]</sup>
* [RabbitMQ](http://www.rabbitmq.com/) - AMQP 信息发送系统，用于Celery后台  <sup>[2]</sup>

可选要求
---------------------
* [memcached](http://memcached.org/) - 后台缓存 <sup>[3]</sup>

链接
-----
* __[Beta page](http://uptee.teesites.net)__
* __[Github repository](https://github.com/teeworldsCNFun/upTee/)__
* __[Issues](https://github.com/teeworldsCNFun/upTee/issues)__
* __[License](https://github.com/teeworldsCNFun/upTee/blob/master/LICENSE)__
* __[Contributors](https://github.com/teeworldsCNFun/upTee/blob/master/CONTRIBUTORS.md)__

帮助
-----
* __[Setting up a development server](https://github.com/teeworldsCNFun/upTee/blob/master/docs/development_server.md)__
* __[Setting up a production server](https://github.com/teeworldsCNFun/upTee/blob/master/docs/production_server.md)__
* __[Mod format](https://github.com/teeworldsCNFun/upTee/blob/master/docs/mod_format.md)__
* __[Config format](https://github.com/teeworldsCNFun/upTee/blob/master/docs/config_format.md)__

### 联系我们
* __IRC__ - [Webchat](http://webchat.quakenet.org/?channels=teeworlds-dev)<br>___irc://irc.quakenet.org/#teeworlds-dev___<br>#teeworlds-dev at irc.quakenet.org

注意
-----
__<sup>[1]</sup>__ 必须下载所有需要的python包<br>
__<sup>[2]</sup>__ 可以用其它配置，但不推荐<br>
__<sup>[3]</sup>__ 推荐这个但其它后台缓存也可以用

-----

upTee – © 2012 - 2015 [upTee](http://uptee.teesites.net/about/)
