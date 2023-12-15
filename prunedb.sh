#!/bin/sh
cd ~/code/launmon
sqlite3 laundry.db < sql/prune.sql
