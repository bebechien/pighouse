import os
import time
import datetime
import telegram, asyncio
import json
from flask import Flask, jsonify, request

bot_token = 'YOUR_BOT_TOKEN_HERE'
chat_id = 'YOUR_USER_ID_HERE'

async def send_telegram_message(msg):
    bot = telegram.Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

app = Flask(__name__)

clients_data = {}
storages_data = {}

@app.route('/', methods=['GET'])
def index():
    cpu_chart_data = []
    mem_chart_data = []
    storage_chart_data = []
    for client_id, client_data in clients_data.items():
        cpu_chart_data.append({
            "label": f"{client_id}",
            "data": client_data["cpu_load"]
        })
        mem_chart_data.append({
            "label": f"{client_id}",
            "data": client_data["memory_usage"]
        })
        storage_chart_data.append({
            "label": f"{client_id}",
            "data": client_data["storage_usage"]
        })
    cpu_chart_data = json.dumps(cpu_chart_data)
    mem_chart_data = json.dumps(mem_chart_data)
    storage_chart_data = json.dumps(storage_chart_data)

    recent_cpu_loads = []
    table_rows = []
    for client_id, client_data in clients_data.items():
        table_rows.append(
            f"<tr><td>{client_id}</td>"
            f"<td>{client_data['cpu_load'][-1]}</td>"
            f"<td>{client_data['memory_usage'][-1]}</td>"
            f"<td>{client_data['storage_usage'][-1]}</td></tr>"
        )
        recent_cpu_loads.append(client_data['cpu_load'][-1])
    table_html = "<table><tr><th>Client ID</th><th>CPU Load</th><th>Memory Usage</th><th>Storage Usage</th></tr>"
    table_html += "".join(table_rows)
    table_html += "</table>"

    storage_rows = []
    for storage_id, storage_data in storages_data.items():
        storage_rows.append(
            f"<tr><td>{storage_id}</td>"
            f"<td>{storage_data['usage']}</td></tr>"
        )
    storage_html = "<table><tr><th>Storage ID</th><th>Usage</th></tr>"
    storage_html += "".join(storage_rows)
    storage_html += "</table>"

    chart_html = f"""
        <canvas id="cpuChart" width="400" height="200"></canvas>
        <canvas id="memChart" width="400" height="200"></canvas>
        <canvas id="storageChart" width="400" height="200"></canvas>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            var ctx = document.getElementById('cpuChart').getContext('2d');
            var cpuChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(list(range(10)))},
                    datasets: {cpu_chart_data}
                }},
                options: {{
                    responsive: false,
                }}
            }});

            var ctx2 = document.getElementById('memChart').getContext('2d');
            var memChart = new Chart(ctx2, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(list(range(10)))},
                    datasets: {mem_chart_data}
                }},
                options: {{
                    responsive: false,
                }}
            }});

            var ctx3 = document.getElementById('storageChart').getContext('2d');
            var storageChart = new Chart(ctx3, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(list(range(10)))},
                    datasets: {storage_chart_data}
                }},
                options: {{
                    responsive: false,
                }}
            }});
        </script>
    """

    image_idx = 0
    if recent_cpu_loads:
        image_idx = int(max(recent_cpu_loads)/10)
        if image_idx > 10:
            image_idx = 10

    image_html = '<img src="static/{:02d}.png" width=128>'.format(image_idx)

    return f"<html><body>{image_html}{chart_html}{table_html}{storage_html}</body></html>"

@app.route('/data', methods=['POST'])
def data():
    content = request.json
    client_id = content['client_id']
    if client_id not in clients_data:
        clients_data[client_id] = {
            'cpu_load': [],
            'memory_usage': [],
            'storage_usage': [],
            'cpu_warning_flag': False,
            'storage_warning_flag': False
        }
    clients_data[client_id]['cpu_load'].append(content['cpu_load'])
    clients_data[client_id]['memory_usage'].append(content['memory_usage'])
    clients_data[client_id]['storage_usage'].append(content['storage_usage'])

    clients_data[client_id]['cpu_load'] = clients_data[client_id]['cpu_load'][-10:]
    clients_data[client_id]['memory_usage'] = clients_data[client_id]['memory_usage'][-10:]
    clients_data[client_id]['storage_usage'] = clients_data[client_id]['storage_usage'][-10:]

    message = ''
    if content['cpu_load'] > 200:
        if not clients_data[client_id]['cpu_warning_flag']:
            message += f"<b>WARNING</b>\n{client_id}'s CPU load is too high ({content['cpu_load']})\n"
            clients_data[client_id]['cpu_warning_flag'] = True
    else:
        if clients_data[client_id]['cpu_warning_flag']:
            message += f"{client_id}'s CPU load is now back to normal ({content['cpu_load']})\n"
        clients_data[client_id]['cpu_warning_flag'] = False

    if content['storage_usage'] > 90:
        if not clients_data[client_id]['storage_warning_flag']:
            message += f"<b>WARNING</b>\n{client_id}'s Storage usage is too high ({content['storage_usage']})\n"
            clients_data[client_id]['storage_warning_flag'] = True
    else:
        if clients_data[client_id]['storage_warning_flag']:
            message += f"{client_id}'s Storage usage is not back to normal ({content['storage_usage']})\n"
        clients_data[client_id]['storage_warning_flag'] = False

    if len(message) > 0:
        asyncio.run(send_telegram_message(message))

    return jsonify({'status': 'ok'})

@app.route('/storage', methods=['POST'])
def storage():
    message = ''

    for content in request.json:
        storage_id = content['storage_id']
        if storage_id not in storages_data:
            storages_data[storage_id] = {
                'usage': [],
                'warning_flag': False
            }

        storages_data[storage_id]['usage'] = content['usage']
        if content['usage'] > 90:
            if not storages_data[storage_id]['warning_flag']:
                message += f"<b>STORAGE WARNING</b>\n{storage_id} Usage is too high ({content['usage']})\n"
                storages_data[storage_id]['warning_flag'] = True
        else:
            if storages_data[storage_id]['warning_flag']:
                message += f"{storage_id} Usage is not back to normal ({content['usage']})\n"
            storages_data[storage_id]['warning_flag'] = False

    if len(message) > 0:
        asyncio.run(send_telegram_message(message))

    return jsonify({'status': 'ok'})

@app.route('/send_summary', methods=['POST'])
def send_summary():
    if not bot_token or not chat_id:
        return jsonify({'status': 'error', 'message': 'Missing Telegram bot token or chat ID'})

    message = '-=: Hourly Report :=-\n'
    for client_id, client_data in clients_data.items():
        message += f"+ <b>{client_id}</b>\n<pre>CPU load: {client_data['cpu_load'][-1]}\nMemory usage: {client_data['memory_usage'][-1]}\nStorage usage: {client_data['storage_usage'][-1]}</pre>\n"

    asyncio.run(send_telegram_message(message))

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

