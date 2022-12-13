# SUES_AutoHealthStatement
a simple program for auto upload health statement for Shanghai University Of Engineering Science(SUES).

上海工程技术大学自动填报健康填报的简单脚本

这是一个小程序用于上海工程技术大学（SUES）的自动健康填报.

## 待完善

## 写在前面
本程序的灵感来源于@[Leng-bingo](https://github.com/Leng-bingo)的[SUES-autotemp](https://github.com/Leng-bingo/SUES-autotemp)，感谢学长（？）留下来的程序，虽然这个程序现在基本不能用了，但里面的验证码识别还是能用的，也令我这个小白大受启发.

本人不过是在前人留下的基础上的进行改进罢了（话说你这连底层架构都跟人家的不一样了吧）...

P.S.话说我现在搞这个是不是有点属于是四九年入国军啊，感觉马上就不再需要健康填报了.

## 实现原理
主要原理是用[playwright](https://github.com/microsoft/playwright)模拟浏览器进行登录与填报操作.

（为什么不用requests或xhttp来纯后台实现呢，其实主要原因是我不会，还有个原因是前人留下来的登录程序好像不能用了，但我们又搞不出新的登录程序，所以干脆一气之下改模拟浏览器了，要是以后还需要健康填报的话，我可能会再研究研究怎么纯后台实现吧..）

其中关于识别验证码的原理，简单的数字验证码是前人留下来的代码，原理是将验证码上的数字切成9x16的方块，将其二值化为144位长的特征码，然后就与实际收到的验证码比对就行了，虽然有可能识别错，但这概率其实很小，我在测试的途中没遇到过识别失败的场景.

滑动验证码就比较麻烦了，最开始是我用pillow加nummpy自己手写了个识别程序，但那个识别程序的成功率有点低，可能才只有90%多. 所以我直接上opencv了. 但说实话，opencv的识别率也不是百分百，大概98%以上？

其他的应该都很简单了吧，毕竟我都直接模拟浏览器了，点个鼠标[谁](https://github.com/Dedicatu1979)不会啊.

对，[我](https://github.com/Dedicatu1979)不会，其实我是为了搞这个程序当场现学的playwright，很多操作都不会，所以你们看源代码时就会发现个很奇怪的东西，那就是我都用playwright了，可我在里面还是用了bs4，因为我不知道该怎么用playwright保存元素...

## 使用方法说明
把源代码下载下来后放到python3.7及以上的版本的解释器中运行本程序（懒得打包成exe了，其实这整个程序都可以说是赶工出来的，懒得改了）.P.S.：请确保您的解释器有[requirements.txt](./requirements.txt)内的第三方模块（你直接```pip install -r requirements.txt```也行）

运行的话，就把它扔到服务器中，或者一台24小时工作的电脑里就行了，它会每天自动打卡，就这样，很简单...但是需要写些设置.

本程序的设置统统在[config.json](./config.json)里进行设置. 

## config文件配置说明
config里有两个主键值对，主键值对中还有些小键值对，我们先说"system_configs"：
```
"system_configs":
{
    "url": "https://workflow.sues.edu.cn/default/work/shgcd/jkxxcj/jkxxcj.jsp",
    "time_of_clock_in": "8:30",
    "SendKey": ""
}
```
|键key      |值value的说明|
|---------- |---------|
|url        |这个就是学校打卡的网址，默认值不需要修改|
|time_of_clock_in |这个是每天打卡的时间，默认值为"8:30"，即每天早上8点30分打一次卡，可以修改成其他时间，但格式必须是24小时制的"xx:yy"的形式，注意":"是英文冒号|
|SendKey    | 这个是[Server酱](https://sct.ftqq.com)的推送调用key，详细可以点[Server酱](https://sct.ftqq.com)了解详情，默认值为空，如果值为空或不存在本键值对的话，程序将不会每日向您微信推送打卡成功情况|

Server酱的推送内容格式为：
```
本日打卡人数共x人，y人打卡成功，z人打卡失败，
{'mumber':[],'cause':[]}
```
其中如果所有人都打卡成功的话，则第二行内都是空的，如果有人打卡失败的话，'member'中会指出打卡失败的人是哪位，'cause'中会指出失败的原因是什么.
### 可能出现的异常
本人就定义了两种可能出现的异常，应该还有个超时异常但我懒得加了，并且这个出现的概率不高.
|异常内容|异常说明|
|------|-----|
|Url or Time Error.| 程序在登录页面卡住了，或者登录时的验证码验证失败，或者打卡页面的网址变动了|
|Captcha Error.| 程序在提交时，滑动验证码验证失败|


## 最后
感谢@[yuban10703](https://github.com/yuban10703)在我写这个小程序时的协助与支持.
