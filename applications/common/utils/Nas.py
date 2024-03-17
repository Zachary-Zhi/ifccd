import os
from pathlib import Path
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure
from applications.option import options
from applications.option.options import task_executing_dic

# def connect():
#     '''
#     建立smb服务连接
#     :param user_name:
#     :param passwd:
#     :param ip:
#     :param port: 445或者139
#     :return:
#     '''
#
#     samba = None
#     status = False
#     try:
#         samba = SMBConnection(options.nas_access_key, options.nas_secret_key, '', '', use_ntlm_v2=True)
#         samba.connect(options.nas_ip, options.nas_ip)
#         status = samba.auth_result
#
#     except:
#         samba.close()
#     return samba, status
def all_shares_name(samba):
    '''
    列出smb服务器下的所有共享目录
    :param samba:
    :return:
    '''
    share_names = list()
    sharelist = samba.listShares()
    for s in sharelist:
        share_names.append(s.name)
    return share_names
def all_file_names_in_dir(samba, service_name, dir_name):
    '''
    列出文件夹内所有文件名
    :param service_name: 服务名（smb中的文件夹名，一级目录）
    :param dir_name: 二级目录及以下的文件目录
    :return:
    '''
    f_names = list()
    for e in samba.listPath(service_name, dir_name):
        if e.filename[0] != '.':   # （会返回一些.的文件，需要过滤）
            f_names.append(e.filename)
    return f_names
def get_last_updatetime(samba, service_name, file_path):
    '''
    返回samba server上的文件更新时间（时间戳），如果出现OperationFailure说明无此文件，返回0
    :param samba:
    :param service_name:
    :param file_path:
    :return:
    '''
    try:
        sharedfile_obj = samba.getAttributes(service_name, file_path)
        return sharedfile_obj.last_write_time
    except OperationFailure:
        return 0



def download(samba, f_names, service_name, smb_dir, local_dir):
    '''
    下载文件
    :param samba:
    :param f_names:文件名
    :param service_name:服务名（smb中的文件夹名）
    :param smb_dir: smb文件夹
    :param local_dir: 本地文件夹
    :return:
    '''
    assert isinstance(f_names, list)
    for f_name in f_names:
        f = open(os.path.join(local_dir, f_name), 'wb')
        print(os.path.join(local_dir, f_name))
        print(os.path.join(smb_dir, f_name))
        samba.retrieveFile(service_name, os.path.join(smb_dir, f_name), f)

        f.close()



def nas_download(path, samba):
    '''
    下载文件
    :param samba:
    :param path:路径
    :param local_dir: 本地文件夹
    :return:
    '''

    p = Path(path)
    print(p.parts[-1])
    print(p.parts[2])
    lparts = list(p.parts)
    del lparts[0]  # 删除file
    del lparts[0]  # 删除host
    del lparts[0]  # 删除share_name（第一级文件夹名）
    del lparts[-1]  # 删除文件名
    print(lparts)  # 此时是中间路径
    print("//".join(lparts))  # 合并成字符串

    f_names = [p.parts[-1]]  # 文件名
    service_name = p.parts[2]  # 服务名（smb中的第一级文件夹名）
    smb_dir = "//".join(lparts)  # smb文件夹
    print(service_name)

    local_download_path = options.nas_download_path + f_names[0]
    print(local_download_path)

    assert isinstance(f_names, list)
    for f_name in f_names:
        with open(os.path.join(options.nas_download_path, f_name), 'wb') as f:

        # f = open(os.path.join(options.nas_download_path, f_name), 'wb')
            print(os.path.join(options.nas_download_path, f_name))
            print(os.path.join(os.path.join(smb_dir, f_name)))

            samba.retrieveFile(service_name, os.path.join(smb_dir, f_name), f)  # 第二个参数path包含文件全路径
            f.close()

    return local_download_path



def createDir(samba, service_name, path):
    """
    创建文件夹
    :param samba:
    :param service_name:
    :param path:
    :return:
    """
    try:
        samba.createDirectory(service_name, path)
    except OperationFailure:
        pass
