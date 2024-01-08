#!/bin/sh
scp launy@375lincoln.nyc:/home/launy/code/launmon/backupdb.sql .
rm laundry.db
sqlite3 laundry.db < backupdb.sql
