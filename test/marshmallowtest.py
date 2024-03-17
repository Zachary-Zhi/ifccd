from marshmallow import Schema, fields, post_load
import pymongo


class Database:
    @classmethod
    def initialize(cls):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/test")
        cls.database = client.get_default_database()
        print(1, cls.database)

    @classmethod
    def save_to_db(cls, data):
        print(2, cls.database)
        cls.database.stores.insert(data)

    @classmethod
    def load_from_db(cls, query):
        return cls.database.stores.find(query)

class Store:
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location


class StoreSchema(Schema):
    name = fields.Str()
    location = fields.Str()

    @post_load
    def make_store(self, data, **kwargs):
        return Store(**data)

walmart = Store("Walmart", "Venice, CA")
store_schema = StoreSchema()

print(store_schema.dump(walmart))
print(type(store_schema.dump(walmart)))


store_data = {"name": "Walmart", "location": "Venice, CA"}
store_schema = StoreSchema()

print(store_schema.load(store_data))
print(type(store_schema.load(store_data)))

Database.initialize()
Database.save_to_db({"name": "Walmart", "location": "Venice, CA"})

loaded_objects = Database.load_from_db({"name":"Walmart"})
print(loaded_objects)





