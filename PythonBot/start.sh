#!/bin/bash
# Start node state server
node /StateService/index.js &
# BUGBUG: BLOCK FOR DEBUGGING - Uncomment above
#node /StateService/index.js 
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start Node State Service: $status"
  exit $status
fi

# Start the Bot
python3.6 /PythonBot/Bot.py &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start Bot: $status"
  exit $status
fi

while sleep 60; do
  ps aux |grep node |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep python3.6 |grep -q -v grep
  PROCESS_2_STATUS=$?
  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit 1
  fi
done