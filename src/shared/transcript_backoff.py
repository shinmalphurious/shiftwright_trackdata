def transcript_backoff_minutes(
    attempts
):

    schedule = [
        30,
        120,
        360,
        720,
        1440
    ]

    if attempts >= len(schedule):
        return schedule[-1]

    return schedule[attempts]
