from typing import Any,Literal
from pymongo import MongoClient
from pymongo.errors import PyMongoError


class MongoDB_Interface:
    """
    Collections:
        - event
        - vocab
    """
    def __init__(self,port:int=27017):
        try:
            self.client=MongoClient(f"mongodb://127.0.0.1:{port}/")
            self.db=self.client["epcis"]
            self.event_collection=self.db["event"]
            self.vocab_collection=self.db["vocab"]
        except PyMongoError as e:
            print(f"MongoDB error: {e}")

    def connect_db(self,port:int=27017):
        try:
            self.client=MongoClient(f"mongodb://127.0.0.1:{port}/")
            self.db=self.client["epcis"]
            self.event_collection=self.db["event"]
            self.vocab_collection=self.db["vocab"]
        except PyMongoError as e:
            print(f"MongoDB error: {e}")

    def disconnect_db(self):
        self.client.close()

    def delete_collection(self,collection_name:str):
        if self.client is None:
            self.connect_db()
        collection=self.db[collection_name]
        try:
            collection.delete_many({})
            print(f"{collection_name} collection is deleted!")
        except PyMongoError as e:
            print(f"MongoDB delete collection error: {e}")

    def insert_data_list(self,data_list:list,data_type:Literal["event","vocab"]):
        if self.client is None:
            self.connect_db()
        data_collection=self.event_collection if data_type=="event" else self.vocab_collection
        try:
            data_collection.insert_many(data_list,ordered=False)
        except PyMongoError as e:
            print(f"{data_type} type data list insert error: {e}")

    def find_events(self):
        return list(self.event_collection.find())

    def find_events_by_filter(self,query:dict[str,Any]):
        return list(self.event_collection.find(query))

    def find_distinct_event_values(self,field_name:str):
        values=self.event_collection.distinct(field_name)
        return sorted(value for value in values if value is not None)

    def find_event_types(self):
        return self.find_distinct_event_values("type")

    def find_biz_steps(self):
        return self.find_distinct_event_values("bizStep")

    def find_biz_locations(self):
        return self.find_distinct_event_values("bizLocation.id")

    def find_read_points(self):
        return self.find_distinct_event_values("readPoint.id")

    def find_dispositions(self):
        return self.find_distinct_event_values("disposition")

    def find_epcs(self):
        fields=(
            "parentID","epcList","childEPCs","inputEPCList","outputEPCList",
            "quantityList.epcClass","childQuantityList.epcClass",
            "inputQuantityList.epcClass","outputQuantityList.epcClass",
        )
        epcs=set()
        for field_name in fields:
            epcs.update(self.event_collection.distinct(field_name))
        epcs.discard(None)
        return sorted(epcs)

    def find_events_by_event_type(self,event_type:str):
        return self.find_events_by_filter({"type":event_type})

    def find_events_by_biz_step(self,biz_step:str):
        return self.find_events_by_filter({"bizStep":biz_step})

    def find_events_by_biz_location(self,biz_location:str):
        return self.find_events_by_filter({"bizLocation.id":biz_location})

    def find_events_by_read_point(self,read_point:str):
        return self.find_events_by_filter({"readPoint.id":read_point})

    def find_events_by_disposition(self,disposition:str):
        return self.find_events_by_filter({"disposition":disposition})

    def find_events_by_epc(self,epc:str):
        fields=(
            "parentID","epcList","childEPCs","inputEPCList","outputEPCList",
            "quantityList.epcClass","childQuantityList.epcClass",
            "inputQuantityList.epcClass","outputQuantityList.epcClass",
        )
        return self.find_events_by_filter({"$or":[{field:epc} for field in fields]})

    def find_event_by_id(self,event_id:str):
        event=self.event_collection.find_one({"_id":event_id})
        if event is None:
            return None
        return event

    def find_events_by_event_id(self,event_id:str):
        return self.find_events_by_filter({
            "$or":[
                {"eventID":event_id},
                {"errorDeclaration.correctiveEventIDs":event_id}
            ]
        })
