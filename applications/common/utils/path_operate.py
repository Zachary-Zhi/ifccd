from pathlib import Path
import os
from applications.option.options import docker_map_url_prefix
def from_path_get_filename(path):
    '''
    从文件路径中获取文件名
    :param path: 文件路径  http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:  img_001
    '''
    p = Path(winPath2LinuxPath(path))
    file_fullname = p.parts[-1]
    result = file_fullname.split('.')
    return result[0]

def from_path_get_filename_suffix(path):
    '''
    从文件路径中获取文件的后缀（类型）
    :param path: 文件路径 http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:    jpg
    '''
    p = Path(winPath2LinuxPath(path))
    file_fullname = p.parts[-1]
    result = file_fullname.split('.')
    return result[1]


def from_path_get_bucketname(path):
    '''
    从文件路径中获取文件的bucketname
    :param path: http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:    photo
    '''
    p = Path(winPath2LinuxPath(path))
    return p.parts[2]

def from_path_get_inbucketpath(path):
    '''

    :param path: http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:  upload//test//img_001.jpg
    '''
    p = Path(winPath2LinuxPath(path))
    lparts = list(p.parts)
    del lparts[0] # 删除file
    del lparts[0] # 删除host
    del lparts[0] # 删除bucketname
    return "/".join(lparts)

def from_path_get_filefullname(path):
    '''

    :param path:  http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:  img_001.jpg
    '''
    p = Path(winPath2LinuxPath(path))
    return p.parts[-1]

def url_map(path):
    '''

    :param path: http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:  upload//test//img_001.jpg
    '''
    p = Path(winPath2LinuxPath(path))
    lparts = list(p.parts)
    del lparts[0] # 删除file
    del lparts[0] # 删除host
    del lparts[0] # 删除bucketname
    return "/".join(lparts)
def url_map_with_slash(path):
    '''

    :param path: http://127.0.0.1:8000/photo/upload//test//img_001.jpg
    :return:  upload//test//img_001.jpg
    '''
    p = Path(winPath2LinuxPath(path))
    lparts = list(p.parts)
    del lparts[0] # 删除file
    del lparts[0] # 删除host
    del lparts[0] # 删除bucketname
    return "/".join(lparts) + "/"
def url_no_filePath(path):
    p = Path(winPath2LinuxPath(path))
    lparts = list(p.parts)
    del lparts[-1]
    return "/".join(lparts) + "/"
def neturl_to_localurl(path):
    '''

        :param path: http://127.0.0.1:8000/photo/upload//test//img_001.jpg
        :return:  upload//test//img_001.jpg
        '''
    p = Path(winPath2LinuxPath(path))
    lparts = list(p.parts)
    del lparts[0]  # 删除file
    del lparts[0]  # 删除host
    del lparts[0]  # 删除bucketname
    resPath = "/".join(lparts)
    resPath = docker_map_url_prefix + resPath
    return resPath

def mapurl_to_neturl(path):
    '''

        :param path: /mnt/linux_share/ifccd/upload/img_001_denoise_20230516110649.png
        :return:  ifccd/upload/img_001_denoise_20230516110649.png
    '''
    p = Path(winPath2LinuxPath(path))
    lparts = list(p.parts)
    del lparts[0]  # 删除""
    del lparts[0]  # 删除"mnt"
    del lparts[0] # 删除“linux_share”
    return "/".join(lparts)


def winPath2LinuxPath(path):
    tmp_list = path.split('\\')
    if len(tmp_list) > 1:
        path = '/'.join(path.split('\\'))
    return path

def linuxPath2WinPath(path):
    result = ""

    for i in range(0, len(path)):
        if path[i] == '/':
            result = result + "\\"
        else:
            result = result + path[i]
    return result