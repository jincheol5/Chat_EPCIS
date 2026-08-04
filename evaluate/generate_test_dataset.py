import argparse
from datetime import datetime,timedelta,timezone
from module import MongoDB_Interface

def generate_nested_aggregation_events(
        n_aggregations:int
    )->list[dict]:
    """
    ADD 이벤트만 사용하여 중첩 Aggregation 데이터를 생성합니다.

    object-0
        -> container-1
            -> container-2
                -> ...
    """
    if n_aggregations<1:
        raise ValueError("n_aggregations는 1 이상이어야 합니다.")

    base_time=datetime(2026,1,1,tzinfo=timezone.utc,)
    events:list[dict]=[]
    for level in range(1,n_aggregations+1):
        child_id=(
            "object_0"
            if level==1
            else f"container_{level-1}"
        )
        parent_id=f"container_{level}"
        event={
            "type": "AggregationEvent",
            "eventTime": (
                base_time+timedelta(seconds=level-1)
            ).isoformat(timespec="milliseconds"),
            "eventTimeZoneOffset":"+00:00",
            "eventID":f"eventID_{level}",
            "action":"ADD",
            "bizStep":"loading",
            "parentID":parent_id,
            "childEPCs":[child_id],
        }
        events.append(event)
    return events

def generate_nested_transformation_events(
        n_transformations:int
    )->list[dict]:
    """
    """

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--event_type",type=str,choices=["aggregation","transformation"],default=f"aggregation")
    parser.add_argument("--n_relation",type=int,default=1000)
    args=parser.parse_args()
    match args.event_type:
        case "aggregation":
            events=generate_nested_aggregation_events(n_aggregations=args.n_relation)
        case "transformation":
            events=generate_nested_transformation_events(n_transformations=args.n_relation)
    mongodb_interface=MongoDB_Interface(isEvaluated=True)
    mongodb_interface.insert_data_list(data_list=events,data_type="event")
    print(f"Success to insert events!")
    mongodb_interface.disconnect_db()
