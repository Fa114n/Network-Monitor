from flask import Flask, render_template, jsonify
import psutil
import subprocess
import platform
import socket
import datetime

app = Flask(__name__)

def ping_host(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-W', '1', host]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except:
        return False

def get_network_stats():
    stats = psutil.net_io_counters()
    return {
        'bytes_sent': round(stats.bytes_sent / 1024 / 1024, 2),
        'bytes_recv': round(stats.bytes_recv / 1024 / 1024, 2),
        'packets_sent': stats.packets_sent,
        'packets_recv': stats.packets_recv
    }

def get_connections():
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED' and conn.raddr:
                try:
                    connections.append({
                        'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'remote': f"{conn.raddr.ip}:{conn.raddr.port}",
                        'status': conn.status,
                        'pid': conn.pid
                    })
                except:
                    pass
    except psutil.AccessDenied:
        pass
    return connections[:15]

def get_interfaces():
    interfaces = []
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                stats = psutil.net_if_stats().get(name)
                interfaces.append({
                    'name': name,
                    'ip': addr.address,
                    'netmask': addr.netmask,
                    'is_up': stats.isup if stats else False,
                    'speed': stats.speed if stats else 0
                })
    return interfaces

# Common hosts to monitor
MONITORED_HOSTS = [
    {'name': 'Gateway', 'host': '192.168.1.1'},
    {'name': 'Google DNS', 'host': '8.8.8.8'},
    {'name': 'Cloudflare', 'host': '1.1.1.1'},
    {'name': 'Local Machine', 'host': '127.0.0.1'},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'network': get_network_stats(),
        'connections': get_connections(),
        'interfaces': get_interfaces(),
        'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
    })

@app.route('/api/ping')
def api_ping():
    results = []
    for host in MONITORED_HOSTS:
        results.append({
            'name': host['name'],
            'host': host['host'],
            'alive': ping_host(host['host'])
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)