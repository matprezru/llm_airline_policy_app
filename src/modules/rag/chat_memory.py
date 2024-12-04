from typing import Dict, List, Optional

class ChatMemory:
    """
    Custom class to store chat memory and make it persistent between queries via API.
    """
    def __init__(self, max_memory: int = 3):
        """
        Initialize custom class to store chat memory and make it persistent between queries via API.

        Args:
            max_memory (int, optional): Max number of recent chat interactions to store in memory. Defaults to 3.
        """
        self.chat_memory = []
        self.max_memory = max_memory
        
    def add_memory(self, question, answer):
        """
        Add question-answer pair to chat memory
        """
        self.chat_memory.append({"question": question, "answer": answer})
        if len(self.chat_memory) > self.max_memory:
            self.chat_memory.pop(0)
    
    def get_memory(self) -> List[Optional[Dict]]:
        """
        Retrieve recent chat history in list format
        """
        return self.chat_memory