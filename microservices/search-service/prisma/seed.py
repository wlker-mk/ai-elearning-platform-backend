#!/usr/bin/env python
"""
Seed script for search-service
"""
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()
    
    print(f"🌱 Seeding search-service...")
    
    # Add your seed data here
    
    print("✅ Seed completed!")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
