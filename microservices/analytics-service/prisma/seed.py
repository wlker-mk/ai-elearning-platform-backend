# prisma/seed.py
import asyncio
from prisma import Prisma
from datetime import datetime, timedelta
import json

async def seed_analytics_data():
    prisma = Prisma()
    
    await prisma.connect()
    
    try:
        print("🌱 Seeding analytics data...")
        
        # Créer quelques course views
        await prisma.courseview.create_many([
            {
                'courseId': 'course_001',
                'userId': 'user_001',
                'ipAddress': '192.168.1.1',
                'userAgent': 'Mozilla/5.0...',
                'country': 'France',
                'city': 'Paris',
                'viewedAt': datetime.now() - timedelta(days=1)
            },
            {
                'courseId': 'course_002', 
                'userId': 'user_002',
                'ipAddress': '192.168.1.2',
                'userAgent': 'Mozilla/5.0...',
                'country': 'USA',
                'city': 'New York',
                'viewedAt': datetime.now() - timedelta(hours=5)
            }
        ])
        
        # Créer des analytics vidéo
        await prisma.videoanalytics.create({
            'lessonId': 'lesson_001',
            'studentId': 'student_001',
            'totalWatchTime': 3600,
            'completionRate': 0.85,
            'pauseCount': 3,
            'rewindCount': 2
        })
        
        # Créer des logs de recherche
        await prisma.searchlog.create({
            'query': 'machine learning',
            'userId': 'user_001',
            'resultsCount': 15,
            'clickedResult': 'course_003'
        })
        
        # Créer des activités utilisateur
        await prisma.useractivity.create({
            'userId': 'user_001',
            'eventType': 'login',
            'metadata': {'device': 'desktop', 'browser': 'chrome'}
        })
        
        print("✅ Analytics data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
    finally:
        await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(seed_analytics_data())