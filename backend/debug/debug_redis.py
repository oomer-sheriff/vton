import redis
import os
import sys

# Try raw connection
try:
    print("Attempting raw connection to 127.0.0.1:6379...")
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    print(f"Ping: {r.ping()}")
    print("Raw connection SUCCESS")
except Exception as e:
    print(f"Raw connection FAILED: {e}")

# Try via Config
try:
    sys.path.append(os.getcwd())
    from app.core.config import settings
    print(f"\nSettings REDIS_HOST: {settings.REDIS_HOST}")
    print(f"Settings BROKER_URL: {settings.CELERY_BROKER_URL}")
    
    from app.core.celery_app import celery_app
    with celery_app.connection() as conn:
        print("Celery Connection Status:", conn.connected)
        conn.ensure_connection()
        print("Celery Ensure Connection: OK")
except Exception as e:
    print(f"App Config connection FAILED: {e}")
