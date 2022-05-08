#!/bin/sh
echo "Backup repo initialized"
restic init /backups
crond -f