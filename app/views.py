from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
import random
import concurrent.futures
import time

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

# Create your views here. python manage.py runserver 0.0.0.0:8000

CALLBACK_URL = "http://127.0.0.1:8000"

def get_syntheses_time(pk, token):
    time.sleep(1)
    days = random.randint(0, 8)
    hours = random.randint(1, 24)

    days_label = 'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'
    hours_label = 'час' if hours == 1 or (hours % 10 == 1 and hours != 11) else 'часа' if 1 < hours < 5 or (20 < hours % 100 < 25 and hours % 10 in [2, 3, 4]) else 'часов'

    # for hours in range(1, 25):
    #     hours_label = 'час' if hours == 1 or (hours % 10 == 1 and hours != 11) else 'часа' if 1 < hours < 5 or (20 < hours % 100 < 25 and hours % 10 in [2, 3, 4]) else 'часов'
    
    #     time_string = f"{hours} {hours_label}"
    #     print(time_string)

    return {
        "id": pk,
        "token": token,
        "time": days + ' ' + days_label + ', ' + hours + ' ' + hours_label
    }
    
def syntheses_time_callback(task):
    try:
        result = task.result()
    except concurrent.futures._base.CancelledError:
        return
    

    if (random.randint(1, 5) == 3):
        # return
        result["time"] = "error"

    nurl = str(CALLBACK_URL + '/syntheses/' + str(result["id"]) +'/set_synthesis_time?time='  + result["time"])
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + str(result["token"])}

    requests.put(nurl, json={}, timeout=3, headers=headers)


@api_view(['POST'])
def set_syntheses_time(request):
    print(request.data)

    if "token" not in request.data.keys():
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    if "token" in request.data.keys() and "pk" in request.data.keys():
        id = request.data["pk"]
        token = request.data["token"]
        task = executor.submit(get_syntheses_time, id, token)
        task.add_done_callback(syntheses_time_callback)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)