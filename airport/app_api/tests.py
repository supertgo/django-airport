from django.test import TestCase
from app_api.views import FlightView
from app_api.consts import (
    ERROR_AIRPORT_DOEST_NOT_EXITS,
    ERROR_BOTH_AIRPORTS_REQUIRED,
    ERROR_BOTH_DATES_REQUIRED,
    ERROR_INVALID_IATA_CODE,
    ERROR_SAME_AIRPORTS,
)


class TestFlightViewQuery(TestCase):
    def setUp(self):
        self.validator = FlightView()

    def test_iata_code(self):
        self.validator.origin = "INVALID_IATA"
        self.validator.destination = "ANOTHER_INVALID_IATA"
        self.assertEqual(self.validator.validate_query(), ERROR_INVALID_IATA_CODE)

    def test_iata_code_departure(self):
        self.validator.origin = "INVALID_IATA"
        self.validator.destination = "SJP"
        self.assertEqual(self.validator.validate_query(), ERROR_INVALID_IATA_CODE)

    def test_iata_code_arrival(self):
        self.validator.origin = "MGF"
        self.validator.destination = "ANOTHER_INVALID_IATA"
        self.assertEqual(self.validator.validate_query(), ERROR_INVALID_IATA_CODE)

    def test_both_airports_required(self):
        self.validator.origin = "POA"
        self.validator.destination = ""
        self.assertEqual(self.validator.validate_query(), ERROR_BOTH_AIRPORTS_REQUIRED)

    def test_both_dates_required(self):
        self.validator.origin = "BHZ"
        self.validator.destination = "POA"
        self.validator.departure_date = "2022-06-12"
        self.validator.return_date = ""
        self.assertEqual(self.validator.validate_query(), ERROR_BOTH_DATES_REQUIRED)

    def test_same_airports(self):
        self.validator.origin = "POA"
        self.validator.destination = "POA"
        self.validator.departure_date = "2022-06-12"
        self.validator.return_date = "2023-08-25"
        self.assertEqual(self.validator.validate_query(), ERROR_SAME_AIRPORTS)

    def test_airport_exists(self):
        self.validator.origin = "CZS"
        self.validator.destination = "POA"

        self.assertEqual(
            self.validator.validate_airport(),
            ERROR_AIRPORT_DOEST_NOT_EXITS(self.validator.origin),
        )
