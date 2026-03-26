"""
Firebase Connection Test with Detailed Error Reporting
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("FIREBASE CONNECTION TEST")
print("=" * 60)

# Step 1: Load .env file
print("\n[1] Loading .env file...")
env_file = os.path.join(os.getcwd(), '.env')
print(f"    Looking for: {env_file}")

if os.path.exists(env_file):
    print(f"    ✅ .env file found")
    print(f"    File size: {os.path.getsize(env_file)} bytes")
else:
    print(f"    ❌ .env file NOT found!")
    sys.exit(1)

# Load the environment variables
load_dotenv(env_file, override=True)
print("    ✅ Environment variables loaded")

# Step 2: Check each required variable
print("\n[2] Checking Firebase configuration variables...")

variables = {
    'FIREBASE_DATABASE_URL': 'Database URL',
    'FIREBASE_PROJECT_ID': 'Project ID',
    'FIREBASE_PRIVATE_KEY_ID': 'Private Key ID',
    'FIREBASE_PRIVATE_KEY': 'Private Key',
    'FIREBASE_CLIENT_EMAIL': 'Client Email',
    'FIREBASE_CLIENT_ID': 'Client ID'
}

all_present = True
for var, description in variables.items():
    value = os.getenv(var)
    if value:
        # Show first few characters of each value for verification
        if var == 'FIREBASE_PRIVATE_KEY':
            preview = value[:50] + "..." if len(value) > 50 else value
            print(f"    ✅ {description}: {preview}")
        elif var == 'FIREBASE_DATABASE_URL':
            print(f"    ✅ {description}: {value}")
        else:
            print(f"    ✅ {description}: {value[:20]}..." if len(value) > 20 else f"    ✅ {description}: {value}")
    else:
        print(f"    ❌ {description} is MISSING!")
        all_present = False

if not all_present:
    print("\n❌ Some Firebase variables are missing. Please check your .env file.")
    sys.exit(1)

# Step 3: Test Firebase import and initialization
print("\n[3] Testing Firebase initialization...")

try:
    import firebase_admin
    from firebase_admin import credentials, db
    print("    ✅ Firebase Admin SDK imported")
except ImportError as e:
    print(f"    ❌ Failed to import firebase_admin: {e}")
    print("    Run: pip install firebase-admin")
    sys.exit(1)

# Step 4: Create credentials
print("\n[4] Creating credentials...")

try:
    # Get private key and fix newlines
    private_key = os.getenv('FIREBASE_PRIVATE_KEY')
    if private_key and '\\n' in private_key:
        private_key = private_key.replace('\\n', '\n')
        print("    ✅ Fixed private key newlines")
    
    # Create credential dictionary with ALL required fields
    cred_dict = {
        "type": "service_account",
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL').replace('@', '%40')}"
    }
    
    cred = credentials.Certificate(cred_dict)
    print("    ✅ Credentials created successfully")
    
except Exception as e:
    print(f"    ❌ Error creating credentials: {e}")
    print("\nDebug: Credential dictionary keys:", list(cred_dict.keys()))
    sys.exit(1)

# Step 5: Initialize Firebase
print("\n[5] Initializing Firebase app...")

try:
    # Check if already initialized
    try:
        firebase_admin.get_app()
        print("    ⚠️ Firebase already initialized, reusing...")
    except ValueError:
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
        })
        print("    ✅ Firebase initialized successfully")
        
except Exception as e:
    print(f"    ❌ Error initializing Firebase: {e}")
    sys.exit(1)

# Step 6: Test database access
print("\n[6] Testing database access...")

try:
    # Try to read from database
    ref = db.reference('/')
    print("    ✅ Got database reference")
    
    # Try to get bus_stops
    bus_stops_ref = db.reference('/bus_stops')
    data = bus_stops_ref.get()
    
    if data is None:
        print("    ⚠️ No data found at /bus_stops")
        print("    This is normal if no ESP32 has uploaded data yet")
    else:
        print(f"    ✅ Found {len(data)} bus stop(s):")
        for stop_id in data.keys():
            print(f"        - {stop_id}")
            
except Exception as e:
    print(f"    ❌ Error accessing database: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)
input("\nPress Enter to exit...")