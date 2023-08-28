from app_core.models import Airport


def core_check_if_airport_exists_db(airport_iata) -> bool:
    return Airport.objects.filter(iata=airport_iata).exists()
