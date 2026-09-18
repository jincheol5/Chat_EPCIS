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

    def _trace_forward(self,
            epc:str,
            event_time:int
        ):
        """
        특정 EPC를 기준으로 시간 제약을 어기지 않는 정방향으로 연결된 EPC들과 해당 관계를 생성한 event들을 반환.
        탐색 event type: AggregationEvent, TransformationEvent

        forward 관계:
            AggregationEvent: 
                action = ADD:
                    childEPCs -> parentID 
                    childQuantityList.epcClass -> parentID 
                    예시: box들 (child) -> pallet (parent)로 집계되었다.
                action = DELETE:
                    parentID -> childEPCs
                    parentID -> childQuantityList.epcClass 
                    예시: pallet (parent) -> box들 (child)로 분해되었다.
            TransformationEvent: 
                inputEPCList -> outputEPCList
                inputQuantityList.epcClass -> outputEPCList 
                inputEPCList -> outputQuantityList.epcClass
                inputQuantityList.epcClass -> outputQuantityList.epcClass
        """
        query={
            "$or":[
                # Aggregation ADD: forward = child -> parent
                {
                    "type":"AggregationEvent",
                    "action":"ADD",
                    "$or":[
                        {"childEPCs":epc},
                        {"childQuantityList.epcClass":epc}
                    ]
                },

                # Aggregation DELETE: forward = parent -> child
                {
                    "type":"AggregationEvent",
                    "action":"DELETE",
                    "parentID":epc
                },

                # Transformation: input -> output
                {
                    "type":"TransformationEvent",
                    "$or":[
                        {"inputEPCList":epc},
                        {"inputQuantityList.epcClass":epc}
                    ]
                }
            ],
            "event_time":{
                "$gt":event_time
            }
        }
        related_epcs=[]
        related_events=self.find_events(query=query)
        for event in related_events:
            event_type=event.get("type")
            related_event_time=event["event_time"]
            match event_type:
                case "AggregationEvent":
                    action=event.get("action")
                    if action=="ADD":
                        parent_id=event.get("parentID")
                        related_epcs.append((parent_id,related_event_time))

                    if action=="DELETE":
                        # EPC Instance
                        for child_epc in event.get("childEPCs",[]):
                            related_epcs.append((child_epc,related_event_time))

                        # EPC Class
                        for quantity_element in event.get("childQuantityList",[]):
                            epc_class=quantity_element.get("epcClass")
                            related_epcs.append((epc_class,related_event_time))

                case "TransformationEvent":
                    # EPC Instance
                    for output_epc in event.get("outputEPCList",[]):
                        related_epcs.append((output_epc,related_event_time))

                    # EPC Class
                    for quantity_element in event.get("outputQuantityList",[]):
                        epc_class=quantity_element.get("epcClass")
                        related_epcs.append((epc_class,related_event_time))

        # 자기 자신 제거, 중복 제거
        related_epcs=[
            (related_epc,related_event_time)
            for related_epc,related_event_time in related_epcs
            if related_epc!=epc
        ]
        related_epcs=list(dict.fromkeys(related_epcs))
        return {
            "object":related_epcs,
            "event":related_events
        }

    def _trace_backward(self,
            epc:str,
            event_time:int
        ):
        """
        특정 EPC를 기준으로 시간 제약을 어기지 않는 역방향으로 연결된 EPC들을 탐색하여 반환.
        탐색 event type: AggregationEvent, TransformationEvent

        backward 관계:
            AggregationEvent: 
                action = ADD:
                    parentID -> childEPCs
                    parentID -> childQuantityList.epcClass 
                    예시: box들 (child) -> pallet (parent)로 집계되었다.
                action = DELETE:
                    childEPCs -> parentID
                    childQuantityList.epcClass -> parentID
                    예시: pallet (parent) -> box들 (child)로 분해되었다.
            TransformationEvent: 
                outputEPCList -> inputEPCList
                outputEPCList -> inputQuantityList.epcClass
                outputQuantityList.epcClass -> inputEPCList
                outputQuantityList.epcClass -> inputQuantityList.epcClass
        """
        query={
            "$or":[
                # Aggregation ADD: backward = parent -> child
                {
                    "type":"AggregationEvent",
                    "action":"ADD",
                    "parentID": epc
                },

                # Aggregation DELETE: backward = child -> parent
                {
                    "type":"AggregationEvent",
                    "action":"DELETE",
                    "$or": [
                        {"childEPCs": epc},
                        {"childQuantityList.epcClass":epc}
                    ]
                },

                # Transformation: output -> input
                {
                    "type":"TransformationEvent",
                    "$or":[
                        {"outputEPCList":epc},
                        {"outputQuantityList.epcClass":epc}
                    ]
                }
            ],
            "event_time":{
                "$lt":event_time
            }
        }
        related_epcs=[]
        related_events=self.find_events(query=query)
        for event in related_events:
            event_type=event.get("type")
            related_event_time=event["event_time"]
            match event_type:
                case "AggregationEvent":
                    action=event.get("action")
                    if action=="ADD":
                        # EPC Instance
                        for child_epc in event.get("childEPCs",[]):
                            related_epcs.append((child_epc,related_event_time))

                        # EPC Class
                        for quantity_element in event.get("childQuantityList",[]):
                            epc_class=quantity_element.get("epcClass")
                            related_epcs.append((epc_class,related_event_time))
                    if action=="DELETE":
                        parent_id=event.get("parentID")
                        related_epcs.append((parent_id,related_event_time))

                case "TransformationEvent":
                    # EPC Instance
                    for input_epc in event.get("inputEPCList",[]):
                        related_epcs.append((input_epc,related_event_time))

                    # EPC Class
                    for quantity_element in event.get("inputQuantityList",[]):
                        epc_class=quantity_element.get("epcClass")
                        related_epcs.append((epc_class,related_event_time))

        # 자기 자신 제거, 중복 제거
        related_epcs=[
            (related_epc,related_event_time)
            for related_epc,related_event_time in related_epcs
            if related_epc!=epc
        ]
        related_epcs=list(dict.fromkeys(related_epcs))
        return {
            "object":related_epcs,
            "event":related_events
        }

    def trace_object(self,
            epc:str,
            event_time:int,
            direction:Literal[
                "backward",
                "forward"
            ]="backward",
            max_hop:int=5
        )->list[dict[str,Any]]:
        """
        매 hop마다 이전 hop에서 찾은 (epc,event_time)을 하나 하나 direction 함수로 탐색.
        최종 반환 값은 각 hop 수를 key로 가지고 object와 event list dict를 value로 가지는 dict.

        Return:
            {
                0:{
                    "object":[(epc,event_time)],
                    "event":[]
                },
                1:{
                    "object":[...],
                    "event":[...]
                },
                ...
            }
        """
        match direction:
            case "backward":
                trace_fn=self._trace_backward
            case "forward":
                trace_fn=self._trace_forward

        final_trace_result={
            0:{
                "object":[(epc,event_time)],
                "event":[]
            }
        }
        cur_objects=[(epc,event_time)]
        for hop in range(1,max_hop+1):
            hop_objects=[]
            hop_events=[]
            for cur_epc,cur_event_time in cur_objects:
                trace_result=trace_fn(
                    epc=cur_epc,
                    event_time=cur_event_time
                )
                hop_objects.extend(trace_result["object"])
                hop_events.extend(trace_result["event"])

            # object 중복 제거
            hop_objects=list(dict.fromkeys(hop_objects))

            # event 중복 제거
            unique_events=[]
            seen_event_ids=set()
            for event in hop_events:
                event_id=event.get("eventID")
                if event_id in seen_event_ids:
                    continue
                seen_event_ids.add(event_id)
                unique_events.append(event)
            hop_events=unique_events

            # Add to final_trace_result
            final_trace_result[hop]={
                "object":hop_objects,
                "event":hop_events
            }

            # 더 이상 탐색할 object가 없으면 종료
            if len(hop_objects)==0:
                break
            cur_objects=hop_objects
        return final_trace_result









