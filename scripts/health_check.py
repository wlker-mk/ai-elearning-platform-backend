#!/usr/bin/env python3
import requests
import sys

services = {
    'auth-service': 8001,
    'user-service': 8002,
    'courses-service': 8003,
    'quizzes-service': 8004,
    'bookings-service': 8005,
    'payments-service': 8006,
    'notifications-service': 8007,
    'webinars-service': 8008,
    'gamification-service': 8009,
    'chatbot-service': 8010,
    'analytics-service': 8011,
    'communications-service': 8012,
    'search-service': 8013,
    'storage-service': 8014,
    'security-service': 8015,
    'monitoring-service': 8016,
    'ai-gateway': 8017,
    'cache-service': 8018,
    'api-gateway': 8019,
    'i18n-service': 8020,
    'sponsors-service': 8021,
}

def check_health():
    failed = []
    
    for service, port in services.items():
        try:
            response = requests.get(f'http://localhost:{port}/api/health/', timeout=5)
            if response.status_code == 200:
                print(f"✅ {service}: OK")
            else:
                print(f"❌ {service}: FAILED (status {response.status_code})")
                failed.append(service)
        except Exception as e:
            print(f"❌ {service}: FAILED ({str(e)})")
            failed.append(service)
    
    if failed:
        print(f"\n❌ {len(failed)} services failed")
        sys.exit(1)
    else:
        print(f"\n✅ All services are healthy!")
        sys.exit(0)

if __name__ == '__main__':
    check_health()
