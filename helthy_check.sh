#!/bin/sh
set -e;
if [[ `curl -V|wc -l` == 0 ]];then
    apk add curl;
fi
echo "###[date: `date +%Y%m%d-%H:%M:%S`] begin check......"
curl -L -k --socks5 127.0.0.1:10800 --connect-timeout 5 https://www.google.com||exit 1
echo ''
#curl -L -k --socks5 127.0.0.1:10800 --connect-timeout 5 https://telegram.org||exit 1
echo ''
echo "###[date: `date +%Y%m%d-%H:%M:%S`] end check."
