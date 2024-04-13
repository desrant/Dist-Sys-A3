import logging
import threading
import uuid
from flask import Flask, request, jsonify, Response
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def generate_unique_id() -> int:
    return uuid.uuid4().int

class SingletonMeta(type):
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
                logging.debug(f"Created a new instance of {cls.__name__}")
            return cls._instances[cls]

class ThreadSafeLockManager(metaclass=SingletonMeta):
    def __init__(self):
        self.lock_map: Dict[int, threading.Lock] = {}

    def acquire(self, key: int):
        if key not in self.lock_map:
            self.lock_map[key] = threading.Lock()
            logging.debug(f"New lock created for key: {key}")
        logging.debug(f"Lock acquired for key: {key}")
        self.lock_map[key].acquire()

    def release(self, key: int):
        if key in self.lock_map:
            logging.debug(f"Lock released for key: {key}")
            self.lock_map[key].release()

class DataStore:
    def __init__(self):
        self.storage: Dict[int, str] = {}
        self.lock_manager = ThreadSafeLockManager()

    def insert(self, key: int, value: str):
        self.lock_manager.acquire(key)
        try:
            self.storage[key] = value
            logging.info(f"Inserted data at key {key}: {value}")
        finally:
            self.lock_manager.release(key)

    def delete(self, key: int):
        self.lock_manager.acquire(key)
        try:
            if key in self.storage:
                del self.storage[key]
                logging.info(f"Deleted data at key {key}")
        finally:
            self.lock_manager.release(key)

    def update(self, key: int, value: str):
        self.lock_manager.acquire(key)
        try:
            if key in self.storage:
                self.storage[key] = value
                logging.info(f"Updated data at key {key} to {value}")
        finally:
            self.lock_manager.release(key)

    def read(self, key: int) -> Optional[str]:
        if key in self.storage:
            logging.debug(f"Read data at key {key}: {self.storage[key]}")
            return self.storage[key]
        else:
            logging.error(f"Attempted to read non-existent key {key}")
            return None

data_store = DataStore()

@app.route('/data', methods=['POST', 'PUT', 'DELETE', 'GET'])
def handle_data():
    response: Dict[str, Any] = {}
    try:
        if request.method == 'POST':
            key, value = request.json['key'], request.json['value']
            data_store.insert(key, value)
            response = {'status': 'success', 'action': 'inserted'}

        elif request.method == 'DELETE':
            key = request.args.get('key', type=int)
            data_store.delete(key)
            response = {'status': 'success', 'action': 'deleted'}

        elif request.method == 'PUT':
            key, value = request.json['key'], request.json['value']
            data_store.update(key, value)
            response = {'status': 'success', 'action': 'updated'}

        elif request.method == 'GET':
            key = request.args.get('key', type=int)
            value = data_store.read(key)
            if value is not None:
                response = {'value': value}
            else:
                response = {'error': 'Not found'}, 404
    except Exception as e:
        logging.error("Error handling request: " + str(e))
        response = {'error': 'Server error'}, 500

    return jsonify(response), response.get('status_code', 200)


app.run(host='0.0.0.0', port=5000, debug=True)
