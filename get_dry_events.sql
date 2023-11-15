SELECT time,endtime FROM (
	SELECT time,lead(time) OVER (ORDER BY time) endtime,washstart FROM (
		SELECT time,
			(lag(status) OVER (ORDER BY time) || status) 
				IN ('nonewash','noneboth','dryboth','drywash') washstart, 
			(lag(status) OVER (ORDER BY time) || status) 
				IN ('washnone','bothnone','bothdry','washdry') washend
		FROM events WHERE location = '4') 
	WHERE washstart > 0 OR washend > 0)
WHERE washstart > 0