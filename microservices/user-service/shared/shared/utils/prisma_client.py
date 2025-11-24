
from prisma import Prisma
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

_prisma_client: Optional[Prisma] = None
_lock = asyncio.Lock()

async def get_prisma_client() -> Prisma:
    """Get or create Prisma client singleton with proper locking"""
    global _prisma_client
    
    async with _lock:
        if _prisma_client is None:
            _prisma_client = Prisma()
            logger.info("Prisma client instance created")
        
        if not _prisma_client.is_connected():
            await _prisma_client.connect()
            logger.info("Prisma client connected to database")
    
    return _prisma_client

async def disconnect_prisma():
    """Disconnect Prisma client"""
    global _prisma_client
    
    async with _lock:
        if _prisma_client and _prisma_client.is_connected():
            await _prisma_client.disconnect()
            logger.info("Prisma client disconnected")
            _prisma_client = None
