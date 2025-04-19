# # domain/sync_engine.py

# from typing import Dict, Any

# class SyncEngine:
#     def __init__(self, room_id: str):
#         self.room_id = room_id
#         self.document = ""  # Simplified shared state
#         self.users = set()

#     def apply_user_edit(self, user_id: str, edit_payload: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Apply the edit and return the result to broadcast.
#         For simplicity, assume edit_payload = {"action": "insert", "char": "a", "pos": 5}
#         """
#         self.users.add(user_id)
#         action = edit_payload.get("action")
#         if action == "insert":
#             char = edit_payload["char"]
#             pos = edit_payload["pos"]
#             self.document = self.document[:pos] + char + self.document[pos:]
#         elif action == "delete":
#             pos = edit_payload["pos"]
#             self.document = self.document[:pos] + self.document[pos+1:]
#         return {
#             "type": "edit",
#             "user_id": user_id,
#             "payload": edit_payload,
#             "document_snapshot": self.document
#         }

#     def remove_user(self, user_id: str):
#         self.users.discard(user_id)

#     def get_active_users(self):
#         return list(self.users)


from typing import Dict, Any
from models.RGA import RGA
from uuid import uuid4

class SyncEngine:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.document = ""  # Shared document state
        self.rga = RGA()
        self.users = set()
        self.cursor_positions: Dict[str, int] = {} 

    def apply_user_edit(self, user_id: str, edit_payload: Dict[str, Any]) -> Dict[str, Any]:
        print("PYLOAD",edit_payload)
        # action = edit_payload.get("action")
        # print("ACTION",action)
        # print(edit_payload)
        self.document = edit_payload.get("document_snapshot")
        # if action == "insert":
        #     char = edit_payload["char"]
        #     pos = edit_payload["pos"]
        #     self.document = self.document[:pos] + char + self.document[pos:]
        # elif action == "delete":
        #     pos = edit_payload["pos"]
        #     self.document = self.document[:pos] + self.document[pos+1:]


        # self.document=edit_payload['document_snapshot']
        # print("DOC",self.document)
        # return {
        #     "type": "edit",
        #     "user_id": user_id,
        #     "payload": edit_payload,
        #     "document_snapshot": self.document
        # }


        # action = edit_payload.get("action")
        # pos = edit_payload.get("pos")
        # char = edit_payload.get("char")

        # # Apply the edit to the CRDT
        # if action == "insert":
        #     self.rga.insert(pos, char)
        # elif action == "delete":
        #     self.rga.delete(pos)


        operations = edit_payload.get("operation", [])
    
        # Iterate over each operation and apply it to the CRDT
        # for operation in operations:
        #     # Handle insert operation
        #     if operation['type'] == 'insert':
        #         position = operation.get('position')
        #         text = operation.get('text')
        #         if position is not None and text is not None:
        #             self.rga.insert(position, text)
            
        #     # Handle delete operation
        #     elif operation['type'] == 'delete':
        #         position = operation.get('position')
        #         length = operation.get('length')
        #         if position is not None:
        #         # If the delete operation only requires position
        #             if length is not None:
        #                 self.rga.delete(position, length)  # If length is expected by your delete method
        #             else:
        #                 self.rga.delete(position)


        # existing_doc = self.rga.get_document()

        for operation in operations:
            if 'operation_id' not in operation:
                operation['operation_id'] = str(uuid4())
            # if operation['type'] == 'insert':
            #     pos = operation['position']
            #     text = operation['text']
                
            #     # Guard clause: if the text is already at the position, skip
            #     if existing_doc[pos:pos+len(text)] == text:
            #         continue
            #     self.rga.insert(pos, text)

            # elif operation['type'] == 'delete':
            #     # Optional: skip deletes if nothing to delete
            #     pos = operation['position']
            #     length = operation.get('length', 1)
            #     if pos >= len(existing_doc):
            #         continue
            #     self.rga.delete(pos, length)
            self.rga.apply_operation(operation)


        # Send the updated document state
        document_snapshot = self.document
        print("UPD",document_snapshot)
        return {
            "type": "edit",
            "user_id": user_id,
            "payload": {
                "operation": operations
            },
            "document_snapshot": document_snapshot
        }
    
    def update_cursor(self, user_id: str, cursor_position: int) -> Dict[str, Any]:
        self.cursor_positions[user_id] = cursor_position
        return {
            "type": "cursor",
            # "user_id": user_id,
            "cursor_position": self.cursor_positions
        }

    def get_snapshot(self):
        return self.document
    
    def get_cursor_positions(self):
        # print(cu)
        return self.cursor_positions
    
    def remove_user(self, user_id: str):
        self.users.discard(user_id)
        self.cursor_positions.pop(user_id, None)

    def get_active_users(self):
        return list(self.users)