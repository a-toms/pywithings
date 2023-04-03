import os

import requests
from datetime import datetime, timedelta
from constants import WorkoutCategory
from typing import *
from pprint import pprint
import turtle


class Workouts:
    """
    A class to fetch workout data from the Withings API.
    """
    def __init__(self, access_token):
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
        self.start_date = start_date or datetime(today.year, today.month - 1, 1) if today.month > 1 else datetime(today.year - 1, 12, 1)
        self.end_date = end_date or datetime(today.year, today.month, 1) - timedelta(days=1)

        params = {
            "action": "getworkouts",
            "startdateymd": self.start_date.strftime("%Y-%m-%d"),
            "enddateymd": self.end_date.strftime("%Y-%m-%d"),
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(self.url, params=params, headers=headers)

        if response.status_code == 200:
            workout_data = response.json()
            if not include_walking_as_workout:
                print("Excluding walking as a workout.")
                return [
                    workout for workout in workout_data["body"]["series"]
                    if workout["category"] != WorkoutCategory.Walking.value
                ]
            else:
                return workout_data["body"]["series"]
        else:
            print("Error fetching workout data. Please check your access token and try again.")

    def count_workouts_per_category(self) -> Dict[WorkoutCategory, int]:
        """
        Counts the number of workouts per category for the previous month and prints the results.
        """
        workout_data = self._get_workout_data()

        workouts_per_category = {}
        for workout in workout_data:
            workout_category = WorkoutCategory(int(workout["category"]))
            workouts_per_category[workout_category] = workouts_per_category.get(workout_category, 0) + 1

        print(f"\nWorkout Data for {self.start_date.strftime('%d %B %Y')} to {self.end_date.strftime('%d %B %Y')}:")
        for category, count in workouts_per_category.items():
            print(f"{category.name}: {count}")
        return workouts_per_category


if __name__ == "__main__":
    access_token = input("Your access token: ")
    wos = Workouts(access_token)
    wos.count_workouts_per_category()
