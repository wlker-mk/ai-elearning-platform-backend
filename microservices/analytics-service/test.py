import asyncio
import os
from dotenv import load_dotenv
from prisma import Prisma

# 🔹 Charger les variables depuis le fichier .env
load_dotenv()

async def main():
    # 🔍 Vérifions d'abord la variable :
    print("DATABASE_URL =", os.getenv("DATABASE_URL"))

    db = Prisma()
    await db.connect()
    print("✅ Prisma client connecté avec succès")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
