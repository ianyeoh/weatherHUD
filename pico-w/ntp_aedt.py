import time
import ntptime


AEST_OFFSET = 60 * 60 * 10
SUMMERTIME_OFFSET = 60 * 60 * 1
    
# Sets RTC using NTP
def ntpSyncTime():
    # Initally set TZ to AEST
    # UTC to AEDT = + 10hr offset
    ntptime.server = '0.au.pool.ntp.org'
    ntptime.settime()

# Returns true if dt is in summer time, false if in standard time, assuming dt is in AEST
def isDST(dt):
    # dt = (year, month, mday, hour, minute, second, weekday, yearday)
    month = dt[1]
    
    # Nov, Dec, Jan, Feb, Mar are always summer time (UTC + 11hrs)
    if (month >= 11 or month <= 3):
        return True 
    # May, Jun, Jul, Aug, Sep are always standard time (UTC + 10hrs)
    if (month >= 5 and month <= 9):
        return False 
    
    date, hour, wday = dt[2], dt[3], dt[6]
    last_sunday = date - (wday + 1) # Date of the last Sunday
    
    # DST begins on the first Sunday at 2AM AEST (known as summer time)
    if month == 10:
        return ((last_sunday > 0) or (wday == 6 and hour >= 2))
        
    # DST ends on the first Sunday at 2AM AEST (known as standard time
    if month == 4:
        return ((last_sunday <= 0) and (wday != 6 or hour < 2))

# Returns AEDT datetime
def datetime():
    # Get current time in UTC, then convert to AEST
    now = time.localtime(time.mktime(time.gmtime()) + AEST_OFFSET)

    # Check if AEST time is in DST, return appropriate AEDT time
    if isDST(now):
        return time.localtime(time.mktime(now) + SUMMERTIME_OFFSET)
    return now

# Returns time in 24 hr time format (hrs:min)
def getTime():
    now = datetime()
    return '{:02d}:{:02d}'.format(now[3], now[4])

# Returns date as DD/MM/YYYY
def getDate():
    now = datetime()
    return '{:02d}/{:02d}/{}'.format(now[1], now[2], now[0])