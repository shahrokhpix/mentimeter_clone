# core/utils.py

def get_max_surveys(subscription_type):
    limits = {
        'free': 2,
        'monthly': 5,
        'quarterly': 10,
        'semi_annual': float('inf'),
    }
    return limits.get(subscription_type, 0)
