from flask import Flask, request, jsonify
import threading
import requests
import time
from dataclasses import dataclass, field
from typing import Dict, List

app = Flask(__name__)

@dataclass
class Server:
    name: str
    active: bool = True
    last_sync: float = field(default_factory=time.time)

@dataclass
class Shard:
    servers: List[Server]
    primary: Server = None

    def elect_leader(self):
        if not self.primary or not self.primary.active:
            active_servers = [server for server in self.servers if server.active]
            self.primary = max(active_servers, key=lambda x: x.last_sync, default=None)
        return self.primary

    def heartbeat(self):
        for server in self.servers:
            if not send_heartbeat(server.name):
                server.active = False
            else:
                server.last_sync = time.time()

def send_heartbeat(server_url):
    try:
        response = requests.get(f'http://{server_url}/heartbeat')
        return response.status_code == 200
    except requests.ConnectionError:
        return False

class ShardManager:
    shards: Dict[str, Shard] = {}

    @classmethod
    def add_server(cls, shard_id, server):
        if shard_id not in cls.shards:
            cls.shards[shard_id] = Shard(servers=[])
        cls.shards[shard_id].servers.append(server)

    @classmethod
    def remove_server(cls, shard_id, server_name):
        if shard_id in cls.shards:
            cls.shards[shard_id].servers = [s for s in cls.shards[shard_id].servers if s.name != server_name]
            if cls.shards[shard_id].primary and cls.shards[shard_id].primary.name == server_name:
                cls.shards[shard_id].primary = None

def monitor_system():
    while True:
        for shard_id, shard in ShardManager.shards.items():
            shard.heartbeat()
            shard.elect_leader()
        time.sleep(10)  # Sleep time could be adjusted based on system needs

@app.route('/add_server', methods=['POST'])
def add_server():
    data = request.json
    server = Server(name=data['server_name'])
    ShardManager.add_server(data['shard_id'], server)
    return jsonify({'message': 'Server added successfully'})

@app.route('/remove_server', methods=['POST'])
def remove_server():
    data = request.json
    ShardManager.remove_server(data['shard_id'], data['server_name'])
    return jsonify({'message': 'Server removed successfully'})

@app.route('/get_primary', methods=['GET'])
def get_primary():
    shard_id = request.args.get('shard_id')
    primary = ShardManager.shards[shard_id].elect_leader()
    return jsonify({'primary': primary.name if primary else 'No active primary'})

if __name__ == '__main__':
    threading.Thread(target=monitor_system, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
