from django.utils import timezone
from django import template
import jdatetime
from django.db.models import DateTimeField


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


@register.filter
def is_new(value: DateTimeField):
    return (value and timezone.now() - value).days < 3


@register.filter
def commafy(value):
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value



@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Return current GET parameters updated with new ones from kwargs.
    Removes any params with empty values.
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        if v is None or v == '':
            query.pop(k, None)
        else:
            query[k] = v
    return query.urlencode()
