from datetime import datetime, timedelta
from typing import *

import requests

from constants import WorkoutCategory, AccessTokenError
from helpers import load_secrets_into_environment


class Workouts:
    """
    A class to fetch workout data from the Withings API.
    """

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.url = "https://wbsapi.withings.net/v2/measure"
        self.start_date: datetime = None
        self.end_date: datetime = None

    def _get_workout_data(
            self, start_date: datetime = None, end_date: datetime = None,
            include_walking_as_workout: bool = False
    ) -> List[Dict]:
        """
        Gets the workout data from the Withings API for the previous month.

        Returns
            list: A list of workout data for the previous month.
        """
        today = datetime.today()
        self.start_date = start_date or datetime(today.year, today.month - 1, 1) if today.month > 1 else datetime(
            today.year - 1, 12, 1)
        self.end_date = end_date or datetime(today.year, today.month, 1) - timedelta(days=1)
        print(
            f"Getting workout data between {self.start_date.strftime('%Y-%m-%d')} "
            f"and {self.end_date.strftime('%Y-%m-%d')}"
        )

        params = {
            "action": "getworkouts",
            "startdateymd": self.start_date.strftime("%Y-%m-%d"),
            "enddateymd": self.end_date.strftime("%Y-%m-%d"),
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.post(self.url, params=params, headers=headers)

        data = response.json()

        if response.status_code == 200 and data["status"] == 0:
            if not include_walking_as_workout:
                print("Excluding walking as a workout.")
                return [
                    workout for workout in data["body"]["series"]
                    if workout["category"] != WorkoutCategory.Walking.value
                ]
            else:
                return data["body"]["series"]
        else:
            raise AccessTokenError(
                f"Error fetching workout data. Please check your access token and try again."
                f"\n{data}"
            )

    def count_workouts(self, start_date: datetime = None, end_date: datetime = None) -> Dict[WorkoutCategory, int]:
        """
        Counts the number of workouts per category for the previous month and prints the results.
        """
        workout_data = self._get_workout_data(start_date, end_date)

        workouts_per_category = {}
        for workout in workout_data:
            workout_category = WorkoutCategory(int(workout["category"]))
            workouts_per_category[workout_category] = workouts_per_category.get(workout_category, 0) + 1

        print(f"\nWorkout Data for {self.start_date.strftime('%d %B %Y')} to {self.end_date.strftime('%d %B %Y')}:")
        for category, count in workouts_per_category.items():
            print(f"{category.name}: {count}")
        return workouts_per_category


if __name__ == "__main__":
    load_secrets_into_environment()
    access_token = input("Enter your access token:")
    wos = Workouts(access_token)
    wos.count_workouts()
