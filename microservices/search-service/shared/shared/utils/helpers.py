from typing import Any, Dict
import uuid

def generate_unique_id() -> str:
    return str(uuid.uuid4())

def format_response(data: Any, message: str = '', status: str = 'success') -> Dict:
    return {
        'status': status,
        'message': message,
        'data': data
    }
