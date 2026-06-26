import datetime
from pymongo import MongoClient, ASCENDING
from config import Config

# Initialize MongoDB Client – exposed as module-level so app.py can ping it for health checks
client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[Config.DATABASE_NAME]

# Collections
jewelry_col = db['jewelry']
logs_col = db['logs']


def init_db():
    """Initializes the database schema and indexes."""
    # Create unique index on HUID (HUID is always uppercase & trimmed)
    jewelry_col.create_index([("huid", ASCENDING)], unique=True)
    # Create index on log timestamps for fast retrieval
    logs_col.create_index([("timestamp", ASCENDING)])

def serialize_doc(doc):
    """Utility to convert MongoDB BSON documents (ObjectIds, Datetimes) to JSON serializable structures."""
    if not doc:
        return None
    serialized = dict(doc)
    serialized.pop('_id', None)  # Remove MongoDB internal ID
    
    # Format datetime fields to ISO format strings
    for key, value in serialized.items():
        if isinstance(value, datetime.datetime):
            serialized[key] = value.isoformat()
            
    return serialized

def get_jewelry(huid):
    """Retrieves a jewelry item by HUID and logs the verification check."""
    normalized_huid = huid.strip().upper()
    item = jewelry_col.find_one({"huid": normalized_huid})
    
    # Log the lookup attempt
    if item:
        status = item.get('status', 'Active')
        log_type = 'stolen_check' if status == 'Stolen' else 'verify'
        add_log(
            log_type, 
            normalized_huid, 
            f"Verification search performed on HUID {normalized_huid} ({status})"
        )
    else:
        add_log(
            'verify_fail', 
            normalized_huid, 
            f"Failed verification search for unregistered HUID {normalized_huid}"
        )
        
    return serialize_doc(item)

def register_jewelry(data):
    """Registers a new jewelry item in the database."""
    normalized_huid = data['huid'].strip().upper()
    
    # Check if HUID is already registered
    if jewelry_col.find_one({"huid": normalized_huid}):
        return {"success": False, "message": "This HUID is already registered in the system."}
    
    new_record = {
        "huid": normalized_huid,
        "ownerName": data['ownerName'].strip(),
        "ownerPhone": data['ownerPhone'].strip(),
        "ownerEmail": data.get('ownerEmail', '').strip(),
        "ownerIdType": data['ownerIdType'].strip(),
        "ownerIdNo": data['ownerIdNo'].strip(),
        "jewelType": data['jewelType'].strip(),
        "metalPurity": data['metalPurity'].strip(),
        "weight": float(data['weight']),
        "purchaseGoldRate": float(data.get('purchaseGoldRate', 0)),
        "description": data['description'].strip(),
        "shopName": data['shopName'].strip(),
        "purchaseDate": data['purchaseDate'],
        "status": "Active",
        "passcode": data['passcode'].strip(),
        "registeredAt": datetime.datetime.utcnow()
    }
    
    jewelry_col.insert_one(new_record)
    
    add_log(
        'register', 
        normalized_huid, 
        f"New HUID {normalized_huid} ({new_record['jewelType']}) registered under {new_record['ownerName']}"
    )
    
    return {"success": True, "record": serialize_doc(new_record)}

def verify_owner_login(huid, passcode):
    """Verifies owner login credentials by HUID and 4-digit passcode."""
    normalized_huid = huid.strip().upper()
    item = jewelry_col.find_one({"huid": normalized_huid})
    
    if not item:
        return {"success": False, "message": "HUID not found."}
        
    if item.get('passcode') != passcode.strip():
        return {"success": False, "message": "Incorrect ownership verification passcode."}
        
    add_log('owner_login', normalized_huid, f"Gold owner for HUID {normalized_huid} logged in successfully")
    return {"success": True, "record": serialize_doc(item)}

def update_status(huid, new_status, passcode, extra_details=''):
    """Updates the status (Active/Stolen) of a jewelry item after verifying the passcode."""
    normalized_huid = huid.strip().upper()
    item = jewelry_col.find_one({"huid": normalized_huid})
    
    if not item:
        return {"success": False, "message": "HUID not found."}
        
    if item.get('passcode') != passcode.strip():
        return {"success": False, "message": "Incorrect ownership verification passcode."}
        
    update_data = {
        "status": new_status
    }
    
    if new_status == 'Stolen':
        update_data["stolenDate"] = datetime.date.today().isoformat()
        update_data["theftDetails"] = extra_details.strip() or "No additional details provided."
        log_msg = f"HUID {normalized_huid} reported STOLEN by owner"
        log_type = 'stolen'
    else:
        # Unset stolen specific fields
        jewelry_col.update_one(
            {"huid": normalized_huid},
            {"$unset": {"stolenDate": "", "theftDetails": ""}}
        )
        log_msg = f"HUID {normalized_huid} status updated to Active/Recovered"
        log_type = 'recover'
        
    jewelry_col.update_one({"huid": normalized_huid}, {"$set": update_data})
    
    add_log(log_type, normalized_huid, log_msg)
    
    # Reload and return updated doc
    updated_item = jewelry_col.find_one({"huid": normalized_huid})
    return {"success": True, "record": serialize_doc(updated_item)}

def get_stats():
    """Calculates statistics overview for the dashboard."""
    total_registered = jewelry_col.count_documents({})
    active_count = jewelry_col.count_documents({"status": "Active"})
    stolen_count = jewelry_col.count_documents({"status": "Stolen"})
    
    # Get total search logs (verify/stolen_check types)
    verification_logs = logs_col.count_documents({"type": {"$in": ["verify", "stolen_check"]}})
    
    return {
        "totalRegistered": total_registered,
        "activeCount": active_count,
        "stolenCount": stolen_count,
        "verificationLogsCount": verification_logs
    }

def get_logs(limit=30):
    """Retrieves recent logs sorted by timestamp descending."""
    logs = logs_col.find().sort("timestamp", -1).limit(limit)
    return [serialize_doc(log) for log in logs]

def getAll():
    """Retrieves all registered items."""
    items = jewelry_col.find().sort("registeredAt", -1)
    return [serialize_doc(item) for item in items]

def add_log(log_type, huid, message):
    """Logs system events into the MongoDB logs collection."""
    new_log = {
        "type": log_type,
        "huid": huid,
        "message": message,
        "timestamp": datetime.datetime.utcnow()
    }
    logs_col.insert_one(new_log)
