"""
Progress Analysis - Pure functions for analyzing user weight trends.

All functions are stateless and testable.
"""

from typing import List, Dict, Any, Tuple
from datetime import date


def calculate_weight_trend(
    weight_entries: List[Dict[str, Any]],
    period_days: int = 7
) -> Dict[str, Any]:
    """
    Calculate weight trend over a period.

    Args:
        weight_entries: List of weight dicts sorted by date (newest first)
        period_days: Number of days to analyze

    Returns:
        Trend analysis dict with avg, change, direction
    """
    if not weight_entries:
        return {'trend': 'unknown', 'avg_weight': 0, 'total_change': 0}

    # Filter entries within the period
    entries_in_period = filter_entries_by_date(weight_entries, period_days)

    if len(entries_in_period) < 2:
        return {
            'trend': 'stable',
            'avg_weight': entries_in_period[0]['weight'] if entries_in_period else 0,
            'total_change': 0,
            'entry_count': len(entries_in_period),
        }

    weights = [e['weight'] for e in entries_in_period]
    avg_weight = sum(weights) / len(weights)
    first_weight = entries_in_period[-1]['weight']  # oldest in the period
    last_weight = entries_in_period[0]['weight']    # newest
    total_change = last_weight - first_weight

    direction = 'unknown'
    if total_change < -0.5:
        direction = 'down'
    elif total_change > 0.5:
        direction = 'up'
    else:
        direction = 'stable'

    return {
        'trend': direction,
        'avg_weight': round(avg_weight, 2),
        'total_change': round(total_change, 2),
        'first_weight': first_weight,
        'last_weight': last_weight,
        'entry_count': len(entries_in_period),
    }


def analyze_calorie_adherence(
    daily_entries: List[Dict[str, Any]],
    target_calories: int,
    target_macros: Dict[str, int] = None
) -> Dict[str, Any]:
    """
    Analyze how closely user adhered to calorie targets.

    Args:
        daily_entries: List of daily macro logs
        target_calories: Daily calorie target
        target_macros: Dict with protein, carbs, fat targets

    Returns:
        Adherence analysis dict
    """
    if not daily_entries or not target_calories:
        return {'adherence_rate': 0, 'avg_intake': 0, 'days_tracked': 0}

    deviations = []
    total_calories = 0

    for entry in daily_entries:
        consumed = entry.get('calories', 0)
        total_calories += consumed
        if consumed > 0:
            deviation = (consumed - target_calories) / target_calories
            deviations.append(deviation)

    days = len(daily_entries)
    avg_intake = total_calories / days

    # Adherence: within +/- 10% is considered adherent
    adherent_days = sum(
        1 for d in deviations if abs(d) <= 0.10
    )
    adherence_rate = (adherent_days / len(deviations) * 100) if deviations else 0

    trend = 'above' if avg_intake > target_calories * 1.05 else \
            'below' if avg_intake < target_calories * 0.95 else \
            'on_target'

    return {
        'adherence_rate': round(adherence_rate, 1),
        'avg_intake': int(avg_intake),
        'target_calories': target_calories,
        'deviation': round(avg_intake - target_calories, 0),
        'trend': trend,
        'days_tracked': days,
    }


def calculate_weekly_summary(
    weight_trend: Dict[str, Any],
    calorie_adherence: Dict[str, Any],
    training_days: int = 0
) -> Dict[str, Any]:
    """
    Generate a weekly analysis summary.

    Args:
        weight_trend: Output from calculate_weight_trend
        calorie_adherence: Output from analyze_calorie_adherence
        training_days: Number of training sessions in period

    Returns:
        Weekly summary dict
    """
    score = 0

    # Weight progress (0-30 points)
    if weight_trend['trend'] == 'down':
        score += 30  # Losing weight
    elif weight_trend['trend'] == 'stable':
        score += 25  # Maintenance
    elif weight_trend['trend'] == 'up':
        score += 10  # Gaining

    # Calorie adherence (0-50 points)
    adherence = calorie_adherence.get('adherence_rate', 0)
    score += adherence * 0.5

    # Training consistency (0-20 points)
    training_score = min(20, training_days * 4)  # 4 points per session
    score += training_score

    return {
        'overall_score': round(score, 1),
        'weight_analysis': weight_trend,
        'calorie_analysis': calorie_adherence,
        'training_consistency': f"{training_days} days",
    }


def filter_entries_by_date(
    entries: List[Dict[str, Any]],
    days: int
) -> List[Dict[str, Any]]:
    """
    Filter entries to only those within the last N days.
    Handles both date objects and ISO date strings.

    Args:
        entries: List of dicts with 'date' field
        days: Number of days to filter

    Returns:
        Filtered entries
    """
    cutoff = date.today().replace(day=date.today().day - days) if days < 365 else None

    if cutoff is None:
        return entries

    filtered = []
    for entry in entries:
        entry_date = entry.get('date')
        if isinstance(entry_date, date) and entry_date >= cutoff:
            filtered.append(entry)
        elif isinstance(entry_date, str):
            try:
                parsed = date.fromisoformat(entry_date)
                if parsed >= cutoff:
                    filtered.append(entry)
            except (ValueError, TypeError):
                continue

    return sorted(filtered, key=lambda x: x.get('date', ''), reverse=True)
