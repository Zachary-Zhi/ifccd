import datetime
from pathlib import Path

from smb.SMBConnection import SMBConnection
# import smb.base
# import urllib
# import paramiko

import os
samba = None
status = False
# samba = SMBConnection("root", "2746740439wei", '', '', use_ntlm_v2=True)
samba = SMBConnection("root", "2746740439wei", '', '', use_ntlm_v2=True)
samba.connect("192.168.153.140", 445)
status = samba.auth_result
print(status)
#samba, status = connect('NasUser', 'nascode', '192.168.128.24', 445)
if status:
    print('smb服务器连接成功！')
else:
    print('smb服务器连接失败！')

# samba.re
# input_names = json_data.get("import")

sharelist = samba.listShares()
for s in sharelist:
    print(s.name)
    # self.share_names.append(s.name)
# print("==============")
for e in samba.listPath("linux_share", ""):
            if e.filename[0] != '.':  # （会返回一些.的文件，需要过滤）
                print(e.filename)
            # print(e)
                # if os.path.exists(e):
                #     print("yes")
print("==============")

print("==============")
# photo_url = "//192.168.153.140/linux_share/img_001.png"
photo_url = "/mnt/linux_share/img_001.png"
# photo_url = "D:\\data\\denoising dataset\\dataset\\Urban100\\img_001.png"
# photo_url = "//192.168.153.134/nas/photo/ifccd/photo/img_001.png"
if os.path.exists(photo_url):
    print("文件存在")
else:
    print("文件不存在")
print("==============")

dir_url = "/mnt/linux_share/ifccd/upload/123/"
folder = os.path.exists(dir_url)

if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
    os.makedirs(dir_url)