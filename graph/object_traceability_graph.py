import networkx as nx
from datetime import datetime

class OTG:
    def __init__(self):
        self.graph=nx.MultiDiGraph() # 동일한 두 노드 사이에 여러 개의 방향성 엣지를 저장 가능, edge=(src,dst,key) 3가지 값으로 식별

    def convert_event_time_to_unix_timestmap(self,
            event_time:str
        ):
        """
        밀리초(ms) 단위 unix timestamp로 변환
        """
        timestamp_ms=int(
            datetime.fromisoformat(
                event_time
            ).timestamp()*1000
        )
        return timestamp_ms

    def add_temporal_edge(self,
            src:str,
            dst:str,
            relation:str,
            event_time:int
        ):
        """
        동일한 source-target-relation 엣지가 존재하면
        중복되지 않은 event_time만 event_times에 추가합니다.

        존재하지 않으면 새로운 엣지를 생성합니다.
        """
        if self.graph.has_edge(src,dst,key=relation):
            event_times=self.graph.edges[
                src,
                dst,
                relation,
            ].setdefault(
                "event_times",
                [],
            )
            if event_time not in event_times:
                event_times.append(event_time)
        else:
            self.graph.add_edge(
                src,
                dst,
                key=relation,
                relation=relation,
                event_times=[event_time],
            )

    def transform_event_to_graph(self,
            event:dict
        ):
        """
        """
        ### event time
        event_time=event.get("eventTime")
        event_time=self.convert_event_time_to_unix_timestmap(event_time=event_time) # unix timestamp

        objects=set()
        ### epcList
        for epc in event.get("epcList",[]):
            self.graph.add_node(
                epc,
                node_type="instance",
            )
            objects.add(epc)

        ### quantityList
        for quantity_element in event.get("quantityList",[]):
            self.graph.add_node(
                quantity_element["epcClass"],
                node_type="class",
            )
            objects.add(quantity_element["epcClass"])

        ### readPoint
        read_point=event.get("readPoint")
        if read_point is not None:
            read_point_id=read_point.get("id")
            self.graph.add_node(
                read_point_id,
                node_type="location",
            )
            for obj in list(objects):
                self.add_temporal_edge(
                    src=obj,
                    dst=read_point_id,
                    relation="isLocatedIn",
                    event_time=event_time
                )

        ### bizLocation
        biz_location=event.get("bizLocation")
        if biz_location is not None:
            biz_location_id=biz_location.get("id")
            self.graph.add_node(
                biz_location_id,
                node_type="location",
            )
            for obj in list(objects):
                self.add_temporal_edge(
                    src=obj,
                    dst=biz_location_id,
                    relation="isLocatedIn",
                    event_time=event_time
                )