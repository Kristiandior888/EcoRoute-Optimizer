from datetime import timedelta

MAX_CONTINUOUS_DRIVE = timedelta(hours=4.5)
BREAK_TIME = timedelta(minutes=45)
MAX_DAILY_DRIVE = timedelta(hours=9)
OVERNIGHT_REST = timedelta(hours=11)

def plan_driver_schedule(route_segments):
    schedule = []
    continuous_drive = timedelta()
    daily_drive = timedelta()

    for seg in route_segments:
        segment_time = seg["time"]

        # Ночёвка
        if daily_drive + segment_time > MAX_DAILY_DRIVE:
            schedule.append({"action": "overnight_rest", "duration": OVERNIGHT_REST})
            daily_drive = timedelta()
            continuous_drive = timedelta()

        # Перерыв
        if continuous_drive + segment_time > MAX_CONTINUOUS_DRIVE:
            schedule.append({"action": "break", "duration": BREAK_TIME})
            continuous_drive = timedelta()

        schedule.append(seg)
        continuous_drive += segment_time
        daily_drive += segment_time

    return schedule