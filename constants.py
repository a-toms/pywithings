from enum import Enum


class WorkoutCategory(Enum):
    """
    We use this to connect Withings' different workout categories to the id
    that Withings uses for each category.
    """
    Walking = 1
    Running = 2
    Hiking = 3
    Cycling = 6
    Swimming = 7
    Surf = 8
    Kitesurf = 9
    Windsurf = 10
    Tennis = 12
    Pingpong = 13
    Squash = 14
    Badminton = 15
    Weights = 16
    Fitness = 17
    Elliptical = 18
    Pilates = 19
    Basketball = 20
    Soccer = 21
    Football = 22
    Rugby = 23
    Volleyball = 24
    Horseback_riding = 26
    Golf = 27
    Yoga = 28
    Dancing = 29
    Boxing = 30
    Ski = 34
    Snowboard = 35
    Other = 36
    Rowing = 187
    Zumba = 188
    Baseball = 191
    Handball = 192
    Hockey = 193
    Icehockey = 194
    Climbing = 195
    Iceskating = 196
    Indoor_Walking = 306
    Indoor_Running = 307
    Indoor_Cycling = 308
    Robot_Withings = 457


class AccessTokenError(Exception):
    def __init__(self, message="Access token has expired"):
        super().__init__(message)
