import re
from rest_framework.response import Response
import operator
from rest_framework import status
from django.db.models.fields.json import json
import requests
from datetime import datetime
from rest_framework.views import APIView
from app_core.works import core_check_if_airport_exists_db
from app_api.utils import calculate_harversine

from app_api.consts import (
    ERROR_AIRPORT_DOEST_NOT_EXITS,
    ERROR_BOTH_AIRPORTS_REQUIRED,
    ERROR_BOTH_DATES_REQUIRED,
    ERROR_EARLIER_DEPARTURE_DATE,
    ERROR_EARLIER_RETURN_DATE,
    ERROR_INVALID_IATA_CODE,
    ERROR_SAME_AIRPORTS,
    IATA_CODE_REGEX,
)

# Create your views here.
DOMESTIC_AIRPORTS_API_URL = (
    "https://stub.amopromo.com/air/airports/pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc"
)
DOMESTIC_AIRPORTS_API_USER = "demo"
DOMESTIC_AIRPORTS_API_PASSWORD = "swnvlD"

MOCK_AIRLINES_API_URL = (
    "http://stub.amopromo.com/air/search/pzrvlDwoCwlzrWJmOzviqvOWtm4dkvuc"
)
MOCK_AIRLINES_USER = "demo"
MOCK_AIRLINES_PASSWORD = "swnvlD"


def api_get_airports():
    try:
        response = requests.get(
            url=DOMESTIC_AIRPORTS_API_URL,
            auth=(DOMESTIC_AIRPORTS_API_USER, DOMESTIC_AIRPORTS_API_PASSWORD),
        )
        data_json = json.loads(response.content)
        return data_json
    except Exception as err:
        return str(err)


class FlightView(APIView):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get(self, request, *args, **kwargs) -> Response:
        self.origin = request.query_params.get("origin")
        self.destination = request.query_params.get("destination")
        self.departure_date = request.query_params.get("departure_date")
        self.return_date = request.query_params.get("return_date")

        error_query_message = self.validate_query()
        if error_query_message != "":
            return Response(
                {"error": error_query_message}, status=status.HTTP_400_BAD_REQUEST
            )

        error_query_airport = self.validate_airport()
        if error_query_airport != "":
            return Response(
                {"error": error_query_airport}, status=status.HTTP_404_NOT_FOUND
            )

        response = self.execute()

        # sort options by price low -> high
        response.sort(key=operator.itemgetter("price"))
        return Response({"options": response})

    def get_data_from_stub(self):
        going_url = f"{MOCK_AIRLINES_API_URL}/{self.origin}/{self.destination}/{self.departure_date}"
        self.going_flights_data = self._get_flight_data(going_url)

        return_url = f"{MOCK_AIRLINES_API_URL}/{self.destination}/{self.origin}/{self.return_date}"
        self.return_flights_data = self._get_flight_data(return_url)

    def validate_airport(self) -> str:
        if not core_check_if_airport_exists_db(self.origin):
            return ERROR_AIRPORT_DOEST_NOT_EXITS(self.origin)

        if not core_check_if_airport_exists_db(self.destination):
            return ERROR_AIRPORT_DOEST_NOT_EXITS(self.destination)

        return ""

    def validate_query(self) -> str:
        """This method returns a string with the respective error if the query was not set correctly, otherwise, it returns an empty string"""
        if not self.origin or not self.destination:
            return ERROR_BOTH_AIRPORTS_REQUIRED

        if self.origin == self.destination:
            return ERROR_SAME_AIRPORTS

        if not re.match(IATA_CODE_REGEX, self.origin) or not re.match(
            IATA_CODE_REGEX, self.destination
        ):
            return ERROR_INVALID_IATA_CODE

        if not self.return_date or not self.departure_date:
            return ERROR_BOTH_DATES_REQUIRED

        if (
            datetime.strptime(self.departure_date, "%Y-%m-%d").date()
            < datetime.now().date()
            if self.departure_date
            else True
        ):
            return ERROR_EARLIER_DEPARTURE_DATE

        if (
            datetime.strptime(self.return_date, "%Y-%m-%d")
            < datetime.strptime(self.departure_date, "%Y-%m-%d")
            if self.return_date
            else True
        ):
            return ERROR_EARLIER_RETURN_DATE

        return ""

    def execute(self):
        self.get_data_from_stub()
        self.all_going_flights = self.going_flights_data["options"]
        self.all_return_flights = self.return_flights_data["options"]

        for flight in self.all_going_flights:
            flight = self.calculate_params(flight)

        for flight in self.all_return_flights:
            flight = self.calculate_params(flight)

        result = []

        for going_flight in self.all_going_flights:
            for return_flight in self.all_return_flights:
                option = {}
                option["price"] = round(
                    return_flight["price"]["total"] + going_flight["price"]["total"], 2
                )
                option["going_flight"] = going_flight
                option["return_flight"] = return_flight
                result.append(option)

        return result

    def calculate_duration(self, meta):
        dep_time = datetime.strptime(meta["departure_time"], "%Y-%m-%dT%H:%M:%S")
        arr_time = datetime.strptime(meta["arrival_time"], "%Y-%m-%dT%H:%M:%S")

        duration = arr_time - dep_time
        duration_in_s = duration.total_seconds()
        return duration_in_s / 3600

    def define_price(self, price):
        if price["fare"] * 0.1 < 40.0:
            price["fees"] = 40.0
        else:
            price["fees"] = round(price["fare"] * 0.1, 2)
        price["total"] = round(price["fare"] + price["fees"], 2)

    def define_meta(self, meta):
        lat_origin = self.going_flights_data["summary"]["from"]["lat"]
        lon_origin = self.going_flights_data["summary"]["from"]["lon"]
        lat_destination = self.going_flights_data["summary"]["to"]["lat"]
        lon_destination = self.going_flights_data["summary"]["to"]["lon"]

        meta["meta"]["range"] = round(
            calculate_harversine(
                lat_origin, lon_origin, lat_destination, lon_destination
            ),
            2,
        )

        duration_in_hours = self.calculate_duration(meta)

        meta["meta"]["cruise_speed_kmh"] = round(
            meta["meta"]["range"] / duration_in_hours, 2
        )
        meta["meta"]["cost_per_km"] = round(
            meta["price"]["fare"] / meta["meta"]["range"], 2
        )

    def calculate_params(self, flight):
        self.define_price(flight["price"])
        self.define_meta(flight)

    def _get_flight_data(self, url):
        try:
            response = requests.get(
                url, auth=(MOCK_AIRLINES_USER, MOCK_AIRLINES_PASSWORD)
            )
            response.raise_for_status()

            return json.loads(response.content)
        except requests.RequestException as e:
            print(f"Error during API request: {e}")
            return None
