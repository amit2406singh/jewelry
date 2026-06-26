from flask import Flask, jsonify, request
from flask_cors import CORS
import database
from config import Config

app = Flask(__name__)

# Enable CORS - allow any origin (dev mode). In production, restrict to your domain.
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

# Initialize Database Schema & Indices
try:
    database.init_db()
    print("[OK] MongoDB connection established successfully.")
except Exception as e:
    print(f"[WARN] MongoDB init warning: {e}")

@app.after_request
def after_request(response):
    """Ensure CORS headers are always present."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Simple status check endpoint."""
    try:
        # Ping MongoDB to confirm it's reachable
        database.client.admin.command('ping')
        return jsonify({"status": "healthy", "service": "huid-backend", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "service": "huid-backend", "db": str(e)}), 503

@app.route('/api/jewelry', methods=['GET'])
def get_all_jewelry():
    """Retrieve all registered items in the ledger."""
    try:
        items = database.getAll()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/jewelry/<huid>', methods=['GET'])
def get_jewelry_item(huid):
    """Retrieve details for a specific HUID."""
    try:
        item = database.get_jewelry(huid)
        if not item:
            return jsonify({"success": False, "message": "HUID not found."}), 404
        return jsonify(item), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/jewelry/register', methods=['POST'])
def register_item():
    """Create a new jewelry record."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Request body cannot be empty."}), 400
            
        required_fields = ['huid', 'ownerName', 'ownerPhone', 'ownerIdType', 'ownerIdNo', 'jewelType', 'metalPurity', 'weight', 'description', 'shopName', 'purchaseDate', 'passcode']
        missing = [f for f in required_fields if f not in data or not str(data[f]).strip()]
        if missing:
            return jsonify({"success": False, "message": f"Missing required fields: {', '.join(missing)}"}), 400
            
        result = database.register_jewelry(data)
        if not result['success']:
            return jsonify(result), 400
            
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/auth/owner', methods=['POST'])
def login_owner():
    """Verify owner login using HUID and passcode."""
    try:
        data = request.json
        if not data or 'huid' not in data or 'passcode' not in data:
            return jsonify({"success": False, "message": "HUID and Passcode are required."}), 400
            
        result = database.verify_owner_login(data['huid'], data['passcode'])
        if not result['success']:
            return jsonify(result), 401
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/jewelry/<huid>/status', methods=['PUT'])
def update_item_status(huid):
    """Update status (Report Stolen / Recovered) of an item."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "Request body cannot be empty."}), 400
            
        status = data.get('status')
        passcode = data.get('passcode')
        extra_details = data.get('theftDetails', '')
        
        if not status or not passcode:
            return jsonify({"success": False, "message": "Status and Passcode are required fields."}), 400
            
        if status not in ['Active', 'Stolen']:
            return jsonify({"success": False, "message": "Invalid status option. Must be Active or Stolen."}), 400
            
        result = database.update_status(huid, status, passcode, extra_details)
        if not result['success']:
            return jsonify(result), 400
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Retrieve system counts and dashboard statistics."""
    try:
        stats = database.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_system_logs():
    """Retrieve recent logging items."""
    try:
        logs = database.get_logs()
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    print(f"[START] Starting AURA HUID Backend on port {Config.PORT}...")
    print(f"[DB] MongoDB URI: {Config.MONGO_URI}")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
