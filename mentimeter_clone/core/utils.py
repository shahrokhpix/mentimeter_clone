# core/utils.py

def get_max_surveys(subscription_type):
    """
    دریافت حداکثر تعداد نظرسنجی‌های مجاز بر اساس نوع اشتراک
    """
    limits = {
        'free': 2,
        'monthly': 5,
        'quarterly': 10,
        'semi_annual': float('inf'),
    }
    return limits.get(subscription_type, 0)
