from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional, Tuple


class BaseCheckPointer(ABC):

    @abstractmethod
    def put(self, session_id: str, value: Any):
        pass
    
    @abstractmethod
    def get(self, session_id: str) -> Optional[List[Dict]]:
        pass

class BaseEpisodicStore(ABC):

    @abstractmethod
    def put(self, key: Tuple, value: Any, timestamp: str):
        pass
    
    @abstractmethod
    def get(self, key: Tuple) -> Optional[List[Dict]]:
        """Retrieve all events for composite key"""
        pass

    @abstractmethod
    def list_keys(self) -> List[Tuple]:
        """
        List all (customer_id, VIN) keys for which episodic memory exists.
        For file-based implementations, this should enumerate files in the storage directory.
        """
        pass


class BaseLongTermStore(ABC):
    @abstractmethod
    def put(self, key: str, value: Any):
        pass
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Any]:
        pass

class BaseRetriever(ABC):
    @abstractmethod
    def build(self):
        pass
    
    @abstractmethod
    def search(self, make: Optional[str]=None, model: Optional[str]=None, issue: Optional[str]=None) -> List[Dict[str, Any]]:
        pass


class BaseConsolidator(ABC):
    """
    Abstract base class for consolidating episodic memory into long-term memory.
    Subclasses must implement the LLM summarization method.
    """

    @abstractmethod
    def consolidate(self, key: Tuple) -> str:
        pass