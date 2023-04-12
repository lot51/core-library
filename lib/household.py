import services


def get_daily_household_income():
    total_daily_income = 0
    for sim_info in services.active_household():
        for career in sim_info.career_tracker.careers.values():
            total_daily_income += career.get_daily_pay()
    return total_daily_income


def get_hourly_household_income():
    total_hourly_income = 0
    for sim_info in services.active_household():
        for career in sim_info.career_tracker.careers.values():
            total_hourly_income += career.get_hourly_pay()
    return total_hourly_income
