@echo off
rem Run as administrator!

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Setting up forward to localhost:8080...
) else (
    echo You must run this script as administrator!
    goto end
)

set PATH=%PATH%;C:\adb
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
adb forward tcp:8080 tcp:8080
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=127.0.0.1
echo Done.

:end
pause