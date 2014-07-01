#!/bin/bash
#usage stop-play-app.sh app-name
start-stop-daemon --chuid play -K -p /home/play/$1/RUNNING_PID