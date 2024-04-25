from flask import Flask, request, jsonify, abort
import pymysql.cursors
from concurrent.futures import ThreadPoolExecutor
import logging
from os import environ
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class Config:
    HOST = environ.get('DB_HOST', 'localhost')
    USER = environ.get('DB_USER', 'user')
    PASSWORD = environ.get('DB_PASSWORD', 'password')
    DATABASE = environ.get('DB_NAME', 'sample_db')
    CHARSET = 'utf8mb4'
    CURSORCLASS = pymysql.cursors.DictCursor

class DatabaseService:
    def __init__(self, config):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.connection = self.connect_to_database()

    def connect_to_database(self):
        try:
            connection = pymysql.connect(host=self.config.HOST,
                                         user=self.config.USER,
                                         password=self.config.PASSWORD,
                                         db=self.config.DATABASE,
                                         charset=self.config.CHARSET,
                                         cursorclass=self.config.CURSORCLASS)
            return connection
        except pymysql.MySQLError as e:
            logging.error(f"Database connection failed due to {e}")
            raise

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                else:
                    self.connection.commit()
                    result = cursor.lastrowid or True
            return result
        except Exception as e:
            logging.error(f"Query failed: {e}")
            self.connection.rollback()
            raise

    def close(self):
        self.connection.close()

app = Flask(__name__)
db_service = DatabaseService(Config())

@app.route('/api/data', methods=['POST'])
def create_record():
    data = request.json
    if not data:
        logging.error("POST request with no data")
        abort(400, description="No data provided.")

    query = "INSERT INTO records (name, value) VALUES (%s, %s)"
    record_id = db_service.execute_query(query, (data['name'], data['value']))
    return jsonify({'record_id': record_id}), 201

@app.route('/api/data/<int:record_id>', methods=['GET'])
def read_record(record_id):
    query = "SELECT * FROM records WHERE id = %s"
    result = db_service.execute_query(query, (record_id,))
    if not result:
        abort(404, description=f"Record with ID {record_id} not found.")
    return jsonify(result), 200

@app.route('/api/data/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.json
    if not data:
        abort(400, description="No update data provided.")
    query = "UPDATE records SET name = %s, value = %s WHERE id = %s"
    db_service.execute_query(query, (data['name'], data['value'], record_id))
    return jsonify({'message': 'Record updated'}), 200

@app.route('/api/data/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    query = "DELETE FROM records WHERE id = %s"
    db_service.execute_query(query, (record_id,))
    return jsonify({'message': 'Record deleted'}), 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'Service is running'}), 200

@app.teardown_appcontext
def cleanup(resp_or_exc):
    db_service.close()
    logging.info("Database connection closed")


app.run(host='0.0.0.0', port=5000)
