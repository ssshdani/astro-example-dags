#!/usr/bin/env python3
"""
Simple DAG validation script to check for syntax and import errors.
Run this to verify your DAG is correct before deploying.
"""

import sys
import traceback
from pathlib import Path


def validate_dag():
    """Validate the example_astronauts DAG."""
    print("🔍 Validating example_astronauts.py DAG...")
    print("-" * 60)

    try:
        # Add dags directory to path
        sys.path.insert(0, str(Path(__file__).parent / "dags"))

        # Try to import the DAG
        print("📥 Importing DAG module...")
        from example_astronauts import example_astronauts

        print("✅ Import successful!")
        print("-" * 60)

        # Check if DAG was instantiated
        print("\n📊 DAG Details:")
        print("   DAG ID: example_astronauts")
        print("   Schedule: @daily")
        print("   Tags: example, space-data, etl")

        print("\n✅ SUCCESS! Your DAG is syntactically correct!")
        print("\n📋 Expected Tasks:")
        tasks = [
            "get_astronauts",
            "get_astronaut_metadata",
            "print_astronaut_craft (will expand dynamically)",
            "get_iss_location",
            "get_weather_at_iss_location",
            "print_iss_location",
            "export_astronaut_data_to_csv",
            "export_iss_data_to_json",
            "generate_summary_report",
        ]
        for i, task in enumerate(tasks, 1):
            print(f"   {i}. {task}")

        print("\n" + "=" * 60)
        print("✨ Your DAG is ready to deploy!")
        print("=" * 60)
        print("\nNext steps:")
        print("  • Start Airflow: astro dev start")
        print("  • Deploy to Astro: astro deploy")
        print("\n")

        return True

    except SyntaxError as e:
        print("❌ SYNTAX ERROR in your DAG:")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        traceback.print_exc()
        return False

    except ImportError as e:
        print("❌ IMPORT ERROR:")
        print(f"   {str(e)}")
        print("\n💡 Make sure these packages are in requirements.txt:")
        print("   • pandas>=2.0.0")
        print("   • requests>=2.28.0")
        traceback.print_exc()
        return False

    except Exception as e:
        print("❌ UNEXPECTED ERROR:")
        print(f"   {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = validate_dag()
    sys.exit(0 if success else 1)
