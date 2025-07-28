import uuid
from typing import Any, Dict, List, Optional, Tuple
from agentic_memory.base import BaseCheckPointer,BaseEpisodicStore, BaseLongTermStore, BaseRetriever

class MultiTierMemoryOrchestrator:
    def __init__(self, checkpointer: BaseCheckPointer, 
                 episodic: BaseEpisodicStore, 
                 longterm: BaseLongTermStore,
                 semantic: BaseRetriever):
        self.checkpointer = checkpointer
        self.episodic = episodic
        self.longterm = longterm
        self.semantic = semantic
    
    def create_session(self) -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())
    
    def get_hierarchical_memory(self,session_id: str,key: Tuple) -> Dict[str, Any]:
        """
        Gets consolidated context from all memory tiers with source identification
        Returns dictionary with keys:
        - 'short_term': Current session data
        - 'episodic': Historical interactions for key
        - 'long_term': Aggregated knowledge for key
        """
        context = {
            "short_term": [],
            "episodic": [],
            "long_term": None
        }
        
        # 1. Short-term memory (current session)
        if checkpoints := self.checkpointer.get(session_id):
            context["short_term"] = [entry["value"] for entry in checkpoints]
        
        # 2. Episodic memory (historical interactions)
        if episodic_data := self.episodic.get(key):
            context["episodic"] = [entry["value"] for entry in episodic_data]
        
        # 3. Long-term memory (aggregated knowledge)
        entity_key = key[0] if isinstance(key, tuple) else key
        if longterm_data := self.longterm.get(entity_key):
            context["long_term"] = longterm_data
        
        #print(context)
        return context

    def search_semantic_store(self,issue_description: Optional[str] = None,make: Optional[str] = None,model: Optional[str] = None) -> Dict[str, Any]:
        """
        Gets consolidated context from all memory tiers with source identification
        Returns dictionary with keys from knowledge_bases: Matching resolutions from other vehicles
        """
        context = {"knowledge_bases": []}
        
        # Similar issues from other vehicles
        context["knowledge_bases"] = self.semantic.search(issue=issue_description,make=make,model=model)
        return context

    def end_session(self, session_id: str, key: Tuple):
        """Transfer data to episodic memory and clear short-term"""
        if checkpoints := self.checkpointer.get(session_id):
            for checkpoint in checkpoints:
                self.episodic.put(key, checkpoint["value"])
            # Clear short-term memory
            self.checkpointer.checkpointer[session_id] = []