import os

import requests
from datetime import datetime, timedelta
from constants import WorkoutCategory
from typing import *
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np


class Workouts:
    """
    A class to fetch workout data from the Withings API.
    """
    def __init__(self, access_token):
        self.access_token = access_token
        self.url = "https://wbsapi.withings.net/v2/measure"

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
        start_date = start_date or datetime(today.year, today.month - 1, 1) if today.month > 1 else datetime(today.year - 1, 12, 1)
        end_date = end_date or datetime(today.year, today.month, 1) - timedelta(days=1)

        params = {
            "action": "getworkouts",
            "startdateymd": start_date.strftime("%Y-%m-%d"),
            "enddateymd": end_date.strftime("%Y-%m-%d"),
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

    def print_workout_data(self) -> None:
        workout_data = self._get_workout_data()
        print("Workout Data for the Previous Month:")
        for workout in workout_data:
            pprint(workout)

    def count_workouts_per_category(self) -> Dict[WorkoutCategory, int]:
        """
        Counts the number of workouts per category for the previous month and prints the results.
        """
        workout_data = self._get_workout_data()

        workouts_per_category = {}
        for workout in workout_data:
            workout_category = WorkoutCategory(int(workout["category"]))
            workouts_per_category[workout_category] = workouts_per_category.get(workout_category, 0) + 1

        print("Number of Workouts per category for the Previous Month:")
        for category, count in workouts_per_category.items():
            print(f"{category.name}: {count}")
        return workouts_per_category

    def plot_workouts_per_day(self) -> None:
        """
        Plots a bar chart showing the workout (indicating type by color) that the user did per day of the month.
        """
        workout_data = self._get_workout_data()
        days = [workout["date"] for workout in workout_data]
        categories = [workout["category"] for workout in workout_data]

        unique_days = sorted(list(set(days)))
        unique_categories = sorted(list(set(categories)))

        day_category_count = np.zeros((len(unique_days), len(unique_categories)))

        for day, category in zip(days, categories):
            day_index = unique_days.index(day)
            category_index = unique_categories.index(category)
            day_category_count[day_index, category_index] += 1

        bar_width = 0.35
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        color_map = {unique_categories[i]: colors[i % len(colors)] for i in range(len(unique_categories))}

        fig, ax = plt.subplots()
        for category_index, category in enumerate(unique_categories):
            ax.bar([day + bar_width * category_index for day in range(len(unique_days))],
                   day_category_count[:, category_index],
                   bar_width,
                   color=color_map[category],
                   label=WorkoutCategory(int(category)).name)

        ax.set_xlabel('Day of the Month')
        ax.set_ylabel('Workouts')
        ax.set_title('Workouts by Day and Category')
        ax.set_xticks(range(len(unique_days)))
        ax.set_xticklabels([str(day) for day in unique_days])
        ax.legend()

        plt.show()

    def plot_workouts_pie_chart(self) -> None:
        """
        Plots a pie chart showing the distribution of workout categories for the previous month.
        """
        workouts_per_category = self.count_workouts_per_category()
        categories = [category.name for category in workouts_per_category.keys()]
        workout_counts = list(workouts_per_category.values())

        fig, ax = plt.subplots()
        ax.pie(workout_counts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.title('Workout Categories Distribution for the Previous Month')
        plt.show()


if __name__ == "__main__":
    access_token = input("Your access token: ")
    wos = Workouts(access_token)
    # wos.print_workout_data()
    # wos.count_workouts_per_category()
    wos.plot_workouts_per_day()
    wos.plot_workouts_pie_chart()
