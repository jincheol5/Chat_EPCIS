import time
import argparse
from module import MongoDB_Interface,Neo4j_Interface

"""
<< Test >> 
Evaluate dataset
"""
def evaluate_fn(**kwargs):
    match kwargs['evaluate_num']:
        case 1:
            """
            Evaluate.
            시간 측정: Object Traceability of EPCIS 
            """
            ### set dataset
            mongodb_interface=MongoDB_Interface(isEvaluated=True)
            source_epc=f"object_0"

            ### count time
            start_time=time.perf_counter()
            result=mongodb_interface.find_trace_events(
                epc=source_epc,
                direction="forward",
                max_depth=kwargs["max_depth"]
            )
            mongodb_interface.disconnect_db()
            end_time=time.perf_counter()
            elapsed_time=end_time-start_time
            print(f"반환 event 개수: {len(result)}")
            print(f"실행 시간: {elapsed_time:.6f}초")
            print(f"실행 시간: {elapsed_time * 1000:.3f}ms")

        case 2:
            """
            Evaluate.
            시간 측정: Object Traceability of Neo4j
            """
            ### set dataset
            neo4j_interface=Neo4j_Interface()
            source_epc=f"object_0"
            graph_id=f"test_graph"

            ### count time
            start_time=time.perf_counter()
            result=neo4j_interface.get_trace_events(
                node_id=source_epc,
                graph_id=graph_id,
                direction="forward",
                max_depth=kwargs["max_depth"]
            )
            neo4j_interface.disconnect_db()
            end_time=time.perf_counter()
            elapsed_time=end_time-start_time
            print(f"반환 event 개수: {len(result)}")
            print(f"실행 시간: {elapsed_time:.6f}초")
            print(f"실행 시간: {elapsed_time * 1000:.3f}ms")

if __name__=="__main__":
    """
    Execute test_fn
    """
    parser=argparse.ArgumentParser()
    parser.add_argument("--evaluate_num",type=int,default=1)
    parser.add_argument("--max_depth",type=int,default=10)
    args=parser.parse_args()
    evaluate_config={
        "evaluate_num":args.evaluate_num,
        "max_depth":args.max_depth
    }
    evaluate_fn(**evaluate_config)