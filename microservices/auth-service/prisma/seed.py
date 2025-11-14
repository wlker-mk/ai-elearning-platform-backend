#!/usr/bin/env python
"""
Seed script for auth-service
"""
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()
    
    print(f"🌱 Seeding auth-service...")
    
    # Add your seed data here
    
    print("✅ Seed completed!")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
