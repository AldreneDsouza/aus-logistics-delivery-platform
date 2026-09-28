"""
carrier_scan_generator.py
Generates realistic carrier scan event files for Meridian Freight Group.
Produces CSV and JSON files simulating daily carrier feeds.
Deliberately injects data quality issues.
"""

import os
import json
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

fake = Faker('en_AU')

# --- Configuration ---
OUTPUT_DIR = "data/carrier_scans"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CARRIERS = {
    "CAR001": "auspost",
    "CAR002": "startrack",
    "CAR003": "teamglobal",
    "CAR004": "toll",
    "CAR005": "couriersplease",
}

# Each carrier uses different status codes — realistic messiness
CARRIER_STATUS_CODES = {
    "CAR001": ["PICKED_UP", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "FAILED", "RTO"],
    "CAR002": ["PU", "IT", "OFD", "DEL", "ATF", "RTO"],
    "CAR003": ["Collected", "InTransit", "OutForDelivery", "Delivered", "FailedAttempt", "Returned"],
    "CAR004": ["picked_up", "in_transit", "out_delivery", "delivered", "failed", "returned"],
    "CAR005": ["SCAN_PU", "SCAN_IT", "SCAN_OFD", "SCAN_DEL", "SCAN_FAIL", "SCAN_RTO"],
}


def generate_scan_events(carrier_id: str, carrier_name: str, num_events: int = 50) -> list:
    """Generate scan events for a single carrier."""
    events = []
    status_codes = CARRIER_STATUS_CODES[carrier_id]

    for _ in range(num_events):
        scan_time = datetime.now() - timedelta(hours=random.randint(0, 24))

        event = {
            "scan_id": fake.uuid4(),
            "carrier_id": carrier_id,
            "carrier_name": carrier_name,
            "order_id": f"ORD{random.randint(1, 123):06d}",
            "status_code": random.choice(status_codes),
            "scan_location": fake.city(),
            "postcode": fake.postcode(),
            "scan_timestamp": scan_time.isoformat(),
            "attempt_number": random.randint(1, 3),
            "failure_reason": None,
        }

        # Add failure reason for failed scans
        if "FAIL" in event["status_code"].upper() or "ATF" in event["status_code"]:
            event["failure_reason"] = random.choice([
                "NOT_HOME", "INCORRECT_ADDRESS", "ACCESS_DENIED",
                "REFUSED", "DAMAGED", None
            ])

        # --- Deliberate data quality issues ---

        # 4% duplicate scan_id
        if random.random() < 0.04:
            event["scan_id"] = events[-1]["scan_id"] if events else event["scan_id"]

        # 3% missing postcode
        if random.random() < 0.03:
            event["postcode"] = None

        # 3% invalid timestamp
        if random.random() < 0.03:
            event["scan_timestamp"] = "N/A"

        # 2% missing order_id
        if random.random() < 0.02:
            event["order_id"] = None

        events.append(event)

    return events


def save_as_csv(events: list, carrier_name: str):
    """Save events as CSV file."""
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{OUTPUT_DIR}/{carrier_name}_{date_str}.csv"
    df = pd.DataFrame(events)
    df.to_csv(filename, index=False)
    print(f"  CSV saved: {filename} ({len(events)} rows)")


def save_as_json(events: list, carrier_name: str):
    """Save events as JSON file."""
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{OUTPUT_DIR}/{carrier_name}_{date_str}.json"
    with open(filename, "w") as f:
        json.dump(events, f, indent=2, default=str)
    print(f"  JSON saved: {filename} ({len(events)} records)")


def generate_all_carriers():
    """Generate scan files for all carriers."""
    print("Generating carrier scan files...\n")

    for carrier_id, carrier_name in CARRIERS.items():
        print(f"Carrier: {carrier_name} ({carrier_id})")
        events = generate_scan_events(carrier_id, carrier_name, num_events=50)

        # Auspost and StarTrack send CSV, others send JSON
        if carrier_id in ["CAR001", "CAR002"]:
            save_as_csv(events, carrier_name)
        else:
            save_as_json(events, carrier_name)

    print(f"\nAll carrier scan files generated in {OUTPUT_DIR}/")


if __name__ == "__main__":
    generate_all_carriers()