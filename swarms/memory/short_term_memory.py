from typing import List, Dict, Any
from collections import deque
import json
import logging

logger = logging.getLogger(__name__)

class ShortTermMemory:
    """
    Short-term memory implementation for swarm agents.
    Maintains recent context and interactions within a configurable window.
    """

    def __init__(self, max_entries: int = 50, max_age_seconds: int = 3600):
        """
        Initialize short-term memory.

        Args:
            max_entries: Maximum number of entries to keep in memory
            max_age_seconds: Maximum age of entries in seconds (1 hour default)
        """
        self.max_entries = max_entries
        self.max_age_seconds = max_age_seconds
        self.memory: deque = deque(maxlen=max_entries)
        self.entry_timestamps: deque = deque(maxlen=max_entries)

    def add_entry(self, entry_type: str, content: Dict[str, Any], agent_name: str = None):
        """
        Add an entry to short-term memory.

        Args:
            entry_type: Type of entry (e.g., 'agent_output', 'user_input', 'search_result')
            content: The content to store
            agent_name: Name of the agent that generated this entry
        """
        import time
        entry = {
            'timestamp': time.time(),
            'type': entry_type,
            'agent': agent_name,
            'content': content
        }

        self.memory.append(entry)
        self.entry_timestamps.append(entry['timestamp'])

        # Clean up old entries
        self._cleanup_old_entries()

        logger.debug(f"Added {entry_type} entry to short-term memory from {agent_name}")

    def get_recent_entries(self, limit: int = 10, entry_type: str = None) -> List[Dict[str, Any]]:
        """
        Get recent entries from memory.

        Args:
            limit: Maximum number of entries to return
            entry_type: Filter by entry type (optional)

        Returns:
            List of recent memory entries
        """
        entries = list(self.memory)

        if entry_type:
            entries = [e for e in entries if e['type'] == entry_type]

        return entries[-limit:]

    def get_context_for_agent(self, agent_name: str, limit: int = 5) -> str:
        """
        Get relevant context for a specific agent.

        Args:
            agent_name: Name of the agent
            limit: Maximum number of entries to include

        Returns:
            Formatted context string
        """
        # Get entries related to this agent or general context
        relevant_entries = []
        for entry in reversed(self.memory):
            if entry['agent'] == agent_name or entry['type'] in ['user_input', 'system_context']:
                relevant_entries.append(entry)
                if len(relevant_entries) >= limit:
                    break

        if not relevant_entries:
            return ""

        # Format context
        context_parts = []
        for entry in relevant_entries:
            context_parts.append(f"[{entry['type']}] {json.dumps(entry['content'], indent=2)}")

        return "\n\n".join(context_parts)

    def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memory for entries containing the query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching entries
        """
        matching_entries = []
        query_lower = query.lower()

        for entry in reversed(self.memory):
            content_str = json.dumps(entry['content']).lower()
            if query_lower in content_str:
                matching_entries.append(entry)
                if len(matching_entries) >= limit:
                    break

        return matching_entries

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current memory state.

        Returns:
            Dictionary with memory statistics
        """
        if not self.memory:
            return {'entries': 0, 'oldest_timestamp': None, 'newest_timestamp': None}

        return {
            'entries': len(self.memory),
            'oldest_timestamp': self.memory[0]['timestamp'],
            'newest_timestamp': self.memory[-1]['timestamp'],
            'entry_types': list(set(e['type'] for e in self.memory))
        }

    def clear_memory(self):
        """Clear all entries from memory."""
        self.memory.clear()
        self.entry_timestamps.clear()
        logger.info("Short-term memory cleared")

    def _cleanup_old_entries(self):
        """Remove entries that are too old."""
        import time
        current_time = time.time()

        while self.memory and (current_time - self.memory[0]['timestamp']) > self.max_age_seconds:
            self.memory.popleft()
            if self.entry_timestamps:
                self.entry_timestamps.popleft()

# Global memory instance
short_term_memory = ShortTermMemory()

def get_memory_instance() -> ShortTermMemory:
    """Get the global short-term memory instance."""
    return short_term_memory
