from minio import Minio
from pathlib import Path
from applications.option import options
from applications.option.options import task_executing_dic
def minio_init():
    minioClient = Minio(options.minio_ip + ":" + options.minio_port,
                        access_key=options.minio_access_key,
                        secret_key=options.minio_secret_key,
                        secure=False)
    return minioClient

def minio_upload(path, photo_output_path, minioClient, task_id):
    file_fullname = from_path_get_filefullname(path)
    upload_path = ""
    if len(photo_output_path) == 0 or photo_output_path == "":
        upload_path = options.minio_upload_path + file_fullname
    else:
        upload_path = photo_output_path + file_fullname

    print(minioClient.fput_object(from_path_get_bucketname(upload_path), from_path_get_inbucketpath(upload_path), path))
    task_executing_dic.get(task_id)["result"] = upload_path


def minio_download(path,minioClient):
    bucketname = from_path_get_bucketname(path)
    inbucketpath = from_path_get_inbucketpath(path)
    local_download_path = options.minio_download_path + from_path_get_filefullname(path)
    print("local_download_path: ", local_download_path)
    print(minioClient.fget_object(bucketname, inbucketpath, local_download_path))
    return local_download_path


def from_path_get_filename(path):
    '''
    从文件路径中获取文件名
    :param path: 文件路径
    :return:
    '''
    p = Path(path)
    file_fullname = p.parts[-1]
    result = file_fullname.split('.')
    return result[0]

def from_path_get_filename_suffix(path):
    '''
    从文件路径中获取文件的后缀（类型）
    :param path: 文件路径
    :return:
    '''
    p = Path(path)
    file_fullname = p.parts[-1]
    result = file_fullname.split('.')
    return result[1]


def from_path_get_bucketname(path):
    '''
    从文件路径中获取文件的bucketname
    :param path:
    :return:
    '''
    p = Path(path)
    return p.parts[2]

def from_path_get_inbucketpath(path):
    p = Path(path)
    lparts = list(p.parts)
    del lparts[0] # 删除file
    del lparts[0] # 删除host
    del lparts[0] # 删除bucketname
    return "/".join(lparts)

def from_path_get_filefullname(path):
    p = Path(path)
    return p.parts[-1]

def from_path_del_filefullname(path):
    p = Path(path)
    lparts = list(p.parts)
    del lparts[-1]  # 删除文件名
    return "//".join(lparts)
    #return p_list[-1]