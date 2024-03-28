import datetime
import threading
import time
import os
import cv2
from applications.common.utils.minio_photo import from_path_get_filefullname,from_path_del_filefullname
from applications.common.utils.Nas import nas_upload

from flask import current_app
from applications.option import options
from applications.reposity.task_reposity import update_task_status_by_task_id, update_task_endtime_by_task_id, \
    update_task_resulturl_by_task_id, select_task_by_task_id, update_task_logs_by_task_id, update_task_completeRate_by_task_id
from applications.option.options import task_executing_dic, docker_map_url_prefix, net_url_prefix, docker_map_url_enhance_prefix, net_url_enhance_prefix
from applications.common.utils.sen_message import send_message
from applications.common.utils.path_operate import url_map, mapurl_to_neturl, neturl_to_localurl, linuxPath2WinPath, from_path_get_filename
from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
from applications.algorithms.check_same_image import checkSameImage
from applications.algorithms.HomographyError import HomographyError
from datetime import timezone
from datetime import timedelta

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai'
)

exitFlag = 0
queueLock = threading.Lock()

#只处理短任务线程
class Enhance_Task_Handle_Thread (threading.Thread):
    def __init__(self, threadID, name, enhance_task_q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.enhance_task_q = enhance_task_q

    def run(self):
        print ("开启线程：" + self.name)
        process_enhance_task(self.name, self.enhance_task_q)
        print ("退出线程：" + self.name)

class Both_Task_Handle_Thread (threading.Thread):
    def __init__(self, threadID, name, ifccd_task_q, enhance_task_q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ifccd_task_q = ifccd_task_q
        self.enhance_task_q = enhance_task_q

    def run(self):
        print ("开启线程：" + self.name)
        process_all_task(self.name, self.ifccd_task_q, self.enhance_task_q)
        print ("退出线程：" + self.name)


#短任务线程执行函数
def process_enhance_task(threadName, enhance_task_q):
    while not exitFlag:
        queueLock.acquire()
        #表示有任务要处理
        if enhance_task_q.get_nums() > 0:

            tmp_task = enhance_task_q.get_que().popleft()
            queueLock.release()
            #任务状态改变
            update_task_status_by_task_id(tmp_task.task_id, 2)

            task_id = str(tmp_task.task_id)
            print('task_id: ', task_id)
            #发送通知
            send_message(task_id, tmp_task.task_params_json.get("user"), "begin to execute", "", "")
            #处理task的相关信息
            task_executing_dic[task_id]["taskStage"] = "prepare to execute"
            #请求体json内容
            tmp_task_dic = tmp_task.task_params_json

            m_operator = tmp_task_dic.get("alg").get("algType")
            alg_dic = tmp_task_dic.get("alg")

            json_photo_download_path = tmp_task_dic.get("import")

            minio_photo_upload_path = tmp_task_dic.get("output")
            if minio_photo_upload_path == None or minio_photo_upload_path == "":
                local_upload_path = ""
            else:
                #设置url
                nas_output_url = url_map(minio_photo_upload_path)
                #print("nas_output_url: " + nas_output_url)
                #本地文件夹路径
                local_upload_path = docker_map_url_enhance_prefix + nas_output_url + "/"
                #print(local_upload_path)

            nas_import_url = url_map(json_photo_download_path)

            print("nas_import_url: " + nas_import_url)

            local_download_path = docker_map_url_enhance_prefix + nas_import_url

            import datetime
            log_jihe = []
            log_dic = {'beginTime': '', 'endTime': '', 'user': '', 'import': '', 'output': '', 'taskType': '',
                       'taskId': '', 'taskstage': '', 'taskClassesType': ""}
            log_dic_current = log_dic.copy()
            log_dic_current['beginTime'] = str(datetime.datetime.now())
            log_dic_current['user'] = tmp_task.task_params_json.get("user")
            log_dic_current['import'] = tmp_task_dic.get("import")
            log_dic_current['output'] = tmp_task_dic.get("output")
            log_dic_current['taskId'] = task_id

            tasktype = select_task_by_task_id(task_id)['task_type']
            #长任务是1 短任务是0
            if (int(tasktype) == 1):
                log_dic_current['taskType'] = 'LongTasks'
            else:
                log_dic_current['taskType'] = 'ShortTasks'
            log_dic_current['taskstage'] = "prepare to execute"


            if "adjust" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "adjust"
                log_dic_adjust=log_dic_current.copy()
                log_dic_adjust['taskClassesType']='adjust'
                log_dic_adjust['taskstage'] = "image adjust begin"

                try:
                    processErrorFlag = False
                    #
                    out = process_img_adjust_task(alg_dic, local_download_path, local_upload_path, task_id)
                except Exception as e:
                    print(e)
                    print("process img adjust error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "adjust failed", "", "adjust failed")
                    update_task_status_by_task_id(task_id, 5)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue

                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "adjust success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)

                log_dic_adjust['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_adjust['taskstage'] = "image adjust success"
                log_dic_adjust['output']=linuxPath2WinPath(out)
                log_jihe.append(log_dic_adjust)
                update_task_logs_by_task_id(task_id, log_jihe)

            elif "denoise" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "denoise"
                log_dic_denoise=log_dic_current.copy()
                log_dic_denoise['taskClassesType']='denoise'
                log_dic_denoise['taskstage'] = "image denoise begin"

                try:
                    processErrorFlag = False
                    out=process_img_denoise_task(alg_dic, local_download_path, local_upload_path, task_id)
                except Exception as e:
                    print(e)
                    print("process img denoise error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "denoise failed", "", "denoise failed")
                    update_task_status_by_task_id(task_id, 5)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue



                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "denoise success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)

                log_dic_denoise['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_denoise['taskstage'] = "image denoise success"
                log_dic_denoise['output'] = linuxPath2WinPath(out)
                log_jihe.append(log_dic_denoise)
                update_task_logs_by_task_id(task_id, log_jihe)

            elif "enhance" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "enhance"
                log_dic_enhance = log_dic_current.copy()
                log_dic_enhance['taskClassesType'] = 'enhance'
                log_dic_enhance['taskstage'] = "image enhance begin"

                try:
                    processErrorFlag = False
                    out=process_img_enhance_task(alg_dic, local_download_path, local_upload_path, task_id)
                except Exception as e:
                    print(e)
                    print("process img enhance error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "enhance failed", "", "enhance failed")
                    update_task_status_by_task_id(task_id, 5)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue

                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "enhance success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)

                log_dic_enhance['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_enhance['taskstage'] = "image enhance success"
                log_dic_enhance['output'] = linuxPath2WinPath(out)
                log_jihe.append(log_dic_enhance)
                update_task_logs_by_task_id(task_id, log_jihe)

            elif "revise" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "revise"
                log_dic_revise=log_dic_current.copy()
                log_dic_revise['taskClassesType']='revise'
                log_dic_revise['taskstage'] = "image revise begin"

                try:
                    processErrorFlag = False
                    out = process_img_revise_task(alg_dic, local_download_path, local_upload_path, task_id)
                except Exception as e:
                    print(e)
                    print("process img revise error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "revise failed", "", "revise failed")
                    update_task_status_by_task_id(task_id, 5)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue


                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "revise success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)

                log_dic_revise['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_revise['taskstage'] ="image revise success"
                log_dic_revise['output'] = linuxPath2WinPath(out)
                log_jihe.append(log_dic_revise)
                update_task_logs_by_task_id(task_id, log_jihe)
            else:
                print("unknown action")
            print("%s processing %s %s" % (threadName, tmp_task.task_id, tmp_task.task_params_json))
            #数据库操作
            #更新任务输出图像地址
            update_task_resulturl_by_task_id(task_id, task_executing_dic[task_id]["result"])
            #更新状态
            update_task_status_by_task_id(task_id, 1)
            #更新结束时间
            update_task_endtime_by_task_id(task_id)
            #字典删除任务信息
            task_executing_dic.pop(task_id)

        else:
            queueLock.release()
        time.sleep(1)


def process_all_task(threadName, ifccd_task_q, enhance_task_q):
    while not exitFlag:
        queueLock.acquire()
        if ifccd_task_q.get_nums() > 0:
            tmp_task = ifccd_task_q.get_que().popleft()
            queueLock.release()

            update_task_status_by_task_id(tmp_task.task_id, 2)

            task_id = str(tmp_task.task_id)

            send_message(task_id, tmp_task.task_params_json.get("user"),
                                                               "begin to execute", "", "")
            task_executing_dic[task_id]["taskStage"] = "prepare to execute"

            # 获取当前任务的dic
            tmp_task_dic = tmp_task.task_params_json
            tmp_taskClassesType = tmp_task.taskClassesType

            minio_photo_download_paths = tmp_task_dic.get("import")
            minio_photo_download_path1 = minio_photo_download_paths[0]
            minio_photo_download_path2 = minio_photo_download_paths[1]


            error_flag = False

            import datetime
            log_jihe = []
            log_dic = {'beginTime': '', 'endTime': '', 'user': '', 'import': '', 'output': '', 'taskType': '',
                       'taskId': '', 'taskstage': '', 'taskClassesType': ""}
            log_dic_current = log_dic.copy()
            log_dic_current['beginTime'] = str(datetime.datetime.now())
            log_dic_current['user'] = tmp_task.task_params_json.get("user")
            log_dic_current['import'] = tmp_task_dic.get("import")
            log_dic_current['taskId'] = task_id

            tasktype = select_task_by_task_id(task_id)['task_type']
            
            if (int(tasktype) == 1):
                log_dic_current['taskType'] = 'LongTasks'
            else:
                log_dic_current['taskType'] = 'ShortTasks'
            log_dic_current['taskstage'] = "prepare to execute"

            nas_import_url1 = url_map(minio_photo_download_path1)
            nas_import_url2 = url_map(minio_photo_download_path2)

            local_download_path1 = docker_map_url_prefix + nas_import_url1
            local_download_path2 = docker_map_url_prefix + nas_import_url2

            if tmp_taskClassesType == "fusion":
                ret_output_name = task_id + "_fusion_resultwithGeo.tif"
            elif tmp_taskClassesType == "detect":
                ret_output_name = task_id + "_detect_resultwithGeo.tif"
            else:
                ret_output_name = "resultwithGeo.tif"

            photo_output_path = tmp_task_dic.get("output")
            if photo_output_path is None or photo_output_path == "":
                import os
                photo_output_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH')  + "/" + ret_output_name
            else:
                nas_output_url = url_map(photo_output_path)
                photo_output_path = docker_map_url_prefix + nas_output_url + "/" + ret_output_name

            if checkSameImage(local_download_path1, local_download_path2) is True:
                log_dic_sameImage = log_dic_current.copy()
                log_dic_sameImage["beginTime"] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_sameImage["taskClassesType"] = tmp_taskClassesType
                log_dic_sameImage["taskstage"] = tmp_taskClassesType + " success"
                log_dic_sameImage["reason"] = "both images are the same, not processed"
                import shutil
                shutil.copy(local_download_path1, photo_output_path)
                task_executing_dic[task_id]["result"] = linuxPath2WinPath(net_url_prefix + mapurl_to_neturl(photo_output_path))
                time.sleep(1)
                log_dic_sameImage["endTime"] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_sameImage["output"] = linuxPath2WinPath(net_url_prefix + mapurl_to_neturl(photo_output_path))
                log_jihe.append(log_dic_sameImage)
                update_task_logs_by_task_id(task_id, log_jihe)
                send_message(task_id, tmp_task.task_params_json.get("user"), str(tmp_taskClassesType) + " success", linuxPath2WinPath(net_url_prefix + mapurl_to_neturl(photo_output_path)), "", import_list=minio_photo_download_paths)

            else:
                if tmp_task_dic.get("output") is None:
                    photo_output_path = ""
                else:
                    photo_output_path = docker_map_url_prefix + url_map(tmp_task_dic.get("output")) + "/" 

                timestamp1 = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
                print(timestamp1)
                forder = from_path_get_filename(local_download_path1) + "_" + from_path_get_filename(local_download_path2) + "_" + timestamp1
                print(forder)

                if "georeference" in tmp_task_dic.keys():
                    task_executing_dic[task_id]["taskStage"] = "georeference"
                    log_dic_georeference = log_dic_current.copy()
                    log_dic_georeference["beginTime"] = str(datetime.datetime.now().astimezone(SHA_TZ))
                    log_dic_georeference['taskClassesType'] = 'georeference'
                    log_dic_georeference['taskstage'] = "georeference begin"
                    processErrorFlag = False

                    # res_list = process_img_georeference_task(tmp_task_dic.get('georeference'),
                    #                                                                        local_download_path1,
                    #                                                                        local_download_path2,
                    #                                                                        photo_output_path, task_id, forder)
                    
                    try:
                        processErrorFlag = False
                        res_list = process_img_georeference_task(tmp_task_dic.get('georeference'), local_download_path1, local_download_path2, photo_output_path, task_id, forder)
                    except Exception as e:
                        print(e)
                        print("process img georeference error")
                        send_message(task_id, tmp_task.task_params_json.get("user"),
                                    "georeference failed", "", e)
                        update_task_status_by_task_id(task_id, 1)
                        update_task_completeRate_by_task_id(task_id, 0)
                        update_task_endtime_by_task_id(task_id)
                        processErrorFlag = True
                        task_executing_dic.pop(task_id)
                        import torch
                        torch.cuda.empty_cache(),print('显存清理完成！')
                    if processErrorFlag:
                        continue

                    ws_res_list = []

                    for t in res_list:
                        ws_res_list.append(linuxPath2WinPath(t))

                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                        "georeference success", ws_res_list, "", import_list=minio_photo_download_paths)

                    log_dic_georeference['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                    log_dic_georeference['taskstage'] ="georeference success"
                    log_dic_georeference['output'] = ws_res_list
                    log_jihe.append(log_dic_georeference)
                    update_task_logs_by_task_id(task_id, log_jihe)
        

                if "fusion" in tmp_task_dic.keys():
                    task_executing_dic[task_id]["taskStage"] = "fusion"
                    log_dic_fusion = log_dic_current.copy()
                    local_res_list = []
                    for i in range(len(res_list)):
                        local_res_list.append(neturl_to_localurl(res_list[i]))
                    log_dic_fusion["beginTime"] = str(datetime.datetime.now().astimezone(SHA_TZ))
                    log_dic_fusion["import"] = [ws_res_list[6], ws_res_list[7]]
                    log_dic_fusion['taskClassesType'] = 'fusion'
                    proportion = tmp_task_dic.get("proportion")

                    # out=process_img_fusion_task(tmp_task_dic.get('fusion'), local_res_list, photo_output_path, task_id, local_download_path1, forder, proportion)
                    try:
                        processErrorFlag = False
                        out = process_img_fusion_task(tmp_task_dic.get('fusion'), local_res_list,
                                                    photo_output_path, task_id, local_download_path1, forder, proportion)
                    except Exception as e:
                        print(e)
                        print("process img fusion error")
                        send_message(task_id, tmp_task.task_params_json.get("user"),
                                    "fusion failed", "", e)
                        log_dic_fusion['taskstage'] = "fusion failed"
                        log_jihe.append(log_dic_fusion)
                        update_task_logs_by_task_id(task_id, log_jihe)
                        update_task_status_by_task_id(task_id, 1)
                        update_task_completeRate_by_task_id(task_id, 0)
                        update_task_endtime_by_task_id(task_id)
                        processErrorFlag = True
                        task_executing_dic.pop(task_id)
                    if processErrorFlag:
                        continue

                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                        "fusion success", linuxPath2WinPath(out), "", import_list=minio_photo_download_paths)

                    log_dic_fusion['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                    log_dic_fusion['taskstage'] ="fusion success"
                    log_dic_fusion['output'] = linuxPath2WinPath(out)
                    log_jihe.append(log_dic_fusion)
                    update_task_logs_by_task_id(task_id, log_jihe)

                if "detect" in tmp_task_dic.keys():
                    local_res_list = []
                    for i in range(len(res_list)):
                        local_res_list.append(neturl_to_localurl(res_list[i]))
                    task_executing_dic[task_id]["taskStage"] = "detect"
                    log_dic_detect = log_dic_current.copy()
                    log_dic_detect["beginTime"] = str(datetime.datetime.now().astimezone(SHA_TZ))
                    log_dic_detect["import"] = [ws_res_list[2], ws_res_list[1]]
                    log_dic_detect['taskstage'] = "detect begin"
                    log_dic_detect['taskClassesType'] = 'detect'

                    # out = process_img_detect_task(tmp_task_dic.get('detect'), local_res_list, photo_output_path, task_id, local_download_path1, forder)

                    try:
                        processErrorFlag = False
                        out = process_img_detect_task(tmp_task_dic.get('detect'), local_res_list, photo_output_path, task_id, local_download_path1, forder)
                    except Exception as e:
                        print(e)
                        print("process img detect error")
                        send_message(task_id, tmp_task.task_params_json.get("user"),
                                    "detect failed", "", e)
                        update_task_status_by_task_id(task_id, 1)
                        update_task_completeRate_by_task_id(task_id, 0)
                        update_task_endtime_by_task_id(task_id)
                        processErrorFlag = True
                        task_executing_dic.pop(task_id)
                        import torch
                        torch.cuda.empty_cache(),print('显存清理完成！')
                    if processErrorFlag:
                        continue

                    print(task_executing_dic.get(task_id)["result"])
                    
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                        "detect success", linuxPath2WinPath(out), "", import_list=minio_photo_download_paths)

                    log_dic_detect['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                    log_dic_detect['taskstage'] = "detect success"
                    log_dic_detect['output'] = linuxPath2WinPath(out)
                    log_jihe.append(log_dic_detect)
                    update_task_logs_by_task_id(task_id, log_jihe)

            print ("%s processing %s %s" % (threadName, task_id, tmp_task.task_params_json))
            task_executing_dic[task_id]["completeRate"] = 100
            update_task_resulturl_by_task_id(task_id, task_executing_dic[task_id]["result"])
            update_task_status_by_task_id(task_id, 1)
            update_task_completeRate_by_task_id(task_id, 100)
            update_task_endtime_by_task_id(task_id)
            task_executing_dic.pop(task_id)
        else:
            queueLock.release()
        time.sleep(1)
        queueLock.acquire()
        if enhance_task_q.get_nums() > 0:
            tmp_task = enhance_task_q.get_que().popleft()
            queueLock.release()
            update_task_status_by_task_id(tmp_task.task_id, 2)

            task_id = str(tmp_task.task_id)
            send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "begin to execute", "", "")
            task_executing_dic[task_id]["taskStage"] = "prepare to execute"
            tmp_task_dic = tmp_task.task_params_json
            m_operator = tmp_task_dic.get("alg").get("algType")
            alg_dic = tmp_task_dic.get("alg")
            json_photo_download_path = tmp_task_dic.get("import")
            minio_photo_upload_path = tmp_task_dic.get("output")
            if minio_photo_upload_path == None or minio_photo_upload_path == "":
                local_upload_path = ""
            else:
                nas_output_url = url_map(minio_photo_upload_path)
                local_upload_path = docker_map_url_enhance_prefix + nas_output_url + "/"
            nas_import_url = url_map(json_photo_download_path)
            local_download_path = docker_map_url_enhance_prefix + nas_import_url

            timestamp1 = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
            forder = from_path_get_filename(json_photo_download_path)  + "_" + timestamp1
            import datetime
            log_jihe = []
            log_dic = {'beginTime': '', 'endTime': '', 'user': '', 'import': '', 'output': '', 'taskType': '',
                       'taskId': '', 'taskstage': '', 'taskClassesType': ""}
            log_dic_current = log_dic.copy()
            log_dic_current['beginTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
            log_dic_current['user'] = tmp_task.task_params_json.get("user")
            log_dic_current['import'] = tmp_task_dic.get("import")
            log_dic_current['output'] = tmp_task_dic.get("output")
            log_dic_current['taskId'] = task_id

            tasktype = select_task_by_task_id(task_id)['task_type']

            if (int(tasktype) == 1):
                log_dic_current['taskType'] = 'LongTasks'
            else:
                log_dic_current['taskType'] = 'ShortTasks'
            log_dic_current['taskstage'] = "prepare to execute"


            if "adjust" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "adjust"
                log_dic_adjust=log_dic_current.copy()
                log_dic_adjust['taskClassesType']='adjust'
                log_dic_adjust['taskstage'] = "image adjust begin"

                try:
                    processErrorFlag = False
                    out = process_img_adjust_task(alg_dic, local_download_path, local_upload_path, task_id)
                except Exception as e:
                    print(e)
                    print("process img adjust error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "adjust failed", "", "adjust failed")
                    update_task_status_by_task_id(task_id, 5)

                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue

                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "adjust success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)

                log_dic_adjust['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_adjust['taskstage'] = "image adjust success"
                log_dic_adjust['output']=linuxPath2WinPath(out)
                log_jihe.append(log_dic_adjust)
                update_task_logs_by_task_id(task_id, log_jihe)

            elif "denoise" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "denoise"
                log_dic_denoise=log_dic_current.copy()
                log_dic_denoise['taskClassesType']='denoise'
                log_dic_denoise['taskstage'] = "image denoise begin"
                # out = process_img_denoise_task(alg_dic, local_download_path, local_upload_path, task_id, forder)

                try:
                    processErrorFlag = False
                    out=process_img_denoise_task(alg_dic, local_download_path, local_upload_path, task_id, forder)
                except Exception as e:
                    print(e)
                    print("process img denoise error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "denoise failed", "", "denoise failed")
                    update_task_status_by_task_id(task_id, 1)
                    update_task_completeRate_by_task_id(task_id, 0)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue

                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "denoise success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)

                log_dic_denoise['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_denoise['taskstage'] = "image denoise success"
                log_dic_denoise['output'] = linuxPath2WinPath(out)
                log_jihe.append(log_dic_denoise)
                update_task_logs_by_task_id(task_id, log_jihe)

            elif "enhance" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "enhance"
                log_dic_enhance = log_dic_current.copy()
                log_dic_enhance['taskClassesType'] = 'enhance'
                log_dic_enhance['taskstage'] = "image enhance begin"
                # out=process_img_enhance_task(alg_dic, local_download_path, local_upload_path, task_id, forder)

                try:
                    processErrorFlag = False
                    out=process_img_enhance_task(alg_dic, local_download_path, local_upload_path, task_id, forder)
                except Exception as e:
                    print(e)
                    print("process img enhance error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "enhance failed", "", "enhance failed")
                    update_task_status_by_task_id(task_id, 1)
                    update_task_completeRate_by_task_id(task_id, 0)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue

                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "enhance success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)
                log_dic_enhance['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_enhance['taskstage'] = "image enhance success"
                log_dic_enhance['output'] = linuxPath2WinPath(out)
                log_jihe.append(log_dic_enhance)
                update_task_logs_by_task_id(task_id, log_jihe)

            elif "revise" == m_operator:
                task_executing_dic[task_id]["taskStage"] = "revise"
                log_dic_revise=log_dic_current.copy()
                log_dic_revise['taskClassesType']='revise'
                log_dic_revise['taskstage'] = "image revise begin"

                try:
                    processErrorFlag = False
                    out = process_img_revise_task(alg_dic, local_download_path, local_upload_path, task_id)
                except Exception as e:
                    print(e)
                    print("process img revise error")
                    send_message(task_id, tmp_task.task_params_json.get("user"),
                                 "revise failed", "", "revise failed")
                    update_task_status_by_task_id(task_id, 5)
                    update_task_endtime_by_task_id(task_id)
                    processErrorFlag = True
                    task_executing_dic.pop(task_id)
                    import torch
                    torch.cuda.empty_cache(),print('显存清理完成！')
                if processErrorFlag:
                    continue
                send_message(task_id, tmp_task.task_params_json.get("user"),
                                                                       "revise success", linuxPath2WinPath(out), "", import_list=json_photo_download_path)
                log_dic_revise['endTime'] = str(datetime.datetime.now().astimezone(SHA_TZ))
                log_dic_revise['taskstage'] ="image revise success"
                log_dic_revise['output'] = linuxPath2WinPath(out)
                log_jihe.append(log_dic_revise)
                update_task_logs_by_task_id(task_id, log_jihe)
            else:
                print("unknown action")
            print("%s processing %s %s" % (threadName, tmp_task.task_id, tmp_task.task_params_json))
            update_task_resulturl_by_task_id(task_id, task_executing_dic[task_id]["result"])
            update_task_status_by_task_id(task_id, 1)
            update_task_completeRate_by_task_id(task_id, 100)
            update_task_endtime_by_task_id(task_id)
            task_executing_dic.pop(task_id)
        else:
            queueLock.release()
        time.sleep(1)

# 初始化线程
def init_task_handle_thread():
    threads = []
    threadID = 1
    IFCCD_TASK_QUEUE = current_app.config.get("IFCCD_TASK_QUEUE")
    ENHANCE_TASK_QUEUE = current_app.config.get("ENHANCE_TASK_QUEUE")

    LONG_TASK_NUMS = os.getenv("LONG_TASK_NUMS")
    SHORT_TASK_NUMS = os.getenv("SHORT_TASK_NUMS")
    time.sleep(5)

    # 创建新线程
    for i in range(int(LONG_TASK_NUMS)):
        thread = Both_Task_Handle_Thread(threadID, "THREAD-" + str(threadID), IFCCD_TASK_QUEUE, ENHANCE_TASK_QUEUE)
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)
        threadID += 1

    for i in range(int(SHORT_TASK_NUMS)):
        thread = Enhance_Task_Handle_Thread(threadID, "THREAD-" + str(threadID),  ENHANCE_TASK_QUEUE)
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)
        threadID += 1

'''
    下面任务是enhance_task
'''
#校正
def process_img_adjust_task(alg_dic, photo_import_path, photo_output_path, task_id):
    photo_import_name =from_path_get_filefullname(photo_import_path)
    alg_name = alg_dic.get("algName")
    alg_params = alg_dic.get("params")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)
    src_file = open(photo_import_path, "rb")
    split_for_pin = photo_import_name.split(".")
    photo_output_name = split_for_pin[0] + "_adjust_"  + "." + split_for_pin[1]
    ret_output_name = split_for_pin[0] +  "_adjust_withGeo." + split_for_pin[1]
    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(task_id) + "/" + photo_output_name
        ret_upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(task_id) + "/" + ret_output_name
    else:
        upload_path = photo_output_path + str(task_id) + "/" + photo_output_name
        ret_upload_path = photo_output_path + str(task_id) + "/" + ret_output_name

    target_file = open(upload_path, "wb")
    target_file.write(src_file.read())
    print("图像adjust成功")
    print("图像上传成功")
    res = net_url_enhance_prefix + mapurl_to_neturl(ret_upload_path)
    task_executing_dic.get(task_id)["result"] = res
    target_file.close()
    src_file.close()
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return (res)

#去噪
def process_img_denoise_task(alg_dic, photo_import_path,  photo_output_path, task_id, forder):
    #拿到文件名
    photo_import_name = from_path_get_filefullname(photo_import_path)
    #获取信息
    alg_name = alg_dic.get("algName")
    alg_params = alg_dic.get("params")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)
    src_file = open(photo_import_path, "rb")
    #切割字符串
    #split_for_pin[0] 文件名
    #split_for_pin[1] 文件类型
    split_for_pin = photo_import_name.rsplit(".", 1)
    #不带地理信息
    photo_output_name = split_for_pin[0] +  "_denoise_"  + "." + split_for_pin[1]
    #带地理信息
    ret_output_name = split_for_pin[0] +  "_denoise_withGeo." + split_for_pin[1]
    #默认值
    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        import os
        #str(forder)时间戳
        save_forder = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(forder) + "/"
        upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" +photo_output_name
        ret_upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" + ret_output_name
    else:
        save_forder = photo_output_path + str(forder) + "/" 
        upload_path = photo_output_path + str(forder) + "/" + photo_output_name
        ret_upload_path = photo_output_path + str(forder) + "/" + ret_output_name
    import os
    #检测文件夹是否存在
    _ = os.path.exists(save_forder)
    if not _:
        os.makedirs(save_forder)

    target_file = open(upload_path, "wb")
    target_file.write(src_file.read())

    if alg_name == "wiener":  # SAR-传统（超限）
        from applications.algorithms.wiener.wiener import wiener_donise
        print("wiener")
        wiener_donise(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "frost":  # 红外-传统
        from applications.algorithms.Pretreatment.frost import frost_donise
        print("frost")
        frost_donise(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "zishiying":  # 可见光-传统
        from applications.algorithms.Pretreatment.zishiying import zishiying_donise
        print("zishiying")
        zishiying_donise(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)


    elif alg_name == "lee":  # sar-传统
        from applications.algorithms.Pretreatment.lee import lee
        print("lee")
        lee(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "linyu_aver":  # 通用（窗口/局部均值）
        from applications.algorithms.Pretreatment.linyu_average import linyu
        print("linyu_aver")
        linyu(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)

    elif alg_name == "pinyu":  # 可见光-传统
        from applications.algorithms.Pretreatment.pinyu import pinyu
        print("pinyu")
        pinyu(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "DRUNet_main":  # 红外-智能（多尺度细节）
        from applications.algorithms.DRUNetmain.predict import DRUNet_main
        print("DRUNet_main")
        DRUNet_main(
            photo_import_path,
            upload_path,
            task_id, forder)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "gamma":  # 红外-传统
        from applications.algorithms.Pretreatment.gamma import gamma_denoise
        print("gamma")
        gamma_denoise(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "tongtai":  # 可见光-传统
        from applications.algorithms.Pretreatment.tongtai_filter import tongtai_enhance
        print("tongtai")
        tongtai_enhance(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "wavelet":  # 可见光-传统
        from applications.algorithms.Pretreatment.wavelet import wavelet_denoise
        print("wavelet")
        wavelet_denoise(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "dehaze":  # 可见光-传统（暗通道）
        from applications.algorithms.Pretreatment.dehaze import dehaze
        print("dehaze")
        dehaze(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)

    elif alg_name == "retinex":  # 可见光-智能（暗夜）
        from applications.algorithms.Pretreatment.Retinex_master.run import Retinex
        print("retinex")
        Retinex(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "ADNet":  # SAR-智能（注意力cnn）
        from applications.algorithms.Pretreatment.ADNet_master.ADNet_master.color.test_c import ADNet_m
        print("ADNet")
        ADNet_m(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)

    else:
        raise Exception("error algname")
    print("图像denoise成功")
    print("图像上传成功")
    res = net_url_enhance_prefix + mapurl_to_neturl(ret_upload_path)
    task_executing_dic.get(task_id)["result"] = res
    target_file.close()
    src_file.close()
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return res

#增强
def process_img_enhance_task(alg_dic, photo_import_path, photo_output_path, task_id, forder):
    photo_import_name = from_path_get_filefullname(photo_import_path)
    alg_name = alg_dic.get("algName")
    alg_params = alg_dic.get("params")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)
    src_file = open(photo_import_path, "rb")

    split_for_pin = photo_import_name.rsplit(".", 1)
    photo_output_name = split_for_pin[0] +  "_enhance_"  + "." + split_for_pin[1]
    ret_output_name = split_for_pin[0] +  "_enhance_withGeo." + split_for_pin[1]
    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        import os
        save_forder = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(forder) + "/"
        upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" +photo_output_name
        ret_upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" + ret_output_name
    else:
        save_forder = photo_output_path + str(forder) + "/"
        upload_path = photo_output_path + str(forder) + "/" + photo_output_name
        ret_upload_path = photo_output_path + str(forder) + "/" + ret_output_name
    import os
    _ = os.path.exists(save_forder)
    if not _:
        os.makedirs(save_forder)


    target_file = open(upload_path, "wb")
    target_file.write(src_file.read())

    if alg_name == "middle":  # 通用（中值）
        from applications.algorithms.Pretreatment.middle import middle
        print("middle")
        middle(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "Gaussian":  # 通用
        from applications.algorithms.Pretreatment.Gaussian import Gaussian_donise
        print("Gaussian")
        Gaussian_donise(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "Psedocolor":
        from applications.algorithms.Pretreatment.Pseudocolor import pseudocolor
        pseudocolor(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    elif alg_name == "bianyuan":
        from applications.algorithms.Pretreatment.bianyuan import bianyuan
        bianyuan(photo_import_path, upload_path, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(photo_import_path, upload_path)
    else:
        raise Exception("error algname")
    print("图像enhance成功")
    print("图像上传成功")
    res = net_url_enhance_prefix + mapurl_to_neturl(upload_path)
    task_executing_dic.get(task_id)["result"] = res
    target_file.close()
    src_file.close()
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return res

#复原（未使用）
def process_img_revise_task(alg_dic, photo_import_path, photo_output_path, task_id):
    photo_import_name = from_path_get_filefullname(photo_import_path)
    alg_name = alg_dic.get("algName")
    alg_params = alg_dic.get("params")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)
    src_file = open(photo_import_path, "rb")
    split_for_pin = photo_import_name.split(".")
    photo_output_name = split_for_pin[0] + "_revise_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + "." + \
                        split_for_pin[1]

    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        upload_path = options.docker_map_url_enhance_prefix + os.getenv('SAVE_PATH') + str(task_id) + "/" + photo_output_name
    else:
        upload_path = photo_output_path + str(task_id) + "/" + photo_output_name

    target_file = open(upload_path, "wb")
    target_file.write(src_file.read())
    print("图像revise成功")
    print("图像上传成功")
    res = net_url_enhance_prefix + mapurl_to_neturl(upload_path)
    task_executing_dic.get(task_id)["result"] = res
    target_file.close()
    src_file.close()
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return (res)



'''
    下面任务是ifccd_task
'''
# 配准
def process_img_georeference_task(georeference_dic, photo_import_path1, photo_import_path2, photo_output_path, task_id, forder):
    alg_name = georeference_dic.get("algName")
    alg_params = georeference_dic.get("params")
    points = georeference_dic.get("GCP")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)
    
    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        import os
        photo_output_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH')  + "/"
    else:
        photo_output_path = photo_output_path  + "/"
    import os
    _ = os.path.exists(str(photo_output_path) + "/" + str(forder) + "/")
    print(_)
    if not _:
        os.makedirs(str(photo_output_path) + "/" + str(forder) + "/")
    try:
        if alg_name == "IR":
            from applications.algorithms.IR.cnn.cnnmatching import IR
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = IR(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)

        elif alg_name == "IR_VIS":
            from applications.algorithms.IR_VIS_georeference.cnn.cnnmatching import IR_VIS
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = IR_VIS(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)

        elif alg_name == "SAR":
            from applications.algorithms.SAR_georeference.cnn.cnnmatching import SAR
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = SAR(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)

        elif alg_name == "VIS":
            from applications.algorithms.VIS_georeference.cnn.cnnmatching import VIS
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = VIS(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
        elif alg_name == "VIS_SAR":
            from applications.algorithms.VIS_SAR_georeference.cnn.cnnmatching import VIS_SAR
            from applications.algorithms.GPS_georeference.GPS import GPS_registration
            print("GPS georeference begin")
            res_list = GPS_registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
            print("GPS georeference over")
            print("SAR_IR georeference begin")
            import os
            newurl = photo_output_path + str(forder) + "/VIS_SAR/"
            print(newurl)
            if not os.path.exists(newurl):
                print("not found")
                os.makedirs(newurl, mode=0o777)
            res_list = VIS_SAR(res_list[0], res_list[5], photo_output_path, task_id, forder)

        elif alg_name == "SAR_IR":
            from applications.algorithms.SAR_IR_georeference.DeepLearning.cnnmatching import registration
            from applications.algorithms.GPS_georeference.GPS import GPS_registration
            print("GPS begin")
            res_list = GPS_registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
            import os
            newurl = photo_output_path + str(forder) + "/SAR_IR/"
            print(newurl)
            if not os.path.exists(newurl):
                print("mkdir: " + newurl)
                os.makedirs(newurl, mode=0o777)
            print(res_list[0])
            print(res_list[5])
            res_list = registration(res_list[0], res_list[5], photo_output_path, task_id, forder)
        elif alg_name == "GPS":
            from applications.algorithms.GPS_georeference.GPS import GPS_registration
            res_list = GPS_registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)


        elif alg_name == "IR_tradition":
            from applications.algorithms.IR.IR import IR_tradition
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = IR_tradition(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
        elif alg_name == "IR_VIS_tradition":
            from applications.algorithms.IR_VIS_georeference.IR_VIS import IR_VIS_TRADITION
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = IR_VIS_TRADITION(photo_import_path1, photo_import_path2, photo_output_path, task_id, alg_params, forder)
        elif alg_name == "SAR_tradition":
            from applications.algorithms.SAR_georeference.SAR import SAR_TRADITION
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = SAR_TRADITION(photo_import_path1, photo_import_path2, photo_output_path, task_id, alg_params, forder)
        elif alg_name == "SAR_IR_tradition":
            from applications.algorithms.SAR_IR_georeference.SAR_IR import SAR_IR_main
            from applications.algorithms.GPS_georeference.GPS import GPS_registration
            print("GPS georeference begin")
            res_list = GPS_registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
            import os
            newurl = photo_output_path + str(forder) + "/SAR_IR/"
            print(newurl)
            if not os.path.exists(newurl):
                os.makedirs(newurl, mode=0o777)
            print(res_list[0])
            print(res_list[5])
            res_list = SAR_IR_main(res_list[0], res_list[5], photo_output_path, task_id, forder, method='RANSAC')
            print("SAR_IR georeference over")
        elif alg_name == "VIS_tradition":
            from applications.algorithms.VIS_georeference.VIS import registration
            from applications.algorithms.GPS_georeference.GPUjudge import judge
            judge(photo_import_path1, photo_import_path2)
            res_list = registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
        elif alg_name == "VIS_SAR_tradition":
            from applications.algorithms.VIS_SAR_georeference.VIS_SAR import VIS_SAR_tradition
            from applications.algorithms.GPS_georeference.GPS import GPS_registration
            print("GPS georeference begin")
            res_list = GPS_registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)
            print("GPS georeference over")
            print("SAR_IR georeference begin")
            print(res_list[0])
            print(res_list[5])
            import os
            newurl = photo_output_path + str(forder) + "/VIS_SAR/"
            print(newurl)
            if not os.path.exists(newurl):
                os.makedirs(newurl, mode=0o777)
            res_list = VIS_SAR_tradition(res_list[0], res_list[5], photo_output_path, task_id, forder)
        elif alg_name == "Manual_georeference":
            from applications.algorithms.ManualSelect_georeference.Manual_registration import registration
            res_list = registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, points, forder)
        else:
            print("error algname")
            raise Exception("error algname")
        print("图像georeference成功")
        print("图像上传成功")
    except HomographyError as e:
        print(e)
        from applications.algorithms.GPS_georeference.GPS import GPS_registration
        res_list = GPS_registration(photo_import_path1, photo_import_path2, photo_output_path, task_id, forder)

    for i in range(len(res_list)):
        res_list[i] = net_url_prefix + mapurl_to_neturl(res_list[i])
    print(res_list)
    task_executing_dic.get(task_id)["result"] = res_list
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return res_list

#融合
def process_img_fusion_task(fusion_dic, res_list, photo_output_path, task_id, local_download_path1, forder, proportion):

    alg_name = fusion_dic.get("algName")
    alg_params = fusion_dic.get("params")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)

    photo_output_name = "fusion_result.tif"
    ret_output_name = "fusion_resultwithGeo.tif"
    ret_output_path = ""
    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        # upload_path = options.docker_map_default_url_prefix + photo_output_name
        upload_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" + photo_output_name
        ret_upload_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" + ret_output_name
        ret_output_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "_" + ret_output_name
        ret_output_path1 = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "_" + photo_output_name
    else:
        upload_path = photo_output_path + str(forder) + "/" + photo_output_name
        ret_upload_path = photo_output_path + str(forder) + "/" + ret_output_name
        ret_output_path = photo_output_path + str(forder) + "_" + ret_output_name
        ret_output_path1 = photo_output_path + str(forder) + "_" + photo_output_name

    if (proportion is None):
        proportion = 50;
    
    # 如果有权重参数且不为50， 调用weight_fusion
    if proportion != 50:
        from applications.algorithms.Weight_Fusion.weight_fusion import weight_fusion
        p1_weight = proportion / 100.0;
        p2_weight = 1 - p1_weight
        weight_fusion(res_list[6], res_list[7], ret_output_path1, task_id, p1_weight, p2_weight)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)

    else:
        # 否则正常调用
        if alg_name == "TIF":
            from applications.algorithms.TIF.TIF import TIF_fusion
            TIF_fusion(res_list[6], res_list[7], ret_output_path1, task_id)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)

        elif alg_name == "GFF":  # 传统！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            from applications.algorithms.SAR_IR_fusion_tradition2.GFF import SAR_VIS_fusion_GFF
            print("SAR_VIS_fusion_GFF")
            SAR_VIS_fusion_GFF(res_list[6], res_list[7], ret_output_path1, task_id)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)

        elif alg_name == "WAVELET":  # 传统！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            print(upload_path)
            from applications.algorithms.IR_VIS_fusion_tradition2.wavelet import IR_VIS_fusion_wavelet
            IR_VIS_fusion_wavelet(res_list[6], res_list[7], ret_output_path1, task_id)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)

        elif alg_name == "VSMWLS":  # 传统！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            from applications.algorithms.SAR_VIS_fusion_tradition2.VSMWLS import SAR_VIS_fusion_VSMWLS
            print("SAR_VIS_fusion_VSMWLS")
            SAR_VIS_fusion_VSMWLS(res_list[6], res_list[7], ret_output_path1, task_id)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)
            
        elif alg_name == "DIF_Net":  # 智能
            from applications.algorithms.SAR_IR_fusion.test import SAR_IR_fusion_DIF_Net
            SAR_IR_fusion_DIF_Net(res_list[6], res_list[7], ret_output_path1, task_id, forder)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)
        elif alg_name == "CNN":  # 智能
            from applications.algorithms.IR_VIS_fusion.test import IR_VIS_FUSION_CNN
            print("IR_VIS_fusion_CNN")
            IR_VIS_FUSION_CNN(res_list[6], res_list[7], ret_output_path1, task_id, forder)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)
        elif alg_name == "IFCNN":  # 智能
            from applications.algorithms.SAR_VIS_fusion.test import SAR_VIS_fusion_IFCNN
            print("SAR_VIS_fusion_IFCNN")
            SAR_VIS_fusion_IFCNN(res_list[6], res_list[7], ret_output_path1, task_id, forder)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)

        elif alg_name == "GFCE":  # SAR_IR传统1
            from applications.algorithms.SAR_IR_fusion_tradion1.GFCE import GFCE_fusion
            print("SAR_IR_fusion_GFCE")
            GFCE_fusion(res_list[6], res_list[7], ret_output_path1, task_id)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)
        elif alg_name == "ADF":  # IR_VIS传统1
            from applications.algorithms.IR_VIS_fusion_tradion1.ADF import ADF_fusion
            print("IR_VIS_fusion_ADF")
            ADF_fusion(res_list[6], res_list[7], ret_output_path1, task_id)
            from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
            ret_upload_path = copy_geoCoordSys(local_download_path1, ret_output_path1)

        else:
            print("error algname")
            raise Exception("error algname")

    print("图像fusion成功")
    print("图像上传成功")
    res = net_url_prefix + mapurl_to_neturl(ret_output_path)
    task_executing_dic.get(task_id)["result"] = res
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return res

#变量检测
def process_img_detect_task(detect_dic, local_res_list, photo_output_path, task_id, local_download_path1, forder):

    alg_name = detect_dic.get("algName")
    alg_params = detect_dic.get("params")
    print("使用的算法名称是：", alg_name)
    print("算法参数是： ", alg_params)

    photo_output_name = "detect_result.tif"
    ret_output_name = "detect_resultwithGeo.tif"
    ret_output_path = ""
    if photo_output_path is None or len(photo_output_path) == 0 or photo_output_path == "":
        upload_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" + photo_output_name
        ret_upload_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "/" + ret_output_name
        ret_output_path = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "_" + ret_output_name
        ret_output_path1 = options.docker_map_url_prefix + os.getenv('SAVE_PATH') + str(forder) + "_" + photo_output_name
    else:
        upload_path = photo_output_path + str(forder) + "/" + photo_output_name
        ret_upload_path = photo_output_path + str(forder) + "/" + ret_output_name
        ret_output_path = photo_output_path + str(forder) + "_" + ret_output_name
        ret_output_path1 = photo_output_path + str(forder) + "_" + photo_output_name

    if alg_name == "IR_PCA":
        from applications.algorithms.IR_PCA.PCAKmeans.main import PCAKmeans_main
        PCAKmeans_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)

    elif alg_name == "PCAKmeans":
        from applications.algorithms.PCAKmeans.PCAKmeans.main import PCAKmeans_main
        PCAKmeans_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "CVA":
        from applications.algorithms.CVA.CVA.cva import CVA_main
        CVA_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "MAD":
        from applications.algorithms.MAD.MAD.irmad import MAD_main
        MAD_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "ISFA":
        from applications.algorithms.ISFA.isfa import ISFA_main
        ISFA_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "SFA":
        from applications.algorithms.SFA.isfa import SFA_main
        SFA_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name=='VIS_DDNet':
        from applications.algorithms.VIS_DDNet.main import VIS_DDNet_main
        VIS_DDNet_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "Deep_SAR_CD":
        from applications.algorithms.SAR_Deep_SAR_CD_detect.main import Deep_SAR_CD_main
        Deep_SAR_CD_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "IR_CF":
        from applications.algorithms.IR_CF.CF_detect import CF_detect_main
        CF_detect_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "ChangeFormer_detect":
        from applications.algorithms.ChangeFormer_main.ChangeFormer_detect import ChangeFormer_detect_main
        ChangeFormer_detect_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "LBNet":
        from applications.algorithms.VIS_detect_LamboiseNet_master.change_detect import LBNet_main
        LBNet_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "SNUNet":
        from applications.algorithms.VIS_detect_SNUNet.change_detect import SNUNet_main
        SNUNet_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id, 0.0, 0.65)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "IR_SNU":
        from applications.algorithms.IR_detect_IR_SNU.change_detect import SNUNet_main
        print("enter ChangeFormer_detect")
        SNUNet_main(local_res_list[2], local_res_list[1], ret_output_path1, task_id, 0.1, 0.3)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "tcd":
        from applications.algorithms.tcd.tcd import targetChangeDetect
        targetChangeDetect(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    elif alg_name == "SAR_TCD":
        from applications.algorithms.SAR_TCD.sar_tcd import SARTargetChangeDetect
        SARTargetChangeDetect(local_res_list[2], local_res_list[1], ret_output_path1, task_id)
        from applications.algorithms.GPS_SAVE.gps_save import copy_geoCoordSys
        copy_geoCoordSys(local_download_path1, ret_output_path1)
    else:
        print("error algname")
        raise Exception("error algname")

    print("图像detect成功")
    print("图像上传成功")
    res = net_url_prefix + mapurl_to_neturl(ret_output_path)
    task_executing_dic.get(task_id)["result"] = res
    import torch
    torch.cuda.empty_cache(),print('显存清理完成！')
    return res
