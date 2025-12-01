"""
Memory Module - Conversation State Management
Maintains user preferences, conversation context, and session history
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)


class Memory(ABC):
    """
    Abstract base class for memory implementations.
    
    Extensibility: Implement this interface for different storage backends.
    Examples:
    - InMemoryStore (default): Fast, ephemeral storage for development
    - RedisMemory: Persistent, distributed storage for production
    - CosmosDBMemory: Azure Cosmos DB for global distribution
    """
    
    @abstractmethod
    def add_interaction(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """Record a conversation turn"""
        pass
    
    @abstractmethod
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update stored user preferences"""
        pass
    
    @abstractmethod
    def get_user_preferences(self) -> Dict[str, Any]:
        """Retrieve user preferences"""
        pass
    
    @abstractmethod
    def get_context_summary(self) -> str:
        """Get a summary of conversation context for LLM"""
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history"""
        pass
    
    @abstractmethod
    def clear(self):
        """Clear all stored data"""
        pass


class InMemoryStore(Memory):
    """
    Default in-memory storage for development and single-user scenarios.
    
    Stores:
    - Conversation history
    - User preferences (dietary restrictions, favorite cuisines, etc.)
    - Session metadata
    
    Limitations:
    - Not persistent across restarts
    - Not suitable for multi-user scenarios
    - No distributed access
    
    For production, use RedisMemory or CosmosDBMemory.
    """
    
    def __init__(self):
        """Initialize in-memory storage"""
        self.conversation_history: List[Dict[str, str]] = []
        self.user_preferences: Dict[str, Any] = {
            "dietary_restrictions": [],
            "favorite_cuisines": [],
            "disliked_ingredients": [],
            "cooking_skill_level": "intermediate",
            "time_constraints": None,  # max minutes
            "servings_preference": 4
        }
        self.session_metadata = {
            "session_start": datetime.now().isoformat(),
            "interaction_count": 0,
            "tools_used": []
        }
        
        logger.info("InMemoryStore initialized")
    
    def add_interaction(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """
        Record a conversation turn.
        
        Args:
            user_message: User's input
            assistant_response: Agent's response
            metadata: Additional interaction data (tool calls, etc.)
        """
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        self.session_metadata["interaction_count"] += 1
        
        # Auto-extract preferences from conversation
        self._auto_update_preferences(user_message, metadata)
        
        # Keep history manageable (last N turns)
        max_history = Config.MAX_CONVERSATION_HISTORY * 2  # user + assistant
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
        
        logger.debug(f"Interaction recorded. History length: {len(self.conversation_history)}")
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """
        Manually update user preferences.
        
        Args:
            preferences: Dict of preference updates
        """
        for key, value in preferences.items():
            if key in self.user_preferences:
                self.user_preferences[key] = value
                logger.info(f"Updated preference: {key} = {value}")
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get current user preferences"""
        return self.user_preferences.copy()
    
    def get_context_summary(self) -> str:
        """
        Generate a concise summary of user context for the LLM.
        
        Returns:
            String summary of preferences and constraints
        """
        prefs = self.user_preferences
        
        summary_parts = []
        
        if prefs["dietary_restrictions"]:
            summary_parts.append(f"Dietary restrictions: {', '.join(prefs['dietary_restrictions'])}")
        
        if prefs["favorite_cuisines"]:
            summary_parts.append(f"Favorite cuisines: {', '.join(prefs['favorite_cuisines'])}")
        
        if prefs["disliked_ingredients"]:
            summary_parts.append(f"Dislikes: {', '.join(prefs['disliked_ingredients'])}")
        
        if prefs["time_constraints"]:
            summary_parts.append(f"Time constraint: {prefs['time_constraints']} minutes max")
        
        summary_parts.append(f"Cooking skill: {prefs['cooking_skill_level']}")
        summary_parts.append(f"Typical servings: {prefs['servings_preference']}")
        
        if summary_parts:
            return "; ".join(summary_parts)
        
        return ""
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM"""
        # Return only role and content for LLM compatibility
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
    
    def clear(self):
        """Clear all stored data"""
        self.conversation_history.clear()
        self.user_preferences = {
            "dietary_restrictions": [],
            "favorite_cuisines": [],
            "disliked_ingredients": [],
            "cooking_skill_level": "intermediate",
            "time_constraints": None,
            "servings_preference": 4
        }
        logger.info("Memory cleared")
    
    def _auto_update_preferences(self, user_message: str, metadata: Dict = None):
        """
        Automatically extract and update preferences from conversation.
        
        Looks for dietary restrictions, cuisine mentions, time constraints, etc.
        """
        user_lower = user_message.lower()
        
        # Extract dietary restrictions
        dietary_keywords = {
            "vegetarian": ["vegetarian", "veggie"],
            "vegan": ["vegan"],
            "gluten-free": ["gluten-free", "gluten free", "celiac"],
            "dairy-free": ["dairy-free", "dairy free", "lactose"],
            "nut-free": ["nut-free", "no nuts"],
            "low-carb": ["low-carb", "keto"],
        }
        
        for restriction, keywords in dietary_keywords.items():
            if any(kw in user_lower for kw in keywords):
                if restriction not in self.user_preferences["dietary_restrictions"]:
                    self.user_preferences["dietary_restrictions"].append(restriction)
                    logger.info(f"Auto-detected dietary restriction: {restriction}")
        
        # Extract cuisine preferences
        cuisines = ["italian", "mexican", "asian", "mediterranean", "american", "indian", "thai"]
        for cuisine in cuisines:
            if cuisine in user_lower and cuisine not in self.user_preferences["favorite_cuisines"]:
                self.user_preferences["favorite_cuisines"].append(cuisine)
                logger.info(f"Auto-detected cuisine preference: {cuisine}")
        
        # Extract time constraints
        import re
        time_patterns = [
            r"under (\d+) min",
            r"less than (\d+) min",
            r"(\d+) min or less",
            r"quick.*?(\d+)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, user_lower)
            if match:
                minutes = int(match.group(1))
                self.user_preferences["time_constraints"] = minutes
                logger.info(f"Auto-detected time constraint: {minutes} minutes")
                break
        
        # Track tool usage from metadata
        if metadata and "tool_calls" in metadata:
            for tool_call in metadata["tool_calls"]:
                tool_name = tool_call.get("tool")
                if tool_name and tool_name not in self.session_metadata["tools_used"]:
                    self.session_metadata["tools_used"].append(tool_name)
    
    def get_session_metadata(self) -> Dict[str, Any]:
        """Get session statistics and metadata"""
        return {
            **self.session_metadata,
            "current_time": datetime.now().isoformat(),
            "history_length": len(self.conversation_history) // 2  # count turns, not messages
        }


# TODO: Implement RedisMemory for production
# Extensibility guide:
"""
class RedisMemory(Memory):
    def __init__(self, redis_url: str = None):
        import redis
        self.redis_url = redis_url or Config.REDIS_URL
        self.client = redis.from_url(self.redis_url)
        self.session_id = str(uuid.uuid4())  # or from user context
        
    def add_interaction(self, user_message, assistant_response, metadata=None):
        # Store in Redis with session_id as key prefix
        key = f"session:{self.session_id}:history"
        interaction = {
            "user": user_message,
            "assistant": assistant_response,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        self.client.rpush(key, json.dumps(interaction))
        self.client.expire(key, 86400)  # 24 hour TTL
        
    def get_conversation_history(self):
        key = f"session:{self.session_id}:history"
        history = self.client.lrange(key, 0, -1)
        return [json.loads(h) for h in history]
    
    # Implement other methods similarly
"""


# TODO: Implement CosmosDBMemory for Azure
# Extensibility guide:
"""
class CosmosDBMemory(Memory):
    def __init__(self):
        from azure.cosmos import CosmosClient
        
        self.client = CosmosClient(
            Config.COSMOS_DB_ENDPOINT,
            Config.COSMOS_DB_KEY
        )
        self.database = self.client.get_database_client("chef_ai")
        self.container = self.database.get_container_client("conversations")
        self.session_id = str(uuid.uuid4())
        
    def add_interaction(self, user_message, assistant_response, metadata=None):
        document = {
            "id": str(uuid.uuid4()),
            "session_id": self.session_id,
            "user_message": user_message,
            "assistant_response": assistant_response,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        self.container.create_item(document)
        
    # Implement other methods with Cosmos DB queries
"""


class MemoryFactory:
    """Factory for creating memory instances"""
    
    @staticmethod
    def create(memory_type: str = None) -> Memory:
        """
        Create a memory instance based on type.
        
        Args:
            memory_type: Type of memory ("in_memory", "redis", "cosmos_db")
            
        Returns:
            Memory instance
        """
        
        mem_type = memory_type or Config.MEMORY_BACKEND
        
        if mem_type == "in_memory":
            return InMemoryStore()
        
        elif mem_type == "redis":
            # TODO: Uncomment when RedisMemory is implemented
            # return RedisMemory()
            raise NotImplementedError(
                "Redis memory not yet implemented. "
                "See memory.py for implementation guide."
            )
        
        elif mem_type == "cosmos_db":
            # TODO: Uncomment when CosmosDBMemory is implemented
            # return CosmosDBMemory()
            raise NotImplementedError(
                "Cosmos DB memory not yet implemented. "
                "See memory.py for implementation guide."
            )
        
        else:
            raise ValueError(
                f"Unknown memory type: {mem_type}. "
                f"Valid options: in_memory, redis, cosmos_db"
            )
