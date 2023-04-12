#!/bin/bash
host="YOUR_SERVER_URL_HERE"

while true; do
    cpu_load=$(echo "$(awk '{print $1*100}' /proc/loadavg)")
    memory_usage=$(free | awk 'NR==2{printf "%.2f\n", $3/$2*100}')
    storage_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    client_id=$(hostname)
    
    data=$(cat <<EOF
{
    "client_id": "${client_id}",
    "cpu_load": ${cpu_load},
    "memory_usage": ${memory_usage},
    "storage_usage": ${storage_usage}
}
EOF
)

echo ${data}
    curl -X POST -H "Content-Type: application/json" -d "${data}" "${host}"

    sleep 60  # Wait for 1 minute before sending data again
done
