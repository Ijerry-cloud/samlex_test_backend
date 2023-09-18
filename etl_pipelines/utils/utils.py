from pymongo import MongoClient


def get_mdb_conn(conn_string, db):
    client = MongoClient(conn_string)
    db = client[db]
    return db
