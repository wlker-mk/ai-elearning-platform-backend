from typing import List, Optional, Dict, Any
from prisma import Prisma

class EmailService:
    def __init__(self):
        self.db = Prisma()
    
    async def connect(self):
        await self.db.connect()
    
    async def disconnect(self):
        await self.db.disconnect()
    
    # Add your service methods here
