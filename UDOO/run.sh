#!/bin/bash

cd "$(dirname "$0")"

run() {
	pkill -f main.py 2>/dev/null
	./main.py &
}

while true; do
	inotifywait -r -e modify . && run
done &

run &

wait