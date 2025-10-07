#!/bin/bash
# Полный тест всех команд на Этапах 1–4

echo "=== Starting full test ==="

pwd

ls
ls -l

cd /home
pwd
ls

cd user/docs
pwd
ls

cd ../../tmp
pwd
ls

find note.md
find missing.txt

tail /home/user.txt
tail -n 1 /tmp/log.txt

cd /etc
tail config.ini

cd /invalid
unknown_command

exit