import os
import time
import datetime
import telegram, asyncio
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

clients_data = {}

@app.route('/', methods=['GET'])
def index():
    cpu_chart_data = []
    mem_chart_data = []
    storage_chart_data = []
    for client_id, client_data in clients_data.items():
        cpu_chart_data.append({
            "label": f"Client {client_id}",
            "data": client_data["cpu_load"]
        })
        mem_chart_data.append({
            "label": f"Client {client_id}",
            "data": client_data["memory_usage"]
        })
        storage_chart_data.append({
            "label": f"Client {client_id}",
            "data": client_data["storage_usage"]
        })
    cpu_chart_data = json.dumps(cpu_chart_data)
    mem_chart_data = json.dumps(mem_chart_data)
    storage_chart_data = json.dumps(storage_chart_data)

    table_rows = []
    for client_id, client_data in clients_data.items():
        table_rows.append(
            f"<tr><td>{client_id}</td>"
            f"<td>{client_data['cpu_load'][-1]}</td>"
            f"<td>{client_data['memory_usage'][-1]}</td>"
            f"<td>{client_data['storage_usage'][-1]}</td></tr>"
        )
    table_html = "<table><tr><th>Client ID</th><th>CPU Load</th><th>Memory Usage</th><th>Storage Usage</th></tr>"
    table_html += "".join(table_rows)
    table_html += "</table>"

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

    return f"<html><body>{chart_html}{table_html}</body></html>"

@app.route('/data', methods=['POST'])
def data():
    content = request.json
    client_id = content['client_id']
    if client_id not in clients_data:
        clients_data[client_id] = {
            'cpu_load': [],
            'memory_usage': [],
            'storage_usage': []
        }
    clients_data[client_id]['cpu_load'].append(content['cpu_load'])
    clients_data[client_id]['memory_usage'].append(content['memory_usage'])
    clients_data[client_id]['storage_usage'].append(content['storage_usage'])

    clients_data[client_id]['cpu_load'] = clients_data[client_id]['cpu_load'][-10:]
    clients_data[client_id]['memory_usage'] = clients_data[client_id]['memory_usage'][-10:]
    clients_data[client_id]['storage_usage'] = clients_data[client_id]['storage_usage'][-10:]

    return jsonify({'status': 'ok'})

@app.route('/send_summary', methods=['POST'])
def send_summary():
    bot_token = 'YOUR_BOT_TOKEN_HERE'
    chat_id = 'YOUR_USER_ID_HERE'
    if not bot_token or not chat_id:
        return jsonify({'status': 'error', 'message': 'Missing Telegram bot token or chat ID'})

    message = 'reporting\n'
    for client_id, client_data in clients_data.items():
        message += f"{client_id}\nCPU load: {client_data['cpu_load'][-1]}\nMemory usage: {client_data['memory_usage'][-1]}\nStorage usage: {client_data['storage_usage'][-1]}\n\n"
    
    async def send_telegram_message():
        bot = telegram.Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)

    asyncio.run(send_telegram_message())

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

    while True:
        now = datetime.datetime.now()
        if now.minute == 0: # Send the message every hour
            response = requests.post('http://localhost:5000/send_summary')
            print(response.json())
        time.sleep(60)  # Wait for 1 minute before checking again