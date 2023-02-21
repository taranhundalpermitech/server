from asyncio.log import logger
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from bson.json_util import dumps
import boto3
import dateutil.parser as parser
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PPEDetections')
DOMAIN = 'localhost'
PORT = 27017

delete_time = "23:50:00"

client = MongoClient(
"mongodb://mongodb_container:27017"
)
db = client["CV_DB"]

def check_limit(col):
    streams_count = col.count_documents({})
    if(streams_count>=4):
        return False
    else:
        return True
def create_stream(req):
    db = client["CV_DB"]
    col = db["streams"]
    check = check_limit(col)
    if(check == False):
        return {"status":False,"id":""}
    record = {"StreamUrl":req["StreamUrl"],"StreamName":req["StreamName"],"StreamRoom":req["StreamRoom"]}
    _id = col.insert_one(record)
    return {"status":True,"id":str(_id.inserted_id)} 

def stream_delete(sourceId):
    streams = db["streams"]
    streams.delete_one({'_id': ObjectId(sourceId)})
def get_streams():
    streams = db["streams"]
    return dumps(streams.find({}))

def get_PPE_detections(sourceId,start,end):
    start = parser.parse(start).strftime('%FT%T')
    end = parser.parse(end).strftime('%FT%T')
    attr = boto3.dynamodb.conditions.Attr('TimeStamp')
    resp = table.query(
            KeyConditionExpression=Key('SourceId').eq(sourceId),
            FilterExpression=attr.between(start,end) 
        )
    return resp["Items"]