"""
Quick MongoDB Connection Test
Tests if we can connect to MongoDB and create a user
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.models.database import connect_to_mongo, get_database
from loguru import logger

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("MONGODB CONNECTION TEST")
    print("="*60)
    
    # Try to connect
    print("\n1. Attempting to connect to MongoDB...")
    try:
        connect_to_mongo()
        db = get_database()
        
        if db is None:
            print("❌ FAILED: Database is None")
            print("   MongoDB might not be available")
            return False
        
        print("✅ SUCCESS: Connected to MongoDB")
        
        # Test database access
        print(f"\n2. Database name: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"\n3. Existing collections: {collections}")
        
        # Check if users collection exists
        if 'users' in collections:
            user_count = db.users.count_documents({})
            print(f"\n4. Users collection exists")
            print(f"   Total users: {user_count}")
            
            # Show some users (without passwords)
            if user_count > 0:
                print("\n5. Sample users:")
                for user in db.users.find().limit(5):
                    print(f"   - {user.get('username')} ({user.get('email')})")
        else:
            print(f"\n4. Users collection does NOT exist yet")
            print("   It will be created when first user registers")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_creation():
    """Test creating a user"""
    print("\n" + "="*60)
    print("USER CREATION TEST")
    print("="*60)
    
    try:
        db = get_database()
        if db is None:
            print("❌ Cannot test - database not connected")
            return False
        
        # Create a test user directly
        import uuid
        import bcrypt
        from datetime import datetime
        
        test_user = {
            "_id": str(uuid.uuid4()),
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode(),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Check if test user already exists
        existing = db.users.find_one({"username": "testuser"})
        if existing:
            print("ℹ️  Test user 'testuser' already exists")
            print(f"   Email: {existing.get('email')}")
            print(f"   Created: {existing.get('created_at')}")
            return True
        
        # Insert test user
        result = db.users.insert_one(test_user)
        print(f"✅ Test user created successfully!")
        print(f"   Username: testuser")
        print(f"   Email: test@example.com")
        print(f"   ID: {result.inserted_id}")
        
        # Verify it was created
        user = db.users.find_one({"_id": test_user["_id"]})
        if user:
            print(f"\n✅ Verified: User exists in database")
            return True
        else:
            print(f"\n❌ ERROR: User not found after creation")
            return False
        
    except Exception as e:
        print(f"❌ ERROR creating user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test connection
    connection_ok = test_mongodb_connection()
    
    if connection_ok:
        print("\n")
        test_user_creation()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    if not connection_ok:
        print("\n⚠️  TROUBLESHOOTING:")
        print("1. Check your MongoDB Atlas connection string in .env")
        print("2. Verify network access (IP whitelist)")
        print("3. Check username/password in connection string")
        print("4. Make sure MongoDB Atlas cluster is running")
