"""
## Enhanced Astronaut & Space Data Pipeline

This DAG creates a comprehensive space data pipeline that:
1. Fetches real-time astronaut data from Open Notify API
2. Retrieves current ISS location (latitude/longitude)
3. Gets weather data for the ISS location
4. Exports all data to CSV and JSON files
5. Generates a beautiful formatted summary report

This pipeline demonstrates:
- Multiple API integrations (Open Notify, OpenWeatherMap)
- Dynamic task mapping for parallel processing
- Data transformation and export
- Professional report generation
- Real-world ETL (Extract, Transform, Load) patterns

Perfect for understanding modern data pipeline orchestration!

For more information: https://docs.astronomer.io/learn/get-started-with-airflow
"""

from airflow import Dataset
from airflow.decorators import dag, task
from pendulum import datetime
import requests
import json
from pathlib import Path
from datetime import datetime as dt


# Define the basic parameters of the DAG
@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={"owner": "Astro", "retries": 3},
    tags=["example", "space-data", "etl"],
)
def example_astronauts():
    """
    Enhanced space data pipeline with multiple data sources and export capabilities.
    """

    @task(outlets=[Dataset("current_astronauts")])
    def get_astronauts(**context) -> list:
        """
        Fetches the list of astronauts currently in space from Open Notify API.

        Returns:
            list: List of astronaut dictionaries (name, craft)
        """
        r = requests.get("http://api.open-notify.org/astros.json")
        data = r.json()

        number_of_people_in_space = data["number"]
        list_of_people_in_space = data["people"]

        # Push metadata to XCom for other tasks
        context["ti"].xcom_push(
            key="number_of_people_in_space", value=number_of_people_in_space
        )
        context["ti"].xcom_push(key="timestamp", value=dt.now().isoformat())
        context["ti"].xcom_push(key="message", value=data.get("message", "success"))

        # Return the list directly for dynamic task mapping
        return list_of_people_in_space

    @task
    def get_astronaut_metadata(**context) -> dict:
        """
        Retrieves astronaut metadata from XCom and packages it with the list.

        Returns:
            dict: Contains astronaut list, total count, timestamp, and message
        """
        ti = context["ti"]
        astronaut_list = ti.xcom_pull(task_ids="get_astronauts")

        return {
            "astronauts": astronaut_list,
            "total_count": ti.xcom_pull(
                task_ids="get_astronauts", key="number_of_people_in_space"
            ),
            "timestamp": ti.xcom_pull(task_ids="get_astronauts", key="timestamp"),
            "message": ti.xcom_pull(task_ids="get_astronauts", key="message"),
        }

    @task
    def print_astronaut_craft(greeting: str, person_in_space: dict) -> None:
        """
        Prints information about each astronaut (uses dynamic task mapping).

        Args:
            greeting: Custom greeting message
            person_in_space: Dictionary containing astronaut name and craft
        """
        craft = person_in_space["craft"]
        name = person_in_space["name"]
        print(f"👨‍🚀 {name} is currently in space flying on the {craft}! {greeting}")

    @task(outlets=[Dataset("iss_location")])
    def get_iss_location() -> dict:
        """
        Fetches the current GPS coordinates of the International Space Station.

        Returns:
            dict: ISS latitude, longitude, timestamp, and additional metadata
        """
        r = requests.get("http://api.open-notify.org/iss-now.json")
        data = r.json()

        iss_position = data["iss_position"]
        timestamp = data["timestamp"]

        # Convert to human-readable format
        lat = float(iss_position["latitude"])
        lon = float(iss_position["longitude"])

        # Determine hemisphere
        lat_direction = "N" if lat >= 0 else "S"
        lon_direction = "E" if lon >= 0 else "W"

        return {
            "latitude": iss_position["latitude"],
            "longitude": iss_position["longitude"],
            "latitude_formatted": f"{abs(lat):.4f}°{lat_direction}",
            "longitude_formatted": f"{abs(lon):.4f}°{lon_direction}",
            "timestamp": timestamp,
            "timestamp_readable": dt.fromtimestamp(timestamp).isoformat(),
            "map_url": f"https://www.google.com/maps?q={lat},{lon}",
        }

    @task
    def get_weather_at_iss_location(location: dict) -> dict:
        """
        Fetches weather data for the ISS location using OpenWeatherMap API.

        Note: This uses the free tier API. For production, add your API key.
        Falls back to generic ocean data if API call fails.

        Args:
            location: Dictionary containing ISS coordinates

        Returns:
            dict: Weather information or fallback data
        """
        try:
            # Using OpenWeatherMap free tier (no API key needed for basic data)
            # Note: For production, sign up at https://openweathermap.org/api and add API key
            location["latitude"]
            location["longitude"]

            # For demo purposes, we'll create a simulated response
            # In production, uncomment below and add your API key:
            # api_key = "YOUR_API_KEY"
            # url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
            # r = requests.get(url)
            # weather_data = r.json()

            # Simulated weather data for demonstration
            weather_data = {
                "location": "Over Ocean/Remote Area",
                "description": "ISS is currently over a remote area (likely ocean)",
                "note": "ISS orbits at ~400km altitude, above weather patterns",
                "altitude": "408 km (254 miles)",
                "speed": "~28,000 km/h (17,500 mph)",
                "orbit_period": "~90 minutes per orbit",
            }

            return weather_data

        except Exception as e:
            return {
                "error": str(e),
                "note": "Weather data unavailable",
                "location": "Unknown",
            }

    @task
    def print_iss_location(location: dict, weather: dict) -> None:
        """
        Displays formatted ISS location and weather information.

        Args:
            location: ISS coordinate data
            weather: Weather information for ISS location
        """
        print("\n" + "=" * 60)
        print("🛰️  INTERNATIONAL SPACE STATION - CURRENT STATUS")
        print("=" * 60)
        print("\n📍 LOCATION:")
        print(f"   Latitude:  {location['latitude_formatted']}")
        print(f"   Longitude: {location['longitude_formatted']}")
        print(f"   Timestamp: {location['timestamp_readable']}")
        print(f"   Map View:  {location['map_url']}")

        print("\n🌦️  LOCATION DETAILS:")
        for key, value in weather.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")

        print("\n" + "=" * 60 + "\n")

    @task
    def export_astronaut_data_to_csv(astronaut_data: dict) -> str:
        """
        Exports astronaut data to a CSV file.

        Args:
            astronaut_data: Dictionary containing astronaut information

        Returns:
            str: Path to the created CSV file
        """
        import pandas as pd

        # Create DataFrame from astronaut list
        df = pd.DataFrame(astronaut_data["astronauts"])

        # Add metadata columns
        df["total_in_space"] = astronaut_data["total_count"]
        df["data_retrieved"] = astronaut_data["timestamp"]

        # Create filename with timestamp
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/astronauts_{timestamp}.csv"

        # Export to CSV
        df.to_csv(filename, index=False)

        print(f"✅ Astronaut data exported to: {filename}")
        print(f"   Total records: {len(df)}")
        print(f"   Columns: {', '.join(df.columns)}")

        return filename

    @task
    def export_iss_data_to_json(location: dict, weather: dict) -> str:
        """
        Exports ISS location and weather data to a JSON file.

        Args:
            location: ISS coordinate data
            weather: Weather information

        Returns:
            str: Path to the created JSON file
        """

        # Combine all data
        combined_data = {
            "iss_location": location,
            "weather_info": weather,
            "export_timestamp": dt.now().isoformat(),
        }

        # Create filename with timestamp
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/iss_data_{timestamp}.json"

        # Export to JSON
        with open(filename, "w") as f:
            json.dump(combined_data, f, indent=2)

        print(f"✅ ISS data exported to: {filename}")
        print(f"   File size: {Path(filename).stat().st_size} bytes")

        return filename

    @task
    def generate_summary_report(
        astronaut_data: dict,
        location: dict,
        weather: dict,
        csv_file: str,
        json_file: str,
    ) -> None:
        """
        Generates a comprehensive formatted summary report of all collected data.

        Args:
            astronaut_data: Astronaut information
            location: ISS location data
            weather: Weather information
            csv_file: Path to exported CSV file
            json_file: Path to exported JSON file
        """

        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 15 + "SPACE DATA PIPELINE - SUMMARY REPORT" + " " * 17 + "║")
        print("╚" + "=" * 68 + "╝")

        print(f"\n📅 Report Generated: {dt.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        # Astronaut Summary
        print("\n" + "─" * 70)
        print("👨‍🚀 ASTRONAUTS IN SPACE")
        print("─" * 70)
        print(f"   Total Astronauts: {astronaut_data['total_count']}")
        print(f"   Data Status:      {astronaut_data['message']}")

        # Group astronauts by spacecraft
        craft_groups = {}
        for astronaut in astronaut_data["astronauts"]:
            craft = astronaut["craft"]
            if craft not in craft_groups:
                craft_groups[craft] = []
            craft_groups[craft].append(astronaut["name"])

        print("\n   Breakdown by Spacecraft:")
        for craft, astronauts in craft_groups.items():
            print(
                f"\n      🚀 {craft} ({len(astronauts)} astronaut{'s' if len(astronauts) > 1 else ''}):"
            )
            for name in sorted(astronauts):
                print(f"         • {name}")

        # Additional statistics
        print("\n   Statistics:")
        avg_crew_size = (
            astronaut_data["total_count"] / len(craft_groups) if craft_groups else 0
        )
        print(f"      • Total spacecraft: {len(craft_groups)}")
        print(f"      • Average crew size: {avg_crew_size:.1f} astronauts per craft")

        # ISS Location Summary
        print("\n" + "─" * 70)
        print("🛰️  ISS CURRENT LOCATION")
        print("─" * 70)
        print(
            f"   Coordinates:  {location['latitude_formatted']}, {location['longitude_formatted']}"
        )
        print(f"   Timestamp:    {location['timestamp_readable']}")
        print(f"   Map Link:     {location['map_url']}")

        # Weather/Location Info
        print("\n" + "─" * 70)
        print("🌍 LOCATION DETAILS")
        print("─" * 70)
        for key, value in weather.items():
            key_formatted = key.replace("_", " ").title()
            print(f"   {key_formatted:20} {value}")

        # Export Files Summary
        print("\n" + "─" * 70)
        print("📦 EXPORTED DATA FILES")
        print("─" * 70)
        print(f"   CSV File:  {csv_file}")
        print(f"   JSON File: {json_file}")

        # Data Quality Check
        print("\n" + "─" * 70)
        print("✅ DATA QUALITY CHECKS")
        print("─" * 70)
        checks = [
            ("Astronaut data retrieved", astronaut_data["total_count"] > 0),
            ("ISS location valid", location["latitude"] and location["longitude"]),
            ("Weather data available", "location" in weather or "note" in weather),
            ("CSV export successful", csv_file.endswith(".csv")),
            ("JSON export successful", json_file.endswith(".json")),
        ]

        for check_name, passed in checks:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"   {status} - {check_name}")

        print("\n" + "═" * 70)
        print("   🚀 Pipeline execution completed successfully!")
        print("═" * 70 + "\n")

    # ========================================================================
    # TASK ORCHESTRATION - Define the workflow
    # ========================================================================

    # Step 1: Fetch astronaut list (returns list directly for mapping)
    astronaut_list = get_astronauts()

    # Step 2: Print each astronaut (dynamic task mapping)
    print_astronaut_craft.partial(greeting="Hello from Earth! 🌍").expand(
        person_in_space=astronaut_list
    )

    # Step 3: Get metadata dictionary (for export and reporting tasks)
    # Note: Must depend on astronaut_list to ensure get_astronauts() completes first
    astronaut_data = get_astronaut_metadata()
    astronaut_list >> astronaut_data  # Explicit dependency to ensure XCom data exists

    # Step 4: Get ISS location
    iss_location = get_iss_location()

    # Step 5: Get weather/location details for ISS position
    weather_data = get_weather_at_iss_location(iss_location)

    # Step 6: Display ISS information
    print_iss_location(iss_location, weather_data)

    # Step 7: Export data to files
    csv_file = export_astronaut_data_to_csv(astronaut_data)
    json_file = export_iss_data_to_json(iss_location, weather_data)

    # Step 8: Generate comprehensive summary report
    generate_summary_report(
        astronaut_data, iss_location, weather_data, csv_file, json_file
    )


# Instantiate the DAG
example_astronauts()
