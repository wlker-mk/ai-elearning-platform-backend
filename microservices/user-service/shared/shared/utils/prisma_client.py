# shared/shared/utils/prisma_client.py
from prisma import Prisma
from typing import Optional

_prisma_client: Optional[Prisma] = None

async def get_prisma_client() -> Prisma:
    """Get or create Prisma client singleton"""
    global _prisma_client
    if _prisma_client is None:
        _prisma_client = Prisma()
    if not _prisma_client.is_connected():
        await _prisma_client.connect()
    return _prisma_client

async def disconnect_prisma():
    """Disconnect Prisma client"""
    global _prisma_client
    if _prisma_client and _prisma_client.is_connected():
        await _prisma_client.disconnect()