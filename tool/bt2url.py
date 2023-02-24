#! /usr/local/bin/python 
# python通过BT种子生成磁力链接
import bencode 
import sys 
import hashlib 
import base64 

# 获取参数
torrentName = sys.argv[1] 
# 读取种子文件
torrent = open(torrentName, 'rb').read() 
# 计算meta数据
metadata = bencode.bdecode(torrent) 
hash_contents = bencode.bencode(metadata['info'])
digest = hashlib.sha1(hash_contents).digest()
b32hash = base64.b32encode(digest) 
# 打印
print('magnet:?xt=urn:btih:%s' % b32hash)
