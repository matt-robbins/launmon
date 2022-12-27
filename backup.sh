#!/bin/sh
sqlite3 laundry.db ".dump" > backupdb.sql
