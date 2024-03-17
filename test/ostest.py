import os
photo_output_path = "/mnt/linux_share/ifccd/photo/newdir/"
task_id = "123456"
newurl = photo_output_path + str(task_id) + "/SAR_IR"
if not os.path.exists(newurl):
    print("not found")
    os.makedirs(newurl, mode=0o777)
# os.mkdir(photo_output_path + str(task_id) + "/SAR_IR")