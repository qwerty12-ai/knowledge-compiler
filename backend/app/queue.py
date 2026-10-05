from bullmq import Queue

ANALYSIS_QUEUE_NAME = "analysis"

def get_analysis_queue() -> Queue:
    return Queue(ANALYSIS_QUEUE_NAME)