# views.py
from django.http import JsonResponse
from django.db import connection

def kbo_best_ba(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT team, position, name, batting_avg, rbi, hr, sb
            FROM kbo_2024_best_ba
            ORDER BY team, position
        """)
        rows = cursor.fetchall()

    data = [
        {
            "team": r[0],
            "position": r[1],
            "name": r[2],
            "batting_avg": r[3],
            "rbi": r[4],
            "hr": r[5],
            "sb": r[6],
        }
        for r in rows
    ]
    return JsonResponse(data, safe=False)
