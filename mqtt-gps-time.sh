#!/bin/bash
set -e

MQTT_HOST="192.168.10.1"
MQTT_TOPIC="pico/gps"
THRESHOLD=60  # seconds

mosquitto_sub -h "$MQTT_HOST" -t "$MQTT_TOPIC" | while read -r msg
do
    # Extract time in format YYYY-MM-DD HH:MM:SS
    TIME=$(echo "$msg" | sed -n 's/.*time=\([0-9\-]*\)T\([0-9:]*\)Z.*/\1 \2/p')

    if [ -n "$TIME" ]; then
        # Convert to epoch seconds
        GPS_EPOCH=$(date -u -d "$TIME" +%s)
        SYS_EPOCH=$(date -u +%s)

        # Compute absolute difference
        DIFF=$(( GPS_EPOCH > SYS_EPOCH ? GPS_EPOCH - SYS_EPOCH : SYS_EPOCH - GPS_EPOCH ))

        if (( DIFF > THRESHOLD )); then
            echo "System time differs by $DIFF s. Updating time to GPS: $TIME (UTC)"
            date -u -s "$TIME"
            hwclock -w 2>/dev/null || true
        fi
    fi
done
