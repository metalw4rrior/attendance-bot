#!/bin/bash

cp ./telegram_bot.service /etc/systemd/system/
cp ./attendance_site.service /etc/systemd/system/

sleep 2

systemctl daemon-reload

systemctl enable telegram_bot.service
systemctl start telegram_bot.service
systemctl enable attendance_site.service
systemctl start attendance_site.service
