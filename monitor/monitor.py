import os
import time
import datetime
import telegram, asyncio
import json
from flask import Flask, jsonify, request

bot_token = 'YOUR_BOT_TOKEN_HERE'
chat_id = 'YOUR_USER_ID_HERE'
project_abs_path = 'YOUR_CODE_LOCAL_PATH_HERE'
image_idx = 0

NOTIFY_THRESHOLD = 600  # Notify if a client has not reported for 10 minute

async def send_telegram_message(msg, photo_obj = None):
    bot = telegram.Bot(token=bot_token)
    if photo_obj is not None:
        await bot.send_photo(chat_id=chat_id, photo=photo_obj, caption=msg, parse_mode="HTML")
    else:
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

app = Flask(__name__)

clients_data = {}
storages_data = {}
weathers_data = {}

def is_all_alive():
    all_alive = True
    for client_id, client_data in clients_data.items():
        if client_data['alive_warning_flag']:
            all_alive = False
    
    return all_alive

def get_image_idx():
    image_idx = 0

    recent_cpu_loads = []
    for client_id, client_data in clients_data.items():
        recent_cpu_loads.append(client_data['cpu_load'][-1])

    if recent_cpu_loads:
        image_idx = int(max(recent_cpu_loads)/10)
        if image_idx > 10:
            image_idx = 10

    return image_idx

@app.route('/', methods=['GET'])
def index():
    cpu_chart_data = []
    mem_chart_data = []
    storage_chart_data = []
    weather_chart_data = []
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
    for location, weather_data in weathers_data.items():
        weather_chart_data.append({
            "label": f"{location}",
            "data": weather_data["temperature"]
        })
    weather_chart_data = json.dumps(weather_chart_data)

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

    storage_rows = []
    for storage_id, storage_data in storages_data.items():
        storage_rows.append(
            f"<tr><td>{storage_id}</td>"
            f"<td>{storage_data['usage']}</td></tr>"
        )
    storage_html = "<table><tr><th>Storage ID</th><th>Usage</th></tr>"
    storage_html += "".join(storage_rows)
    storage_html += "</table>"

    weather_rows = []
    for location, weather_data in weathers_data.items():
        weather_rows.append(
            f"<tr><td>{location}</td>"
            f"<td>{weather_data['temperature'][-1]}</td>"
            f"<td>{weather_data['pressure'][-1]}</td>"
        )
    weather_html = "<table><tr><th>Location</th><th>Temperature</th><th>Pressure</th>"
    weather_html += "".join(weather_rows)
    weather_html += "</table>"

    chart_html = f"""
        <canvas id="cpuChart" width="400" height="200"></canvas>
        <canvas id="memChart" width="400" height="200"></canvas>
        <canvas id="storageChart" width="400" height="200"></canvas>
        <canvas id="weatherChart" width="400" height="200"></canvas>
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

            var ctx4 = document.getElementById('weatherChart').getContext('2d');
            var weatherChart = new Chart(ctx4, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(list(range(10)))},
                    datasets: {weather_chart_data}
                }},
                options: {{
                    responsive: false,
                }}
            }});
        </script>
    """

    if is_all_alive():
        image_html = '<img src="static/{:02d}.png" width=128>'.format(get_image_idx())
    else:
        image_html = '<img src="static/mia.png" width=128>'

    return f"<html><body>{image_html}{chart_html}{table_html}{storage_html}{weather_html}</body></html>"

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
            'storage_warning_flag': False,
            'last_report_time': time.time(),
            'alive_warning_flag': False
        }
    clients_data[client_id]['cpu_load'].append(content['cpu_load'])
    clients_data[client_id]['memory_usage'].append(content['memory_usage'])
    clients_data[client_id]['storage_usage'].append(content['storage_usage'])
    clients_data[client_id]['last_report_time'] = time.time()

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

@app.route('/weather', methods=['POST'])
def weather():
    for content in request.json:
        location = content['location']
        if location not in weathers_data:
            weathers_data[location] = {
                'temperature': [],
                'pressure': []
            }

        weathers_data[location]['temperature'].append(content['temperature'])
        weathers_data[location]['pressure'].append(content['pressure'])

        weathers_data[location]['temperature'] = weathers_data[location]['temperature'][-10:]
        weathers_data[location]['pressure'] = weathers_data[location]['pressure'][-10:]

    return jsonify({'status': 'ok'})

@app.route('/send_summary', methods=['POST'])
def send_summary():
    global image_idx

    if not bot_token or not chat_id:
        return jsonify({'status': 'error', 'message': 'Missing Telegram bot token or chat ID'})

    message = '-=: Hourly Report :=-\n'
    for client_id, client_data in clients_data.items():
        message += f"+ <b>{client_id}</b>\n<pre>CPU load: {client_data['cpu_load'][-1]}\nMemory usage: {client_data['memory_usage'][-1]}\nStorage usage: {client_data['storage_usage'][-1]}</pre>\n"

    if is_all_alive():
        image_path = "{}/static/{:02d}.png".format(project_abs_path, get_image_idx())
    else:
        image_path = "{}/static/mia.png".format(project_abs_path)

    asyncio.run(send_telegram_message(message, open(image_path, 'rb')))

    return jsonify({'status': 'ok'})

@app.route('/check_status', methods=['POST'])
def check_status():
    now = time.time()

    message = ''
    for client_id, client_data in clients_data.items():
        if now - client_data['last_report_time'] > NOTIFY_THRESHOLD:
            if not client_data['alive_warning_flag']:
                message += f"<b>MIA</b>\n{client_id} has not reported in the last 10 minutes.\n"
                client_data['alive_warning_flag'] = True
        else:
            if client_data['alive_warning_flag']:
                message += f"{client_id} is now back to online.\n"
            client_data['alive_warning_flag'] = False
    
    if len(message) > 0:
        asyncio.run(send_telegram_message(message))

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

