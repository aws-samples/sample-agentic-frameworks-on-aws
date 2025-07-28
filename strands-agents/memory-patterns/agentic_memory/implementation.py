from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from agentic_memory.base import BaseCheckPointer,BaseEpisodicStore, BaseLongTermStore

class CheckPointerInMemory(BaseCheckPointer):
    """In-memory implementation storing multiple checkpoints per session"""
    def __init__(self):
        self.checkpointer: Dict[str, List[Dict]] = defaultdict(list)
    
    def put(self, session_id: str, value: Any):
        """Append new checkpoint with timestamp"""
        self.checkpointer[session_id].append({
            "v": 1,
            "ts": datetime.now(timezone.utc).isoformat(),
            "value": value
        })
    
    def get(self, session_id: str) -> Optional[List[Dict]]:
        """Retrieve all checkpoints for session"""
        return self.checkpointer.get(session_id)


class EpisodicStoreFile(BaseEpisodicStore):
    """File-based implementation preserving original timestamps"""
    def __init__(self, storage_dir: str = "auto_service_records"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _get_file_path(self, key: Tuple) -> str:
        safe_key = [str(k).replace(os.sep, "_") for k in key]
        file_path = os.path.join(self.storage_dir ,"_".join(safe_key) + ".json")
        return file_path
    
    def put(self, key: Tuple, value: Any):
        """Append value with original timestamp"""
        file_path = self._get_file_path(key)
        history = []
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            "v": 1,
            "value": value
        })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    
    def get(self, key: Tuple) -> Optional[List[Dict]]:
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_keys(self) -> list:
        keys = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                base = filename[:-5]
                parts = base.split("_")
                if len(parts) >= 2:
                    customer_id = "_".join(parts[:2])
                    vin = parts[2]
                    keys.append((customer_id, vin))
        return keys

class LongTermStoreFile(BaseLongTermStore):
    """File-based implementation storing all VINs in a single JSON file with multiple issues per VIN"""
    def __init__(self, storage_file: str = "long_term_store/all_vins.json"):
        self.storage_file = storage_file
        dir_name = os.path.dirname(self.storage_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def put(self, key: str, value: dict):
        data = {}
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        # If VIN exists, append to service_history list
        if key in data:
            existing = data[key]
            if "service_history" not in existing:
                existing["service_history"] = []
            # Append new detailed issue summary to service_history
            existing["service_history"].append({
                "issue_summary": value.get("issue_summary", ""),
                "resolution": value.get("resolution", ""),
                "service_engineer": value.get("service_engineer", ""),
                "service_date": value.get("service_date", ""),
                **{k: v for k, v in value.items() if k not in ["issue_summary", "resolution", "service_engineer", "service_date"]}
            })
            data[key] = existing
        else:
            if type(value) == list: #To avoid er due to response formatted as list
                for i in value:
                    # New VIN entry with vehicle metadata and service_history list
                    data[key] = {
                        "service_history": [{
                            "issue_summary": i.get("issue_summary", ""),
                            "resolution": i.get("resolution", ""),
                            "service_engineer": i.get("service_engineer", ""),
                            "service_date": i.get("service_date", ""),
                            **{k: v for k, v in i.items() if k not in ["issue_summary", "resolution", "service_engineer", "service_date"]}
                        }]
                    }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def get(self, key: str) -> Optional[dict]:
        if not os.path.exists(self.storage_file):
            return None
        with open(self.storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(key)

    def search(self, query: str) -> List[dict]:
        results = []
        if not os.path.exists(self.storage_file):
            return results
        with open(self.storage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for vin, entry in data.items():
            if query.lower() in json.dumps(entry).lower():
                results.append(entry)
        return results