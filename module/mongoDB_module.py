from typing import Any,Literal
from collections import deque
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class MongoDB_Interface:
    """
    Collections:
        - event
        - vocab
    """
    def __init__(self,
            port:int=27017,
            isEvaluated:bool=False
        ):
        try:
            self.client=MongoClient(f"mongodb://127.0.0.1:{port}/")
            self.db=self.client["epcis"]
            if not isEvaluated:
                self.event_collection=self.db["event"]
            else:
                self.event_collection=self.db["test_event"]
            self.vocab_collection=self.db["vocab"]
        except PyMongoError as e:
            print(f"MongoDB error: {e}")

    def connect_db(self,
            port:int=27017,
            isEvaluated:bool=False
        ):
        try:
            self.client=MongoClient(f"mongodb://127.0.0.1:{port}/")
            self.db=self.client["epcis"]
            if not isEvaluated:
                self.event_collection=self.db["event"]
            else:
                self.event_collection=self.db["test_event"]
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
        match data_type:
            case "event":
                data_collection=self.event_collection
            case "vocab":
                data_collection=self.vocab_collection
        try:
            data_collection.insert_many(data_list,ordered=False)
        except PyMongoError as e:
            print(f"{data_type} type data list insert error: {e}")

    def find_event_by_id(self,
            event_id:str
        )->dict[str,Any]|None:
        event=self.event_collection.find_one({"_id":event_id})
        if event is None:
            return None
        return event

    def find_events(self,
            limit:int|None=None
        ):
        """
        """
        cursor=self.event_collection.find()
        if limit is not None:
            if limit<1:
                raise ValueError("limit은 1 이상의 정수여야 합니다.")
            cursor=cursor.limit(limit)
        return list(cursor)

    def find_events_by_filter(self,
            query:dict[str,Any],
            limit:int|None=None
        ):
        """
        query에 MongoDB 조회 조건을 전달.

        ex:
            query={"type":"ObjectEvent"}
        """
        cursor=self.event_collection.find(query)
        if limit is not None:
            if limit<1:
                raise ValueError("limit은 1 이상의 정수여야 합니다.")
            cursor=cursor.limit(limit)
        return list(cursor)

    def find_distinct_event_values(self,field_name:str):
        """
        전달한 필드에서 중복되지 않은 값들만 조회.
        """
        values=self.event_collection.distinct(field_name)
        return sorted(value for value in values if value is not None)

    def find_event_types(self):
        """
        반환 예시:
            [
                "AggregationEvent",
                "AssociationEvent",
                "ObjectEvent",
                "TransformationEvent"
            ]
        """
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

    def find_events_by_event_type(self,
            event_type:Literal[
                "ObjectEvent",
                "AggregationEvent",
                "TransformationEvent",
                "TransactionEvent",
                "AssociationEvent"
            ],
            limit:int|None=None
        ):
        return self.find_events_by_filter(
            query={
                "type":event_type
            },
            limit=limit
        )

    def find_events_by_biz_step(self,
            biz_step:str,
            limit:int|None=None
        ):
        return self.find_events_by_filter(
            query={
                "bizStep":biz_step
            },
            limit=limit
        )

    def find_events_by_biz_location(self,
            biz_location:str,
            limit:int|None=None
        ):
        return self.find_events_by_filter(
            query={
                "bizLocation.id":biz_location
            },
            limit=limit
        )

    def find_events_by_read_point(self,
            read_point:str,
            limit:int|None=None
        ):
        return self.find_events_by_filter(
            query={
                "readPoint.id":read_point
            },
            limit=limit
        )

    def find_events_by_disposition(self,
            disposition:str,
            limit:int|None=None
        ):
        return self.find_events_by_filter(
            query={
                "disposition":disposition
            },
            limit=limit
        )

    def find_events_by_epc(self,
            epc:str,
            limit:int|None=None
        ):
        fields=(
            "parentID","epcList","childEPCs","inputEPCList","outputEPCList",
            "quantityList.epcClass","childQuantityList.epcClass",
            "inputQuantityList.epcClass","outputQuantityList.epcClass",
        )
        return self.find_events_by_filter(
            query={
                "$or":[{field:epc} for field in fields]
            },
            limit=limit
        )

    def _get_event_epcs(
            self,
            event:dict[str,Any],
        )->set[str]:
        """
        하나의 EPCIS 이벤트에 포함된 모든 객체 식별자를 반환합니다.
            EPCIS Instance + class
        """
        epcs:set[str]=set()

        # 단일 식별자 필드
        parent_id=event.get("parentID")
        if parent_id is not None:
            epcs.add(parent_id)

        # EPC 리스트 필드
        list_fields=(
            "epcList",
            "childEPCs",
            "inputEPCList",
            "outputEPCList",
        )

        for field_name in list_fields:
            values=event.get(field_name) or []
            epcs.update(values)

        # 클래스 단위 식별자 필드
        quantity_fields=(
            "quantityList",
            "childQuantityList",
            "inputQuantityList",
            "outputQuantityList",
        )

        for field_name in quantity_fields:
            quantity_list=event.get(field_name) or []
            for quantity_element in quantity_list:
                epc_class=quantity_element.get("epcClass")
                if epc_class is not None:
                    epcs.add(epc_class)
        epcs.discard(None)
        return epcs

    def _get_related_epcs(
            self,
            event:dict[str,Any],
            current_epc:str,
            direction:Literal[
                "backward",
                "forward",
                "both",
            ]="both",
        )->set[str]:
        """
        현재 EPC와 이벤트의 관계를 바탕으로 다음에 탐색할 EPC를 반환합니다.

        direction:
            backward:
                현재 객체의 이전 객체 또는 내부 객체 방향을 탐색합니다.
                TransformationEvent:
                    output -> input
                AggregationEvent:
                    parent -> child
            forward:
                현재 객체로부터 생성되거나 현재 객체를 포함하는 상위 객체를
                탐색합니다.
                TransformationEvent:
                    input -> output
                AggregationEvent:
                    child -> parent
            both:
                양방향 모두 탐색합니다.
        """
        event_type=event.get("type")
        related_epcs:set[str]=set()

        if event_type in {
            "AggregationEvent",
            "AssociationEvent",
        }:
            parent_id=event.get("parentID")
            child_epcs=set(event.get("childEPCs") or [])
            for quantity_element in event.get(
                "childQuantityList",
            ) or []:
                epc_class=quantity_element.get("epcClass")
                if epc_class is not None:
                    child_epcs.add(epc_class)

            # child -> parent
            if (
                direction in {"forward","both"}
                and current_epc in child_epcs
                and parent_id is not None
            ):
                related_epcs.add(parent_id)

            # parent -> child
            if (
                direction in {"backward","both"}
                and current_epc==parent_id
            ):
                related_epcs.update(child_epcs)

        elif event_type=="TransformationEvent":
            input_epcs=set(event.get("inputEPCList") or [])
            output_epcs=set(event.get("outputEPCList") or [])
            for quantity_element in event.get(
                "inputQuantityList",
            ) or []:
                epc_class=quantity_element.get("epcClass")
                if epc_class is not None:
                    input_epcs.add(epc_class)
            for quantity_element in event.get(
                "outputQuantityList",
            ) or []:
                epc_class=quantity_element.get("epcClass")
                if epc_class is not None:
                    output_epcs.add(epc_class)

            # input -> output
            if (
                direction in {"forward","both"}
                and current_epc in input_epcs
            ):
                related_epcs.update(output_epcs)

            # output -> input
            if (
                direction in {"backward","both"}
                and current_epc in output_epcs
            ):
                related_epcs.update(input_epcs)

        elif event_type=="TransactionEvent":
            # TransactionEvent는 객체 간 물리적 변환이나 포함 관계를
            # 직접 표현하지 않으므로, 기본적으로 새로운 EPC로 확장하지 않습니다.
            pass
        elif event_type=="ObjectEvent":
            # ObjectEvent 역시 객체 자체의 상태나 관찰을 표현하므로
            # 다른 EPC로 탐색을 확장하지 않습니다.
            pass

        related_epcs.discard(current_epc)
        related_epcs.discard(None)
        return related_epcs

    def _trace_events(self,
            epc:str,
            direction:Literal[
                "forward",
                "backward"
            ],
            max_depth:int=5
        )->list[dict[str]]:
        """
        하나의 방향(forward/backward)으로만 이력을 탐색합니다.
        """
        queue=deque() 
        queue.append((epc,0,None)) # (epc,current_depth,current_time)
        visited_states:set[tuple[str,str|None]]=set()
        visited_events:set[str]=set()
        traced_events:list[dict[str,Any]]=[]

        while queue:
            current_epc,current_depth,current_time=queue.popleft()
            current_state=(
                current_epc,
                current_time,
            )
            if current_state in visited_states:
                continue
            visited_states.add(current_state)
            current_events=self.find_events_by_epc(
                epc=current_epc,
            )
            current_events.sort(
                key=lambda event:event.get("eventTime",""),
                reverse=direction=="backward",
            )
            for event in current_events:
                event_time=event.get("eventTime")
                if (
                    current_time is not None
                    and event_time is not None
                ):
                    if (
                        direction=="forward"
                        and event_time<current_time
                    ):
                        continue
                    if (
                        direction=="backward"
                        and event_time>current_time
                    ):
                        continue
                event_id=event.get("eventID")

                if event_id not in visited_events:
                    visited_events.add(event_id)
                    traced_events.append(event)

                if (
                    max_depth is not None
                    and current_depth>=max_depth
                ):
                    continue

                related_epcs=self._get_related_epcs(
                    event=event,
                    current_epc=current_epc,
                    direction=direction,
                )

                for related_epc in related_epcs:
                    next_state=(
                        related_epc,
                        event_time,
                    )
                    if next_state in visited_states:
                        continue
                    queue.append(
                        (
                            related_epc,
                            current_depth+1,
                            event_time,
                        )
                    )
        return traced_events

    def find_trace_events(self,
            epc:str,
            direction:Literal[
                "backward",
                "forward",
                "both",
            ]="both",
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
            both:
                forward와 backward 탐색을 각각 수행한 뒤, 중복 이벤트를 제거하여 반환합니다.
        
        Return:
            Traced EPCIS Event list
        """
        if direction=="forward":
            return self._trace_events(
                epc=epc,
                direction="forward",
                max_depth=max_depth,
            )

        if direction=="backward":
            return self._trace_events(
                epc=epc,
                direction="backward",
                max_depth=max_depth,
            )

        forward_events=self._trace_events(
            epc=epc,
            direction="forward",
            max_depth=max_depth,
        )

        backward_events=self._trace_events(
            epc=epc,
            direction="backward",
            max_depth=max_depth,
        )

        traced_events:list[dict[str,Any]]=[]
        visited_event_ids:set[str]=set()
        for event in forward_events+backward_events:
            event_id=event.get("eventID")
            if event_id is None:
                raise ValueError(
                    "추적 대상 이벤트에 eventID가 없습니다."
                )
            if event_id in visited_event_ids:
                continue
            visited_event_ids.add(event_id)
            traced_events.append(event)
        return traced_events