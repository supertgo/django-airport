import numpy as np
import pandas as pd
from django.core.management import BaseCommand

from app_core.models import Airport
from app_api.views import api_get_airports


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = {
            "model": "Airport",
            "success": False,
            "information": None,
            "n_records_updated": 0,
            "n_records_created": 0
        }

    def handle(self, *args, **options):
        self.log["information"] = self.get_api_data()
        if self.log["information"] is not None:
            self.stdout.write(self.style.ERROR("Failed to fetch API data."))
            return

        self.divide_airport_data()

        if self.domestic_airport.shape[0] > 0:
            self.log["n_records_created"] = self.create_airports()

        if self.data_to_update.shape[0] > 0:
            self.log["n_records_updated"] = self.update_airports()

        n_records_created = self.log.get('n_records_created', {})

        n_records_updated = self.log.get('n_records_updated', 0)

        self.log["success"] = True


        self.stdout.write(
            self.style.SUCCESS(
                f"{n_records_created} records created."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"{n_records_updated} records updated.")
        )
        self.stdout.write(
            self.style.SUCCESS("Data synchronization completed successfully.")
        )

    def get_api_data(self):
        api_get_airports_response = api_get_airports()

        if isinstance(api_get_airports_response, str):
            self.log["details"] = str(f"API request error: {api_get_airports_response}")
            return

        domestic_airport_data = [
            api_get_airports_response[key] for key in api_get_airports_response
        ]

        self.domestic_airport = pd.DataFrame(domestic_airport_data)

    def create_airports(self):
        result = {}
        batch_size = 500

        objs = self.domestic_airport.replace({np.nan: None}).to_dict("records")

        ins_list = [Airport(**vals) for vals in objs]

        try:
            Airport.objects.bulk_create(ins_list, batch_size)
            result = len(objs)
        except Exception as err:
            result["error"] = True
            result[
                "information"
            ] = f"Failed to insert data at Airport Model: {str(err)}"
        return result

    def divide_airport_data(self):
        merged_data = pd.merge(
            self.domestic_airport,
            self.retrieves_current_data,
            how="left",
            on="iata",
            suffixes=["", "_db"],
        )

        columns = [col for col in merged_data.columns if not col.endswith("_db")]

        self.domestic_airport = (
            merged_data.loc[merged_data["id"].isna(), columns].drop(columns=["id"]).reset_index(drop=True)
        )

        self.data_to_update = merged_data.loc[merged_data["id"].notna(), :].pipe(
            self.filter_changed_columns
        )

    def update_airports(self):
        batch_size = 500
        objs = self.data_to_update.replace({np.nan: None}).to_dict("records")

        try:
            Airport.objects.bulk_update(
                [Airport(**vals) for vals in objs],
                ["iata", "city", "lat", "lon", "state"],
                batch_size,
            )
            return len(objs)
        except Exception as err:
            print.error(f"Failed to update airports data: {err}")
            return 0

    def filter_changed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()

        for db_column in [col for col in df.columns if col.endswith("_db")]:
            new_values = df[db_column.replace("_db", "")]
            db_values = df[db_column]

            df[db_column + "_changed"] = np.where(
                (new_values.notna()) & (new_values != db_values), True, False
            )

        rows_with_changes = df[[col for col in df.columns if col.endswith("_changed")]].any(axis=1)

        return df.loc[
            rows_with_changes, [col for col in df.columns if not col.endswith(("_db", "_changed"))]
        ].reset_index(drop=True)

    @property
    def retrieves_current_data(self):
        columns = ["id", "iata", "city", "lat", "lon", "state"]
        qs = Airport.objects.values_list(*columns)
        df = pd.DataFrame(list(qs), columns=columns)
        float_columns = ["lat", "lon"]

        for col in float_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(
                "float", errors="ignore"
            )
        return df


if __name__ == "__main__":
    Command().handle()
