from unittest import case

from django import template
import jdatetime


register = template.Library()

PERSIAN_MONTHS = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]

@register.filter
def to_jalali_verbose(value, only=None):
    if not value:
        return ''
    try:
        jdate = jdatetime.datetime.fromgregorian(datetime=value)
        day = jdate.day
        month_name = PERSIAN_MONTHS[jdate.month - 1]
        year = jdate.year
        match only:
            case 'd': return str(day)
            case 'm': return str(month_name)
            case 'y': return str(year)
            case   _: return f"{day} {month_name} {year}"

    except Exception:
        return ''
