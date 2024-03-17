# flask配置
FLASK_APP = app.py
FLASK_ENV = development
FLASK_DEBUG = 0
FLASK_RUN_HOST = 0.0.0.0
FLASK_RUN_PORT = 5000

# ifccd配置
SYSTEM_NAME = ifccd

SECRET_KEY = 'ifccd'


# 插件配置
PLUGIN_ENABLE_FOLDERS = []

# MongoDB设置
MONGODB_HOST = 127.0.0.1
MONGODB_PORT = 27017
MONGODB_DBNAME = ifccd


# host_ip 主机ip地址
HOST_IP = 127.0.0.1


# NAS ip地址
NAS_HOST = 127.0.0.1
NAS_UPLOAD_DEFAULT_URL = file:///nasHost/processedImg

# 网关地址
NET_GATE_IP = 192.168.1.10
NET_GATE_PORT = 8080

# websocket 地址
WEB_SOCKET_IP = 127.0.0.1
WEB_SOCKET_IP = 8080

SAVE_PATH  = ifccd/upload/default/
WEBSOCKET_SERVER = ws://wshost:port/ifccd/init

# 创建融合，变化检测，配准等任务队列的长度（长任务队列）
IFCCD_TASK_PRIORITY_QUEUE_LENGTH = 100
# 创建图像增强、预处理、校正、去噪等任务队列的长度 （短任务队列）
ENHANCE_TASK_PRIORITY_QUEUE_LENGTH = 100

# 处理长任务的线程数
LONG_TASK_NUMS = 3
# 处理段任务的线程数
SHORT_TASK_NUMS = 0

# # websocket ip
# WEBSOCKET_IP = 192.168.8.183
# # websocket port
# WEBSOCKET_PORT = 5001
# # websocket url
# WEBSOCKET_URL = wsIFCCD