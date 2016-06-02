@echo off
set PATH=%PATH%;C:\adb
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
adb forward tcp:8080 tcp:8080
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=127.0.0.1
pause