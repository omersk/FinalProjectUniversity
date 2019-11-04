class timeUnion:
    def __init__(self, time):
        self.start_time = time.split(" --> ")[0]
        self.end_time = time.split(" --> ")[1]

    def union(self, other):
        arr_start = [self.start_time, other.start_time]
        arr_end = [self.end_time, other.end_time]
        arr_get_sec_start = [get_sec(self.start_time), get_sec(other.start_time)]
        arr_get_sec_end = [get_sec(self.end_time), get_sec(other.end_time)]
        start_index = arr_get_sec_start.index(min(arr_get_sec_start))
        end_index = arr_get_sec_end.index(max(arr_get_sec_end))
        start_time = arr_start[start_index]
        end_time = arr_end[end_index]
        return timeUnion(str(start_time) + " --> " + str(end_time))

    def __str__(self):
        return str(self.start_time) + " --> " + str(self.end_time)

    def getInitialTimeInSec(self):
        return get_sec(self.start_time)

    def getEndTimeInSec(self):
        return get_sec(self.end_time)


def get_sec(time_str):
    """Get Seconds from time."""
    h, m, sms = time_str.split(':')
    s, ms = sms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + 0.001 * int(ms)
