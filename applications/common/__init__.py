# from applications.common.utils.minio_photo import minio_init
# from applications.common.utils.Nas import connect
# from applications.option import options
# from smb.SMBConnection import SMBConnection
# import os

# nas_username = "ubuntu1"
# if os.getenv("IFCCD_SMB_USERNAME") is not None:
#     nas_username = os.getenv("IFCCD_SMB_USERNAME")

# nas_password = "1"
# if os.getenv("IFCCD_SMB_PASSWD") is not None:
#     nas_password = os.getenv("IFCCD_SMB_PASSWD")

# nas_ip = "192.168.8.251"
# if os.getenv("IFCCD_SMB_IP") is not None:
#     nas_ip = os.getenv("IFCCD_SMB_IP")
# minioClient = minio_init()

# samba = None
# status = False
# try:
#     samba = SMBConnection(nas_username, nas_password, '', '', use_ntlm_v2=True)
#     samba.connect(nas_ip, 445)
#     status = samba.auth_result

# except Exception as e:
#     print(e)
#     print("smb服务器连接失败")

# if status:
#     print('smb服务器连接成功！')
# else:
#     print('smb服务器连接失败！')
