import logging
import uuid

class TraceIDFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = str(uuid.uuid4())
        return True
