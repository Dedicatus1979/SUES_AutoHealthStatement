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
主要原理是用[playwright](github.com/microsoft/playwright)模拟浏览器进行登录与填报操作.

（为什么不用requests或xhttp来纯后台实现呢，其实主要原因是我不会，还有个原因是前人留下来的登录程序好像不能用了，但我们又搞不出新的登录程序，所以干脆一气之下改模拟浏览器了，要是以后还需要健康填报的话，我可能会再研究研究怎么纯后台实现吧..）

其中关于识别验证码的原理，简单的数字验证码是前人留下来的代码，原理是将验证码上的数字切成9x16的方块，将其二值化为144位长的特征码，然后就与实际收到的验证码比对就行了，虽然有可能识别错，但这概率其实很小，我在测试的途中没遇到过识别失败的场景.

滑动验证码就比较麻烦了，最开始是我用pillow加nummpy自己手写了个识别程序，但那个识别程序的成功率有点低，可能才只有90%多. 所以我直接上opencv了. 但说实话，opencv的识别率也不是百分百，大概98%以上？

其他的应该都很简单了吧，毕竟我都直接模拟浏览器了，点个鼠标[谁](github.com/Dedicatu1979)不会啊.

对，[我](github.com/Dedicatu1979)不会，其实我是为了搞这个程序当场现学的playwright，很多操作都不会，所以你们看源代码时就会发现个很奇怪的东西，那就是我都用playwright了，可我在里面还是用了bs4，因为我不知道该怎么用playwright保存元素...

## 使用方法说明
把源代码下载下来后放到python3.7及以上的版本的解释器中运行本程序（懒得打包成exe了）.P.S.：请确保您的解释器有[requirements.txt](./requirements.txt)内的第三方模块（你直接```pip install -r requirements.txt```也行）

## 最后
感谢@[yuban10703](github.com/yuban10703)在我写这个小程序时的协助与支持.
