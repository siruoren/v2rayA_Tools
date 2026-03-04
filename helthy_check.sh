#!/bin/sh
set -e;
apk add curl;
curl -L -k --socks5 127.0.0.1:10800 --connect-timeout 5 https://www.google.com||exit 1
