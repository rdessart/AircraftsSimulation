import json
from openap import Thrust, WRAP


def main():
    aircraft = json.loads(open("./data/a319.json", 'r').read())
    print(aircraft)


if __name__ == "__main__":
    main()
