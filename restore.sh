#!/bin/sh
scp launy@launmon.ddns.net:/home/launy/code/launmon/backupdb.sql .
rm laundry.db
sqlite3 laundry.db < backupdb.sql
