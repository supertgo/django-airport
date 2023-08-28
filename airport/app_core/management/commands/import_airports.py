from datetime import datetime
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
            "n_records_inserted": 0,
            "n_records_updated": 0,
            "details": None,
            "started_at": datetime.utcnow(),
            "finished_at": None,
        }

    def handle(self, *args, **options):
        self.log["details"] = self.get_api_data()
        if self.log["details"] is not None:
            self.log["finished_at"] = datetime.utcnow()
            self.stdout.write(self.style.ERROR("Failed to fetch API data."))
            return

        self.segregate_data_for_action()

        if self.domestic_airport.shape[0] > 0:
            self.log["n_records_inserted"] = self.load_data()

        if self.data_to_update.shape[0] > 0:
            self.log["n_records_updated"] = self.update_data()

        self.log["success"] = True
        self.log["finished_at"] = datetime.utcnow()
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

    def load_data(self):
        result = {}
        batch_size = 500

        objs = self.domestic_airport.replace({np.nan: None}).to_dict("records")

        ins_list = [Airport(**vals) for vals in objs]

        try:
            Airport.objects.bulk_create(ins_list, batch_size)
            result["inserted"] = len(objs)
        except Exception as err:
            result["error"] = True
            result["details"] = f"Failed to insert data at Airport Model: {str(err)}"
        return result

    def segregate_data_for_action(self):
        """Compares the inputted dataframe data to the existing data on the recipient model"""
        df = pd.merge(
            self.domestic_airport,
            self.retrieves_current_data,
            how="left",
            on="iata",
            suffixes=["", "_db"],
        )

        columns = [col for col in df.columns if not col.endswith("_db")]

        self.domestic_airport = (
            df.loc[df["id"].isna(), columns].drop(columns=["id"]).reset_index(drop=True)
        )

        self.data_to_update = df.loc[df["id"].notna(), :].pipe(
            self.filter_changed_values
        )

    def update_data(self):
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

    def filter_changed_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """This methods returns only the data that is new in comparison to the existing data"""
        if df.empty:
            return pd.DataFrame()

        for col in [c for c in df.columns if c.endswith("_db")]:
            new_values = df[col.replace("_db", "")]

            db_values = df[col]

            df[col + "_test"] = np.where(
                (new_values.notna()) & (new_values != db_values), True, False
            )

        has_new_data = df[[c for c in df.columns if c.endswith("_test")]].any(axis=1)

        return df.loc[
            has_new_data, [c for c in df.columns if not c.endswith(("_db", "_test"))]
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
