import sqlite3
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('qr_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS qr_codes
                 (id TEXT PRIMARY KEY, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/create_qr', methods=['POST'])
def create_qr():
    data = request.get_json()
    content = data.get('content', '')
    qr_id = str(uuid.uuid4())
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('qr_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO qr_codes (id, content, created_at) VALUES (?, ?, ?)",
              (qr_id, content, created_at))
    conn.commit()
    conn.close()
    return jsonify({'id': qr_id, 'url': f'http://127.0.0.1:5000/qr/{qr_id}'})

@app.route('/qr/<qr_id>', methods=['GET'])
def get_qr_content(qr_id):
    conn = sqlite3.connect('qr_data.db')
    c = conn.cursor()
    c.execute("SELECT content FROM qr_codes WHERE id = ?", (qr_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({'content': result[0]})
    return jsonify({'error': 'QR Code not found'}), 404

@app.route('/api/update_qr/<qr_id>', methods=['PUT'])
def update_qr(qr_id):
    data = request.get_json()
    new_content = data.get('content', '')
    conn = sqlite3.connect('qr_data.db')
    c = conn.cursor()
    c.execute("UPDATE qr_codes SET content = ? WHERE id = ?", (new_content, qr_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    if affected:
        return jsonify({'message': 'Content updated successfully'})
    return jsonify({'error': 'QR Code not found'}), 404

@app.route('/api/list_qr', methods=['GET'])
def list_qr():
    conn = sqlite3.connect('qr_data.db')
    c = conn.cursor()
    c.execute("SELECT id, content, created_at FROM qr_codes")
    rows = c.fetchall()
    conn.close()
    qr_list = [{'id': row[0], 'content': row[1], 'created_at': row[2]} for row in rows]
    return jsonify(qr_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)