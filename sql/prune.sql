DELETE FROM rawcurrent WHERE time < datetime('now','-1 month');
VACUUM;
