import services


def get_household(household_id):
    if household_id is not None:
        return services.household_manager().get(household_id)


def get_daily_household_income(household=None):
    total_daily_income = 0
    if household is None:
        household = services.active_household()
    for sim_info in household:
        for career in sim_info.career_tracker.careers.values():
            total_daily_income += career.get_daily_pay()
    return total_daily_income


def get_hourly_household_income(household=None):
    total_hourly_income = 0
    if household is None:
        household = services.active_household()
    for sim_info in household:
        for career in sim_info.career_tracker.careers.values():
            total_hourly_income += career.get_hourly_pay()
    return total_hourly_income
