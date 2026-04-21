import aiosqlite
import json
import logging
import os
import shutil
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class Buffer:
    def __init__(self, path: str = 'buffer.db', mx_records: int = 5000, mx_memory_mb: int = 50):
        self.path = path
        self.mx_records = mx_records
        self.mx_memory_mb = mx_memory_mb
