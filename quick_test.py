"""
Firebase Quick Test Script
This will verify your Firebase connection
"""

import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

print("=" * 50)
print("FIREBASE QUICK TEST")
print("=" * 50)

# Load environment variables
print("\n1. Loading .env file...")
load_dotenv()
print("   ✅ .env loaded")

# Get database URL
db_url = os.getenv('FIREBASE_DATABASE_URL')
print(f"2. Database URL: {db_url}")

# Get project ID
project_id = os.getenv('FIREBASE_PROJECT_ID')
print(f"3. Project ID: {project_id}")

# Get client email
client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
print(f"4. Client Email: {client_email}")

print("\n5. Preparing credentials...")
try:
    # Handle private key
    private_key = os.getenv('FIREBASE_PRIVATE_KEY')
    if private_key and '\\n' in private_key:
        private_key = private_key.replace('\\n', '\n')
    
    cred_dict = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": client_email,
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    }
    
    cred = credentials.Certificate(cred_dict)
    print("   ✅ Credentials created")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit()

print("\n6. Initializing Firebase...")
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': db_url
    })
    print("   ✅ Firebase initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit()

print("\n7. Testing database connection...")
try:
    ref = db.reference('/bus_stops')
    data = ref.get()
    
    if data:
        print(f"   ✅ Connected! Found {len(data)} bus stop(s)")
        for stop in data.keys():
            print(f"      - {stop}")
    else:
        print("   ⚠️ Connected but no data found at /bus_stops")
        print("      Make sure your ESP32 is sending data")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)

# Keep window open
input("\nPress Enter to exit...")