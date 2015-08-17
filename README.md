#万象优图(Cloud Image)迁移工具Linux版

##基本功能
将其他方式存储的图片批量上传到万象优图，目前支持3种存储方式的上传。

1. 图片在本地存储，直接将某目录下的所有文件上传到万象优图。

2. 指定URL列表文件，文件中包含若干张图片的URL。下载列表文件中的每一张图片并上传到万象优图。

3. 指定七牛云存储的账号和空间名，迁移该指定空间中的所有文件或部分文件到万象优图。

##使用方法

以下所有bash脚本均在bin目录下。

1. 启动迁移，运行start.sh脚本，工具会按照配置文件中的配置开始运行

2. 查看迁移状态，运行stat.sh脚本，会在屏幕上持续输出迁移状态，按Ctrl+C退出查看

3. 停止迁移，运行stop.sh。

4. 获取迁移失败的文件列表及信息，运行get_failed.sh。

5. 清空日志信息，运行clean.sh。

在迁移过程中运行stop.sh脚本停止迁移，这一过程可能需要等待几秒钟的时间以保证已经开始的任务正常结束并写入日志。如果需要强制停止，运行stop.sh -f。

停止迁移之后如果没有清空日志并且没有修改配置信息，再次启动迁移会继续上次的迁移任务，并且重试所有失败记录。

##配置文件

配置文件中section name和option name不区分大小写。

###迁移类型

`基本功能`一节中描述的迁移类型，填写其序号。例如迁移本地文件：


```
[MigrateInfo]
migrate.type = 1
```


###本地文件系统

若迁移类型为1，则需要配置上传的本地根目录位置，必须为绝对路径。上传后的file id不包含根目录。例如：

```
[Local]
local.image_root_path = /data/temp/image
```

###URL列表文件

若迁移类型为2，则需要配置URL列表文件的位置，必须为绝对路径。例如：

```
[URLList]
url.url_list_file_path = /data/url_list
```

###七牛云存储账号信息

若迁移类型为3，则需要配置七牛云存储账号相关信息。

`qiniu.bucket`填写被迁移的空间名；`qiniu.domain`为七牛域名，需要包含协议类型（如http://）；若只迁移一部分则需要提供`qiniu.start_offset`和`qiniu.total_num`，`qiniu.start_offset`从0计；若空间开启了防盗链，需要在`qiniu.referer`中指定访问来源域名，同样需要包含协议类型（如http://）；如果是私有空间，将`qiniu.isprivate`设置为`1`或`True`。

```
[Qiniu]
qiniu.bucket = 
qiniu.AccessKey = 
qiniu.SecretKey = 
qiniu.domain = 
qiniu.start_offset = 
qiniu.total_num = 
qiniu.referer = 
qiniu.isprivate = 
```

###万象优图账号信息

从[万象优图图片空间](http://console.qcloud.com/image/bucket)中查看项目ID和空间名称，分别填写到`appinfo.appid`和`appinfo.bucket`；从[万象优图项目设置](http://console.qcloud.com/image/project)中查看Secret ID和Secret Key分别填写到`appinfo.secretID`和`appinfo.secretKey`。

```
[AppInfo]
appinfo.appid = 
appinfo.secretID = 
appinfo.secretKey = 
appinfo.bucket = 
```

###并行上传

`Concurrency`控制同时运行的上传进程数目，请根据上行带宽和机器配置适当调整该数值。必须提供一个大于0的整数。

```
[ToolConfig]
Concurrency = 100
```

##致谢

本工具包含了以下开源项目

1. [Requests: HTTP for Humans](http://www.python-requests.org/en/latest/)

2. [Cloud Image Python 2 SDK](https://github.com/tencentyun/python-sdk)

3. [Qiniu Resource Storage SDK for Python](https://github.com/qiniu/python-sdk)

##许可
基于MIT开源协议发布，详见[LICENSE](LICENSE)。
