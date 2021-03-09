import json
from openap import Thrust, WRAP


def main():
    aircraft = json.loads(open("a320.json", 'r').read())
    print(aircraft)

