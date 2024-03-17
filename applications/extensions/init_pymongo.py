import pymongo

pymongo_settings = {
    "host": "127.0.0.1",
    "db_name": "ifccd",
    "port": 27017
}
client = pymongo.MongoClient(host=pymongo_settings['host'])
db = client[pymongo_settings['db_name']]
print("db----------------")
if db is None:
    print("db is None")
print(db)

