from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CustomUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, StaticHTMLRenderer
from django.db.models import Avg, F, RowRange, Window, Q, ExpressionWrapper, DecimalField
import requests
from bs4 import BeautifulSoup
import json


class ListWeather(APIView):
    """
    Input start and end date for geting average weather
     :param request: datatime start_date, end_date
    :param format: YYYY-MM-DD
    :return: average temp per 6 Hours
    """


    def get(self, request, format=None):
        return Response({"start_date": "2020-09-01",
                         "end_date": "2020-10-03"
                         })