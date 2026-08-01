from datetime import datetime
from typing import Any,Literal
from module import Neo4j_Interface

class OTG:
    """
    Object Traceability Graph
    """
    def __init__(self,graph_db:Neo4j_Interface):
        self.graph_db=graph_db

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

    def create_node_dict(self,
            node_id:str,
            node_type:Literal["class","instance","location"],
            **properties
        )->dict[str,Any]:
        """
        shape:
            {
                "node_id":value,
                "node_type":value,
                "properties":{key:value,...}
            }
        """
        return {
            "node_id":node_id,
            "node_type":node_type,
            "properties":properties
        }

    def create_edge_event_dict(self,
            src_id:str,
            dst_id:str,
            event_time:int,
            edge_type:Literal[
                "isLocatedIn",
                "isOwned",
                "isPossessed",
                "contains",
                "transformTo"
            ],
            **properties
        ):
        """
            shape:
                {
                    "src_id":value,
                    "dst_id":value,
                    "event_time":value,
                    "edge_type":value,
                    "properties":{key:value,...}
                }
        """
        return {
            "src_id":src_id,
            "dst_id":dst_id,
            "event_time":event_time,
            "edge_type":edge_type,
            "properties":properties
        }

    def transform_other_event_to_graph(self,
            event:dict
        ):
        """
        Transform ObjectEvent,TransactionEvent to graph
        """
        ### event time
        event_time=event.get("eventTime")
        event_time=self.convert_event_time_to_unix_timestmap(event_time=event_time) # unix timestamp

        ### set nodes, edge_events, objects
        nodes=[]
        edge_events=[]
        objects=set()

        ### check epcList and create node
        for epc in event.get("epcList",[]):
            node=self.create_node_dict(
                node_id=epc,
                node_type="instance"
            )
            nodes.append(node)
            objects.add(epc)

        ### check quantityList and create node
        for quantity_element in event.get("quantityList",[]):
            epc_class=quantity_element["epcClass"]
            quantity=quantity_element["quantity"]
            uom=quantity_element["uom"]
            properties={
                "quantity":quantity,
                "uom":uom
            }
            node=self.create_node_dict(
                node_id=epc_class,
                node_type="class",
                **properties
            )
            nodes.append(node)
            objects.add(epc_class)

        ### check readPoint and create edge_event
        read_point=event.get("readPoint")
        if read_point is not None:
            read_point_id=read_point.get("id")
            node=self.create_node_dict(
                node_id=read_point_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=read_point_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### check bizLocation and create edge_event
        biz_location=event.get("bizLocation")
        if (biz_location is not None) and (read_point!=biz_location):
            biz_location_id=biz_location.get("id")
            node=self.create_node_dict(
                node_id=biz_location_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=biz_location_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)
        return {
            "nodes":nodes,
            "edge_events":edge_events
        }

    def transform_aggregation_event_to_graph(self,
            event:dict
        ):
        """
        Transform AggregationEvent to graph
        """
        ### event time
        event_time=event.get("eventTime")
        event_time=self.convert_event_time_to_unix_timestmap(event_time=event_time) # unix timestamp

        ### set nodes, edge_events, objects
        nodes=[]
        edge_events=[]
        objects=set()

        ### check parentID and create node
        parent_id=event.get("parentID")
        if parent_id is not None:
            node=self.create_node_dict(
                node_id=parent_id,
                node_type="instance" # AggregationEvent의 parentID는 원칙적으로 instance 
            )
            nodes.append(node)

        ### check childEPCs and create node
        for child_epc in event.get("childEPCs",[]):
            node=self.create_node_dict(
                node_id=child_epc,
                node_type="instance"
            )
            nodes.append(node)
            objects.add(child_epc)

        ### check childQuantityList and create node
        for child_quantity_element in event.get("childQuantityList",[]):
            epc_class=child_quantity_element["epcClass"]
            quantity=child_quantity_element["quantity"]
            uom=child_quantity_element["uom"]
            properties={
                "quantity":quantity,
                "uom":uom
            }
            node=self.create_node_dict(
                node_id=epc_class,
                node_type="class",
                **properties
            )
            nodes.append(node)
            objects.add(epc_class)

        ### check readPoint and create edge_event
        read_point=event.get("readPoint")
        if read_point is not None:
            read_point_id=read_point.get("id")
            node=self.create_node_dict(
                node_id=read_point_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=read_point_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### check bizLocation and create edge_event
        biz_location=event.get("bizLocation")
        if (biz_location is not None) and (read_point!=biz_location):
            biz_location_id=biz_location.get("id")
            node=self.create_node_dict(
                node_id=biz_location_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=biz_location_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### create contains edge_event (parent -> child)
        bizStep=event.get("bizStep")
        properties={
            "bizStep":bizStep
        }
        for obj in list(objects):
            edge_event=self.create_edge_event_dict(
                src_id=parent_id,
                dst_id=obj,
                event_time=event_time,
                edge_type="contains",
                **properties
            )
            edge_events.append(edge_event)

        return {
            "nodes":nodes,
            "edge_events":edge_events
        }

    def transform_transformation_event_to_graph(self,
            event:dict
        ):
        """
        Transform TransformationEvent to graph
        """
        ### event time
        event_time=event.get("eventTime")
        event_time=self.convert_event_time_to_unix_timestmap(event_time=event_time) # unix timestamp

        ### set nodes, edge_events, objects
        nodes=[]
        edge_events=[]
        objects=set()
        input_objects=set()
        output_objects=set()

        ### check inputEPCList and create node
        for input_epc in event.get("inputEPCList",[]):
            node=self.create_node_dict(
                node_id=input_epc,
                node_type="instance"
            )
            nodes.append(node)
            input_objects.add(input_epc)
            objects.add(input_epc)

        ### check inputQuantityList and create node
        for input_quantity_element in event.get("inputQuantityList",[]):
            epc_class=input_quantity_element["epcClass"]
            quantity=input_quantity_element["quantity"]
            uom=input_quantity_element["uom"]
            properties={
                "quantity":quantity,
                "uom":uom
            }
            node=self.create_node_dict(
                node_id=epc_class,
                node_type="class",
                **properties
            )
            nodes.append(node)
            input_objects.add(epc_class)
            objects.add(epc_class)

        ### check outputEPCList and create node
        for output_epc in event.get("outputEPCList",[]):
            node=self.create_node_dict(
                node_id=output_epc,
                node_type="instance"
            )
            nodes.append(node)
            output_objects.add(output_epc)
            objects.add(output_epc)

        ### check outputQuantityList and create node
        for output_quantity_element in event.get("outputQuantityList",[]):
            epc_class=output_quantity_element["epcClass"]
            quantity=output_quantity_element["quantity"]
            uom=output_quantity_element["uom"]
            properties={
                "quantity":quantity,
                "uom":uom
            }
            node=self.create_node_dict(
                node_id=epc_class,
                node_type="class",
                **properties
            )
            nodes.append(node)
            output_objects.add(epc_class)
            objects.add(epc_class)

        ### check readPoint and create edge_event
        read_point=event.get("readPoint")
        if read_point is not None:
            read_point_id=read_point.get("id")
            node=self.create_node_dict(
                node_id=read_point_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=read_point_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### check bizLocation and create edge_event
        biz_location=event.get("bizLocation")
        if (biz_location is not None) and (read_point!=biz_location):
            biz_location_id=biz_location.get("id")
            node=self.create_node_dict(
                node_id=biz_location_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=biz_location_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### create transformTo edge_event (input -> output)
        for input_obj in list(input_objects):
            for output_obj in list(output_objects):
                edge_event=self.create_edge_event_dict(
                    src_id=input_obj,
                    dst_id=output_obj,
                    event_time=event_time,
                    edge_type="transformTo",
                )
                edge_events.append(edge_event)
        return {
            "nodes":nodes,
            "edge_events":edge_events
        }

    def transform_association_event_to_graph(self,
            event:dict
        ):
        """
        Transform AssociationEvent to graph
        """
        ### event time
        event_time=event.get("eventTime")
        event_time=self.convert_event_time_to_unix_timestmap(event_time=event_time) # unix timestamp

        ### set nodes, edge_events, objects
        nodes=[]
        edge_events=[]
        objects=set()

        ### check parentID and create node
        parent_id=event.get("parentID")
        if parent_id is not None:
            node=self.create_node_dict(
                node_id=parent_id,
                node_type="instance" # AssociationEvent의 parentID는 원칙적으로 instance 
            )
            nodes.append(node)

        ### check childEPCs and create node
        for child_epc in event.get("childEPCs",[]):
            node=self.create_node_dict(
                node_id=child_epc,
                node_type="instance"
            )
            nodes.append(node)
            objects.add(child_epc)

        ### check childQuantityList and create node
        for child_quantity_element in event.get("childQuantityList",[]):
            epc_class=child_quantity_element["epcClass"]
            quantity=child_quantity_element["quantity"]
            uom=child_quantity_element["uom"]
            properties={
                "quantity":quantity,
                "uom":uom
            }
            node=self.create_node_dict(
                node_id=epc_class,
                node_type="class",
                **properties
            )
            nodes.append(node)
            objects.add(epc_class)

        ### check readPoint and create edge_event
        read_point=event.get("readPoint")
        if read_point is not None:
            read_point_id=read_point.get("id")
            node=self.create_node_dict(
                node_id=read_point_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=read_point_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### check bizLocation and create edge_event
        biz_location=event.get("bizLocation")
        if (biz_location is not None) and (read_point!=biz_location):
            biz_location_id=biz_location.get("id")
            node=self.create_node_dict(
                node_id=biz_location_id,
                node_type="location"
            )
            nodes.append(node)
            for obj in list(objects):
                edge_event=self.create_edge_event_dict(
                    src_id=obj,
                    dst_id=biz_location_id,
                    event_time=event_time,
                    edge_type="isLocatedIn"
                )
                edge_events.append(edge_event)

        ### create isAssociatedWith edge_event (parent -> child)
        bizStep=event.get("bizStep")
        properties={
            "bizStep":bizStep
        }
        for obj in list(objects):
            edge_event=self.create_edge_event_dict(
                src_id=parent_id,
                dst_id=obj,
                event_time=event_time,
                edge_type="isAssociatedWith",
                **properties
            )
            edge_events.append(edge_event)

        return {
            "nodes":nodes,
            "edge_events":edge_events
        }

    def transform_epcis_events_to_graph(self,
            events:list[dict]
        ):
        """
        Transform EPCIS Events to graph
        """
        nodes=[]
        edge_events=[]
        for event in events:
            event_type=event.get("type")
            match event_type:
                case "ObjectEvent"|"TransactionEvent":
                    graph_elements=self.transform_other_event_to_graph(event=event)
                    nodes+=graph_elements["nodes"]
                    edge_events+=graph_elements["edge_events"]
                case "AggregationEvent":
                    graph_elements=self.transform_aggregation_event_to_graph(event=event)
                    nodes+=graph_elements["nodes"]
                    edge_events+=graph_elements["edge_events"]
                case "TransformationEvent":
                    graph_elements=self.transform_transformation_event_to_graph(event=event)
                    nodes+=graph_elements["nodes"]
                    edge_events+=graph_elements["edge_events"]
                case "AssociationEvent":
                    graph_elements=self.transform_association_event_to_graph(event=event)
                    nodes+=graph_elements["nodes"]
                    edge_events+=graph_elements["edge_events"]
        return {
            "nodes":nodes,
            "edge_events":edge_events
        }