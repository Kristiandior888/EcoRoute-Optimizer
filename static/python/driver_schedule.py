from datetime import timedelta

MAX_CONTINUOUS_DRIVE = timedelta(hours=4.5)
BREAK_TIME = timedelta(minutes=45)
MAX_DAILY_DRIVE = timedelta(hours=9)
OVERNIGHT_REST = timedelta(hours=11)

def plan_driver_schedule(total_distance, speed):
    """
    total_distance: км
    speed: км/ч
    """
    total_time_hours = total_distance / speed
    total_time = timedelta(hours=total_time_hours)
    schedule = []
    continuous_drive = timedelta()
    daily_drive = timedelta()

    # Увеличиваем сегмент для лучшего распределения
    segment_time = timedelta(hours=2)  # Увеличили с 1 часа до 2
    traveled_time = timedelta()

    while traveled_time < total_time:
        next_segment = min(segment_time, total_time - traveled_time)

        # Проверяем необходимость перерыва
        if continuous_drive + next_segment > MAX_CONTINUOUS_DRIVE:
            schedule.append({"action": "break", "duration": BREAK_TIME})
            continuous_drive = timedelta()
            # После перерыва добавляем сегмент вождения
            drive_segment = min(segment_time, total_time - traveled_time)
            schedule.append({"action": "drive", "duration": drive_segment})
            traveled_time += drive_segment
            continuous_drive += drive_segment
            daily_drive += drive_segment
            continue

        # Проверяем необходимость ночевки
        if daily_drive + next_segment > MAX_DAILY_DRIVE:
            schedule.append({"action": "overnight_rest", "duration": OVERNIGHT_REST})
            daily_drive = timedelta()
            continuous_drive = timedelta()
            # После ночевки добавляем сегмент вождения
            drive_segment = min(segment_time, total_time - traveled_time)
            schedule.append({"action": "drive", "duration": drive_segment})
            traveled_time += drive_segment
            continuous_drive += drive_segment
            daily_drive += drive_segment
            continue

        # Обычное вождение
        schedule.append({"action": "drive", "duration": next_segment})
        traveled_time += next_segment
        continuous_drive += next_segment
        daily_drive += next_segment

    return schedule