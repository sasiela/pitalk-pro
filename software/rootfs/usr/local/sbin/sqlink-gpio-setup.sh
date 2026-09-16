#!/bin/bash

set -e

GPIO=536
BASE=/sys/class/gpio
PIN="$BASE/gpio$GPIO"

if [ ! -e "$PIN" ]; then
    echo "$GPIO" > "$BASE/export"
fi

for i in $(seq 1 50); do
    [ -e "$PIN/value" ] && break
    sleep 0.1
done

if [ ! -e "$PIN/value" ]; then
    echo "ERROR: gpio$GPIO was not created"
    exit 1
fi

# No kernel inversion.
echo 0 > "$PIN/active_low"

# Set output HIGH atomically.
# HIGH = idle / squelch CLOSED.
echo high > "$PIN/direction"

chown sqlink:gpio "$PIN/value"
chmod 0664 "$PIN/value"

exit 0
