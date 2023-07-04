from uuid import uuid4

def generate_id():
    return ''.join(str(uuid4()).split('-'))

