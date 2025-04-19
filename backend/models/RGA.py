from collections import deque
from uuid import uuid4
from typing import List, Dict

class RGA:
    def __init__(self):
        self.characters = deque()  # This will store the characters in a list-like structure
        self.operation_history = []  # List of operations applied
        self.document_snapshot = ""
        self.clock = 0  # Logical clock to track operations
        self.applied_operations = set()  # To track applied operations and avoid duplicates

    def insert(self, pos: int, char: str) -> str:
        """
        Insert a character at a specific position.
        """
        # self.characters.insert(pos, char)

        chars_to_insert = list(char)
        
        # Insert characters into the deque at the specified position
        for char in chars_to_insert:
            self.characters.insert(pos, char)
            pos += 1

        self.clock += 1
        operation_id = str(uuid4())
        self.operation_history.append(('insert', pos, char, operation_id,self.clock))
        return operation_id

    def delete(self, pos: int, length: int = 1) -> str:
        """
        Delete a character at a specific position.
        """
        deleted_chars = []
        for _ in range(length):
            if pos < len(self.characters):
                char = self.characters[pos]
                self.characters.remove(char)
                deleted_chars.append(char)
        # self.clock += 1
        operation_id = str(uuid4())
        self.operation_history.append(('delete', pos, ''.join(deleted_chars), operation_id,self.clock))
        return operation_id

    def get_document(self) -> str:
        """
        Get the current document state as a string.
        """
        return ''.join(self.characters)

    def apply_operation(self, operation: Dict) -> None:
        """
        Apply a received operation to the CRDT.
        """
        # Use operation_id to check if operation has already been applied
        operation_id = operation['operation_id']
        if operation_id in self.applied_operations:
            return  # Skip the operation if it has already been applied

        action = operation['type']
        pos = operation['position']
        char = operation.get('text', None)
        # clock = operation.get('clock', None)

        # if clock is not None and clock <= self.clock:
        #     # If the operation has already been applied, skip it
        #     return

        if action == 'insert':
            self.insert(pos, char)
        elif action == 'delete':
            self.delete(pos)

        # Add operation to the applied set
        # self.applied_operations.add(operation_id)
        self.document_snapshot = self.get_document()
        print("RGA DOC:",self.document_snapshot)
        # self.clock += 1  # Update the logical clock after applying an operation

    def get_operations(self) -> List[Dict]:
        return self.operation_history
