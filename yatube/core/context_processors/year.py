from datetime import date

# Сделал по заданию, но в проекте применено решение из джанго


def year(request):
    """Добавляет переменную с текущим годом."""
    now = date.today()
    now_year = now.year
    return {"year": now_year}
