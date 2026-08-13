"""Route calculation tools for RoadTrip Concierge agent."""


def calculate_route_metrics(
    origin: str,
    destination: str,
    starting_battery_pct: int = 90,
    vehicle_model: str = "Tesla Model Y",
) -> str:
    """Calculate driving distance, estimated drive time, battery consumption, and recommended charging stop duration.

    Args:
        origin: Starting location (e.g. 'San Francisco, CA').
        destination: Destination location (e.g. 'Lake Tahoe, CA' or 'Reno, NV').
        starting_battery_pct: Initial battery charge percentage (1-100, default: 90).
        vehicle_model: Model of electric vehicle (default: 'Tesla Model Y').

    Returns:
        Formatted summary of route metrics, energy usage, charging stop requirement, and estimated trip duration.
    """
    origin_clean = origin.lower()
    dest_clean = destination.lower()

    # Route estimates matrix for common Northern California driving routes
    routes_database = {
        ("san francisco", "lake tahoe"): {"miles": 200, "hours": 3.5},
        ("san francisco", "sacramento"): {"miles": 88, "hours": 1.5},
        ("san francisco", "reno"): {"miles": 218, "hours": 3.8},
        ("sacramento", "lake tahoe"): {"miles": 112, "hours": 2.0},
        ("sacramento", "reno"): {"miles": 132, "hours": 2.2},
        ("pleasanton", "sacramento"): {"miles": 78, "hours": 1.3},
        ("berkeley", "sacramento"): {"miles": 75, "hours": 1.2},
    }

    # Find closest matching route or calculate default estimate based on name length heuristic
    matched = None
    for (o, d), metrics in routes_database.items():
        if o in origin_clean and d in dest_clean:
            matched = metrics
            break
        elif d in origin_clean and o in dest_clean:
            matched = metrics
            break

    if matched:
        miles = matched["miles"]
        hours = matched["hours"]
    else:
        # Default fallback approximation: 120 miles, 2.0 hours
        miles = 120
        hours = 2.0

    # EV Consumption model (~0.28 kWh / mile for Model Y)
    battery_kwh_capacity = 75.0  # standard long range battery capacity
    kwh_consumed = miles * 0.28
    pct_consumed = round((kwh_consumed / battery_kwh_capacity) * 100)

    arrival_battery = starting_battery_pct - pct_consumed
    needs_charge = arrival_battery < 20

    charging_recommendation = ""
    if needs_charge:
        charge_needed_pct = 80 - arrival_battery
        charge_time_mins = round((charge_needed_pct / 100) * 35)  # 250kW V3 Supercharger rate
        charging_recommendation = (
            f"⚡ CHARGING REQUIRED: Arrival battery would drop to {arrival_battery}%.\n"
            f"   Recommendation: Stop at a 250kW Tesla Supercharger for ~{charge_time_mins} minutes "
            f"to recharge back to 80%."
        )
    else:
        charging_recommendation = (
            f"✅ NO CHARGE STOP REQUIRED: Estimated arrival battery is {arrival_battery}% "
            f"(above the 20% safety threshold)."
        )

    return (
        f"🚗 Route Metrics from {origin.title()} to {destination.title()} ({vehicle_model}):\n"
        f"• Total Distance: {miles} miles\n"
        f"• Estimated Drive Time: {hours:.1f} hours (without stops)\n"
        f"• Starting Battery: {starting_battery_pct}%\n"
        f"• Energy Used: ~{kwh_consumed:.1f} kWh ({pct_consumed}% battery drain)\n"
        f"• Estimated Arrival Battery: {arrival_battery}%\n\n"
        f"{charging_recommendation}"
    )
