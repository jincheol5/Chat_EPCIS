from typing import Any,Literal
from collections import deque
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class MongoDB_Interface:
    """
    DB:
        - epcis
    Collection:
        - vocab
        - event
        - test_event
    """
    def __init__(self,
            port:int=27017,
            db_name:Literal["epcis"]="epcis"
        ):
        self.connect_db(port=port,db_name=db_name)

    def connect_db(self,
            port:int=27017,
            db_name:Literal["epcis"]="epcis"
        ):
        try:
            self.port=port
            self.client=MongoClient(f"mongodb://127.0.0.1:{port}/")
            self.db=self.client[db_name]
            self.current_collection=None
        except PyMongoError as e:
            print(f"MongoDB error: {e}")

    def disconnect_db(self):
        self.client.close()

    def set_collection(self,
            collection_name:Literal[
                "vocab",
                "event",
                "test_event"
            ]="event"
        ):
        """
        특정 collection 연결
        """
        try:
            self.current_collection=collection_name
            self.collection=self.db[collection_name]
        except PyMongoError as e:
            print(f"MongoDB error: {e}")

    def drop_collection(self,
            collection_name:Literal[
                "vocab",
                "event",
                "test_event"
            ]="event"
        ):
        """
        특정 collection 삭제
        """
        if self.current_collection!=collection_name:
            self.set_collection(collection_name=collection_name)
        try:
            self.current_collection=None
            self.collection.drop()
            print(f"{collection_name} collection is dropped!")
        except PyMongoError as e:
            print(f"MongoDB error:{e}")

    def delete_document_in_collection(self,
            collection_name:Literal[
                "vocab",
                "event",
                "test_event"
            ]="event",
            query:dict[str,Any]=None
        ):
        """
        특정 collection 내 조건에 맞는 document 삭제
        """
        if self.current_collection!=collection_name:
            self.set_collection(collection_name=collection_name)
        try:
            if query is None:
                self.collection.delete_many({})
            else:
                self.collection.delete_many(query)
            print(f"{collection_name} collection documents are deleted!")
            print(f"Query: {query}")
        except PyMongoError as e:
            print(f"MongoDB error:{e}")

    def insert_data_list(self,
            data_list:list,
            data_type:Literal["vocab","event"]="event"
        ):
        """
        여러 개의 document를 한번에 입력

        ordered=False 설정으로 입력 중 오류가 발생해도 나머지 document의 입력을 계속 시도
        """
        if self.current_collection!=data_type:
            self.set_collection(collection_name=data_type)
        try:
            self.collection.insert_many(data_list,ordered=False)
        except PyMongoError as e:
            print(f"MongoDB error:{e}")

    def find_event(self,
            query:dict[str,Any]=None,
        )->dict[str,Any]|None:
        """
        find_one():
            조건에 맞는 MongoDB document 하나를 python dict 형태로 반환
                query ex: {"_id":1}
            조건에 맞는 document가 없으면 None을 반환
        """
        if self.current_collection!="event":
            self.set_collection(collection_name="event")
        event=self.collection.find_one(query)
        return event

    def find_events(self,
            query:dict[str,Any]=None,
            limit:int|None=None
        ):
        """
        find():
            조건에 맞는 여러 MongoDB document를 반환
                query ex: {"type":"ObjectEvent"}
            여러 document를 순회하기 위한 Cursor 객체 반환
            list()로 결과를 dict 리스트로 변환 
        """
        if self.current_collection!="event":
            self.set_collection(collection_name="event")
        cursor=self.collection.find(query)
        if limit is not None:
            if limit<1:
                raise ValueError("limit은 1 이상의 정수여야 합니다.")
            cursor=cursor.limit(limit)
        return list(cursor)

    def find_distinct_values_in_event(self,field_name:str):
        """
        distinct():
            특정 필드에 존재하는 중복되지 않은 값(unique values)들을 조회
            반환값은 python list
        """
        if self.current_collection!="event":
            self.set_collection(collection_name="event")
        values=self.collection.distinct(field_name)
        return sorted(value for value in values if value is not None)

    def object_traceability(self,
            epc:str,
            direction:Literal[
                "backward",
                "forward"
            ]="backward",
            max_depth:int=5
        )->list[dict[str,Any]]:
        """
        특정 EPC에서 시작하여 관련 EPCIS 이벤트를 추적합니다.
        모든 분기에서 발견된 이벤트들을 하나의 traced_events 리스트에 합쳐 반환합니다.

        direction (탐색 방향):
            forward:
                시간 오름차순으로 탐색합니다.
                AggregationEvent: child -> parent
                TransformationEvent: input -> output
            backward:
                시간 내림차순으로 탐색합니다.
                AggregationEvent: parent -> child
                TransformationEvent: output -> input

        Input:
            epc: str
            direction: backward | forward
            max_depth: int
        Return:
            Traced EPCIS Event list
        """



















    # def find_event_types(self):
    #     """
    #     반환 예시:
    #         [
    #             "AggregationEvent",
    #             "AssociationEvent",
    #             "ObjectEvent",
    #             "TransformationEvent"
    #         ]
    #     """
    #     return self.find_distinct_event_values("type")

    # def find_biz_steps(self):
    #     return self.find_distinct_event_values("bizStep")

    # def find_biz_locations(self):
    #     return self.find_distinct_event_values("bizLocation.id")

    # def find_read_points(self):
    #     return self.find_distinct_event_values("readPoint.id")

    # def find_dispositions(self):
    #     return self.find_distinct_event_values("disposition")

    # def find_epcs(self):
    #     fields=(
    #         "parentID","epcList","childEPCs","inputEPCList","outputEPCList",
    #         "quantityList.epcClass","childQuantityList.epcClass",
    #         "inputQuantityList.epcClass","outputQuantityList.epcClass",
    #     )
    #     epcs=set()
    #     for field_name in fields:
    #         epcs.update(self.event_collection.distinct(field_name))
    #     epcs.discard(None)
    #     return sorted(epcs)

    # def find_events_by_event_type(self,
    #         event_type:Literal[
    #             "ObjectEvent",
    #             "AggregationEvent",
    #             "TransformationEvent",
    #             "TransactionEvent",
    #             "AssociationEvent"
    #         ],
    #         limit:int|None=None
    #     ):
    #     return self.find_events_by_filter(
    #         query={
    #             "type":event_type
    #         },
    #         limit=limit
    #     )

    # def find_events_by_biz_step(self,
    #         biz_step:str,
    #         limit:int|None=None
    #     ):
    #     return self.find_events_by_filter(
    #         query={
    #             "bizStep":biz_step
    #         },
    #         limit=limit
    #     )

    # def find_events_by_biz_location(self,
    #         biz_location:str,
    #         limit:int|None=None
    #     ):
    #     return self.find_events_by_filter(
    #         query={
    #             "bizLocation.id":biz_location
    #         },
    #         limit=limit
    #     )

    # def find_events_by_read_point(self,
    #         read_point:str,
    #         limit:int|None=None
    #     ):
    #     return self.find_events_by_filter(
    #         query={
    #             "readPoint.id":read_point
    #         },
    #         limit=limit
    #     )

    # def find_events_by_disposition(self,
    #         disposition:str,
    #         limit:int|None=None
    #     ):
    #     return self.find_events_by_filter(
    #         query={
    #             "disposition":disposition
    #         },
    #         limit=limit
    #     )

    # def find_events_by_epc(self,
    #         epc:str,
    #         limit:int|None=None
    #     ):
    #     fields=(
    #         "parentID","epcList","childEPCs","inputEPCList","outputEPCList",
    #         "quantityList.epcClass","childQuantityList.epcClass",
    #         "inputQuantityList.epcClass","outputQuantityList.epcClass",
    #     )
    #     return self.find_events_by_filter(
    #         query={
    #             "$or":[{field:epc} for field in fields]
    #         },
    #         limit=limit
    #     )

