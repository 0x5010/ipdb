# ipdb
  ip裤子来源 https://git.oschina.net/lionsoul/ip2region (谢谢原作者的辛苦整理)
  脚本进了修改和添加功能
  是从阿里的ip库爬取, 准确率99%以上
  加入了内存缓存和是不是移3g网的功能(移动3g的裤子比较老了不一定准)
  大家可以提供些运营商ip段的裤来一起完善
  
### 运行效果如图
>>python ./test_searcher.py

```python
initializing binary...
ipdbn>> 114.114.114.114
[Return]: 中国|华东|江苏省|南京市|0 in 0.031006 millseconds
[Return]: no_3g in 0.021006 millseconds
ipdbn>> 112.5.74.74
[Return]: 中国|华东|福建省|漳州市|移动 in 0.027832 millseconds
[Return]: no_3g in 0.017832 millseconds
ipdbn>> 
```

test_searcher就是使用方式

cache=True 的时候使内存缓存速度比较快占较大的内存(binary算法)
cache=False 时候只缓存btree索引速度也不太慢0.1x毫秒级别(btree算法)

