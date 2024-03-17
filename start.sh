#!/bin/bash
#sh /home/shell/start-mongosh.sh &&
#cd /app &&
#tail -f /dev/null
echo "start"
flask run
echo "end"
tail -f /dev/null