#万象优图(Cloud Image)迁移工具

##基本功能
将其他方式存储的图片批量上传到万象优图，目前支持4种存储方式的上传。

1. 图片在本地存储，直接将某目录下的所有文件上传到万象优图。

2. 指定URL列表文件，文件中包含若干张图片的URL。下载列表文件中的每一张图片并上传到万象优图。

3. 指定七牛云存储的账号和空间名，迁移该指定空间中的所有文件到万象优图。

4. 指定阿里云oss的账号和空间名，迁移该指定空间中的所有文件到万象优图。

本工具目前支持类Unix操作系统。推荐在Linux或Mac OS X下使用Python 2.7运行。

##使用方法

以下所有bash脚本均在bin目录下。


1. 开始上传，运行start.sh脚本，程序将按照配置文件中配置开始运行。

2. 查看上传状态，运行stat.sh脚本，会在屏幕上输出工作进度。

3. 暂停上传，运行stop.sh。

4. 获取上传失败的文件列表及错误信息，运行view_failed.sh

5. 清空日志，运行clean.sh。

start.sh脚本首先扫描待上传的任务提交到任务列表，然后开始上传。如果第一个过程被打断，下次运行start.sh会重新扫描待上传的任务；如果第二个过程被打断，下次运行start.sh会继续上传。如果需要强制刷新任务列表请运行`start.sh -f`。

上传完成后再次运行start.sh会重试失败的任务。

奇奇怪怪的操作（例如在运行过程中修改配置文件中的关键属性，运行过程中用其他程序读写日志文件，上传过程中清空日志等）会导致不可预知的行为。



##配置文件

配置文件位于conf/config.ini，请参照config.ini.template和以下说明编写配置文件。
配置文件中section name和property name (option name)不区分大小写；value除特殊说明外，区分大小写。

###上传类型

[基本功能](#基本功能)中描述的上传类型，填写Local、URLList、Qiniu、Oss中的一个。例如上传本地文件：


```
[MigrateInfo]
migrate.type = Local
```


###本地文件系统

若上传类型为Local，则需要配置上传的本地根目录位置，必须为绝对路径。上传后的file id不包含根目录。例如：

```
[Local]
local.image_root_path = /root/data/images/
```

###URL列表文件

若上传类型为URLList，则需要配置URL列表文件的位置，必须为绝对路径。例如：

```
[URLList]
url.url_list_file_path = /data/url_list
```

支持多种scheme，例如http，https，ftp，file等。必须提供未编码的URL。 

###七牛云存储账号信息

若上传类型为Qiniu，则需要配置[七牛云存储](https://portal.qiniu.com/)账号相关信息。

`qiniu.bucket`填写被迁移的空间名；`qiniu.domain`为七牛域名，需要包含协议类型（如http://）；若空间开启了防盗链，需要在`qiniu.referer`中指定访问来源域名，同样需要包含协议类型（如http://）；如果是私有空间，将`qiniu.isprivate`设置为`True`，否则设置为`False`。

```
[Qiniu]
qiniu.bucket = my_bucket_name
qiniu.AccessKey = _17terLxP-ZK7tma9jXgm7MuEOk72yP9OZBIP35G
qiniu.SecretKey = PFw6JivhTAdNKRojaguUkC6tlFHAI9SBrjVYdfya
qiniu.domain = http://abcde.com1.fg.glb.clouddn.com/
qiniu.referer = 
qiniu.isprivate = False
```

###阿里云oss账号信息

若上传类型为Oss，则需要配置[阿里云oss](https://ak-console.aliyun.com/#/accesskey/)账号相关信息。

`oss.bucket`填写被迁移的空间名；`oss.endpoint`为阿里云oss的endpoint，可以指定协议类型（http://或者https://，不指定则默认为http://）；如果是cname的域名，请将 oss.iscname设置为True，默认为False；

```
[Oss]
oss.bucket = my_bucket_name
oss.accesskey = _17terLxP-ZK7tma9jXgm7MuEOk72yP9OZBIP35G
oss.secretkey = PFw6JivhTAdNKRojaguUkC6tlFHAI9SBrjVYdfya
oss.endpoint = oss-cn-shanghai.aliyuncs.com 
oss.iscname = False
```

###万象优图账号信息

从[万象优图图片空间](http://console.qcloud.com/image/bucket)中查看项目ID和空间名称，分别填写到`appinfo.appid`和`appinfo.bucket`；从[万象优图项目设置](http://console.qcloud.com/image/project)中查看Secret ID和Secret Key分别填写到`appinfo.secretID`和`appinfo.secretKey`。

```
[AppInfo]
appinfo.appid = 10000000
appinfo.secretID = AKIDgRmc3zz5pKK8MdfLV7ZOM6KkBNifozMG
appinfo.secretKey = 2wUid99BjpOyL7VVDSEhPmW8xcUvuHEv
appinfo.bucket = my_bucket
```

###上传设置

`Concurrency`控制同时运行的上传进程数目，请根据上行带宽和机器配置适当调整该数值，如果带宽小而此值大会经常出现网络连接相关的错误。必须提供一个大于0的整数。

`db.commit.interval`控制上传结果写回日志的时间间隔，单位为秒，应该提供一个合法的正整数或浮点数或正无穷（inf）。如果进程意外结束，未写回的日志将丢失。此值设置过小将严重影响性能，一般情况下使用默认值即可。

`jobqueue.capacity`、`jobqueue.reload.threshold`、`buffer.size`是控制任务队列和内存缓冲区的选项，一般情况下使用默认值即可。

```
[ToolConfig]
concurrency = 10
jobqueue.capacity = 2000
jobqueue.reload.threshold = 0.4
buffer.size = 100000
db.commit.interval = 3
```

`fileid.ignore.if`使工具在提交任务时忽略file id符合指定条件的任务。

`fileid.ignore.unless`使工具在提交任务时忽略file id不符合指定条件的任务。

`error.ignore.if`使工具在重试出错任务时忽略错误日志符合指定条件的任务。

以上三个选项若启用则应提供一个正则表达式，否则留空，语法参考[Python re Module Reference](https://docs.python.org/2/library/re.html)。如果同时提供了`fileid.ignore.if`和`fileid.ignore.unless`，并且某个file id同时符合两个正则表达式，那么它会被忽略。

例如忽略OS X操作系统下的.DS_Store文件，不重试错误码为-1886的任务：

```
[Advanced]
fileid.ignore.if = .*.DS_Store
fileid.ignore.unless = 
error.ignore.if = .*code: -1886.*
```


##致谢

本工具包含了以下开源项目

1. [Requests: HTTP for Humans](http://www.python-requests.org/en/latest/)

2. [Cloud Image Python 2 SDK](https://github.com/tencentyun/python-sdk)

3. [Qiniu Resource Storage SDK for Python](https://github.com/qiniu/python-sdk)

4. [Aliyun OSS SDK for Python](https://github.com/aliyun/aliyun-oss-python-sdk)

##许可
基于MIT开源协议发布，详见[LICENSE](LICENSE)。
