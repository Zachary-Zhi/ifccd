import os

# MongoDB设置
MONGODB_HOST = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DBNAME = "ifccd"

task_executing_dic = {}
stop_tasks_url = "/ifccd/stopTask/"
changePriority_url = "/ifccd/changePriority/"
log_url = "/ifccd/log/"
selectTaskUrl = "/ifccd/tasks"
send_message_pointer = None

page_size = 10
docker_map_url_prefix = "/mnt/linux_share/"
docker_map_default_url_prefix = "/mnt/linux_share/ifccd/upload/default/"
if os.getenv("IFCCD_PATH") is not None:
    net_url_prefix = os.getenv("IFCCD_PATH")

X_forwarded_host = "192.168.8.249:5004"

docker_map_url_enhance_prefix = "/mnt/share/"
if os.getenv("ENHANCE_PATH") is not None:
    net_url_enhance_prefix = os.getenv("ENHANCE_PATH")



