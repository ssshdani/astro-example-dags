"""
## Astronaut ETL example DAG

This DAG queries the list of astronauts currently in space from the
Open Notify API and prints each astronaut's name and flying craft.
It also fetches the current location of the ISS (International Space Station).

There are multiple tasks:
1. Get astronaut data from the API
2. Print each astronaut's information (using dynamic task mapping)
3. Get the current ISS location (latitude/longitude)
4. Print the ISS location with a map link

All tasks use the Open Notify API to fetch real-time space data.

For more explanation and getting started instructions, see our Write your
first DAG tutorial: https://docs.astronomer.io/learn/get-started-with-airflow

![Picture of the ISS](https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2010/02/space_station_over_earth/10293696-3-eng-GB/Space_Station_over_Earth_card_full.jpg)
"""

from airflow import Dataset
from airflow.decorators import dag, task
from pendulum import datetime
import requests


# Define the basic parameters of the DAG, like schedule and start_date
@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={"owner": "Astro", "retries": 3},
    tags=["example"],
)
def example_astronauts():
    # Define tasks
    @task(
        # Define a dataset outlet for the task. This can be used to schedule downstream DAGs when this task has run.
        outlets=[Dataset("current_astronauts")]
    )  # Define that this task updates the `current_astronauts` Dataset
    def get_astronauts(**context) -> list[dict]:
        """
        This task uses the requests library to retrieve a list of Astronauts
        currently in space. The results are pushed to XCom with a specific key
        so they can be used in a downstream pipeline. The task returns a list
        of Astronauts to be used in the next task.
        """
        r = requests.get("http://api.open-notify.org/astros.json")
        number_of_people_in_space = r.json()["number"]
        list_of_people_in_space = r.json()["people"]

        context["ti"].xcom_push(
            key="number_of_people_in_space", value=number_of_people_in_space
        )
        return list_of_people_in_space

    @task
    def print_astronaut_craft(greeting: str, person_in_space: dict) -> None:
        """
        This task creates a print statement with the name of an
        Astronaut in space and the craft they are flying on from
        the API request results of the previous task, along with a
        greeting which is hard-coded in this example.
        """
        craft = person_in_space["craft"]
        name = person_in_space["name"]

        print(f"{name} is currently in space flying on the {craft}! {greeting}")

    @task
    def get_iss_location() -> dict:
        """
        This task fetches the current location of the ISS (International Space Station)
        from the Open Notify API. Returns latitude, longitude, and timestamp.
        """
        r = requests.get("http://api.open-notify.org/iss-now.json")
        data = r.json()

        # Extract ISS position
        iss_position = data["iss_position"]
        timestamp = data["timestamp"]

        return {
            "latitude": iss_position["latitude"],
            "longitude": iss_position["longitude"],
            "timestamp": timestamp,
        }

    @task
    def print_iss_location(location: dict) -> None:
        """
        This task prints the current location of the ISS with coordinates
        and a link to view it on Google Maps.
        """
        print("🛰️  ISS Current Location:")
        print(f"   Latitude: {location['latitude']}")
        print(f"   Longitude: {location['longitude']}")
        print(f"   Timestamp: {location['timestamp']}")
        print(
            f"   View on map: https://www.google.com/maps?q={location['latitude']},{location['longitude']}"
        )

    # Use dynamic task mapping to run the print_astronaut_craft task for each
    # Astronaut in space
    astronaut_data = get_astronauts()
    print_astronaut_craft.partial(greeting="Hello! :)").expand(
        person_in_space=astronaut_data  # Define dependencies using TaskFlow API syntax
    )

    # Get ISS location and print it
    iss_location = get_iss_location()
    print_iss_location(iss_location)


# Instantiate the DAG
example_astronauts()
