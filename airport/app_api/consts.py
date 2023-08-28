# Error messages for validation
ERROR_BOTH_AIRPORTS_REQUIRED = "Both origin and destination airports are required."
ERROR_BOTH_DATES_REQUIRED = "Both departure and return date must are required."
ERROR_SAME_AIRPORTS = "The origin and destination airport cannot be the same."
ERROR_EARLIER_DEPARTURE_DATE = "The departure date cannot be earlier than today's date."
ERROR_EARLIER_RETURN_DATE = "The return date cannot be earlier than the departure date."
ERROR_INVALID_IATA_CODE = "The IATA code must have 3 upper case digits."


def ERROR_AIRPORT_DOEST_NOT_EXITS(airport_iata):
    return f"The airport '{airport_iata}' does not exist"

# Regexs
IATA_CODE_REGEX = r"^[A-Z]{3}$"

