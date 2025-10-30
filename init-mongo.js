// MongoDB initialization script
db = db.getSiblingDB('genomeguard');

// Create collections with indexes
db.createCollection('users');
db.createCollection('analyses');

// Create indexes for better performance
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.analyses.createIndex({ "user_id": 1 });
db.analyses.createIndex({ "created_at": -1 });

print('Database initialized successfully');