def nas_upload(path, photo_output_path, samba, task_id):
    '''
    上传文件
    :param samba:
    :param service_name:服务名（smb中的文件夹名）
    :param smb_dir: smb文件夹
    :param local_dir: 本地文件列表所在目录
    :param f_names: 本地文件列表
    :return:
    '''
    p = Path(path)#本地打开
    print(p.parts[-1])
    f_names = [p.parts[-1]]  # 文件名

    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        upload_path = options.nas_upload_path + f_names[0]
        photo_output_path = options.nas_upload_path
    else:
        upload_path = photo_output_path + f_names[0]


    to_p = Path(photo_output_path)  # 目标打开
    to_lparts = list(to_p.parts)
    to_p_list = photo_output_path.split("\\")
    print(to_p_list)
    service_name = to_p_list[3]
    del to_p_list[0]
    del to_p_list[0]
    del to_p_list[0]
    del to_p_list[0]
    del to_p_list[-1]
    smb_dir = "//".join(to_p_list)  # smb文件夹
    # print(to_p_list)
    # print("1111111111111")
    # print(photo_output_path)
    # print(to_lparts)
    # print(to_lparts[0])
    # # del to_lparts[0]  # 删除file
    # del to_lparts[0]  # 删除host
    # del to_lparts[0]  # 删除share_name（第一级文件夹名）
    # print(to_lparts)  # 此时是中间路径
    # print("//".join(to_lparts))  # 合并成字符串
    #
    # service_name = to_p.parts[2]  # 服务名（smb中的第一级文件夹名）
    # smb_dir = "//".join(to_lparts)  # smb文件夹
    print("service_name:")
    print(service_name)
    print(222)
    print(smb_dir)


    print(111)
    print(upload_path)
    print(111)
    assert isinstance(f_names, list)
    for f_name in f_names:
        f = open(path, 'rb')
        print(os.path.join(smb_dir, f_name))
        samba.storeFile(service_name, os.path.join(smb_dir, f_name), f)  # 第二个参数path包含文件全路径
        f.close()

    task_executing_dic.get(task_id)["result"] = upload_path

def connect(user_name, passwd, ip, port):
    '''
    建立smb服务连接
    :param user_name:
    :param passwd:
    :param ip:
    :param port: 445或者139
    :return:
    '''
    samba = None
    status = False
    try:
        samba = SMBConnection(user_name, passwd, '', '', use_ntlm_v2=True)
        samba.connect(ip, port)
        status = samba.auth_result

    except:
        samba.close()
    return samba, status


# def connect():
#     '''
#     建立smb服务连接
#     :param user_name:
#     :param passwd:
#     :param ip:
#     :param port: 445或者139
#     :return:
#     '''
#
#     samba = None
#     status = False
#     try:
#         samba = SMBConnection(options.nas_access_key, options.nas_secret_key, '', '', use_ntlm_v2=True)
#         samba.connect(options.nas_ip, options.nas_ip)
#         status = samba.auth_result
#
#     except:
#         samba.close()
#     return samba, status

if __name__ == '__main__':

    samba = None
    status = False

    samba = SMBConnection(options.nas_access_key, options.nas_secret_key, '', '', use_ntlm_v2=True)
    samba.connect(options.nas_ip, 445)
    status = samba.auth_result
    #samba, status = connect('NasUser', 'nascode', '192.168.128.24', 445)
    if status:
        print('smb服务器连接成功！')
    else:
        print('smb服务器连接失败！')
    share_names = all_shares_name(samba)
    print("share_names:", share_names)
    share_name = "test0"  # 第一级文件夹名
    dst_name = ''
    f_names = all_file_names_in_dir(samba, share_name, dst_name)
    print("share_name: {} -dir_name: {} include f_names:".format(share_name, dst_name), f_names)

    # file_path = '/程序/auto_start.bat'
    # timestamp = get_last_updatetime(samba, share_name, file_path)
    # print(datetime.datetime.fromtimestamp(timestamp))

    # smb_dir = '/数据/历史气象数据'
    # f_names =['README.txt','MERRA-2全球再分析数据集.doc','Delivery_05-29-2009_05-28-2019_hourly.zip']
    # local_dir = ''
    # download(samba, f_names, share_name, smb_dir, local_dir)






    # smb_dir = '/elsesecond'  # 具体到最终文件夹，拼在第一级文件夹后面使用
    # f_names = ['testpicture.jpg', 'testtxt.txt']
    # local_dir = 'G:\\Graduate\\Cowhorse\\MIFCCD\\test0'
    # download(samba, f_names, share_name, smb_dir, local_dir)
    #
    #
    # smb_dir = '/secondtime'  # 该目录需提前创建好
    # local_dir = 'G:\\Graduate\\Cowhorse\\MIFCCD\\test0'
    # f_names = ['testpicture.jpg', 'testtxt.txt']
    # upload(samba, share_name, smb_dir, local_dir, f_names)

    samba.close()
