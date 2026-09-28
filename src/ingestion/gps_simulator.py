"""
gps_simulator.py
Simulates GPS telemetry events from delivery drivers for Meridian Freight Group.
Sends events to Azure Event Hubs with deliberate fault injection.
"""

import os
import json
import time
import random
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
CONNECTION_STRING = os.getenv("EVENT_HUB_CONNECTION_STRING")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")

# Simulated Australian delivery zones
DELIVERY_ZONES = [
    {"city": "Adelaide",   "lat": -34.9285, "lng": 138.6007},
    {"city": "Melbourne",  "lat": -37.8136, "lng": 144.9631},
    {"city": "Sydney",     "lat": -33.8688, "lng": 151.2093},
    {"city": "Brisbane",   "lat": -27.4698, "lng": 153.0251},
    {"city": "Perth",      "lat": -31.9505, "lng": 115.8605},
]

CARRIERS = ["CAR001", "CAR002", "CAR003", "CAR004", "CAR005"]
EVENT_TYPES = ["POSITION", "STOP", "DELIVERY_ATTEMPT", "DELIVERY_SUCCESS", "DELIVERY_FAILED"]


def generate_event(driver_id: str, zone: dict) -> dict:
    """Generate a single GPS telemetry event with optional faults."""

    # Small random movement around the zone centre
    lat = zone["lat"] + random.uniform(-0.05, 0.05)
    lng = zone["lng"] + random.uniform(-0.05, 0.05)

    event = {
        "driver_id": driver_id,
        "carrier_id": random.choice(CARRIERS),
        "order_id": f"ORD{random.randint(1, 123):06d}",
        "event_type": random.choice(EVENT_TYPES),
        "latitude": round(lat, 6),
        "longitude": round(lng, 6),
        "speed_kmh": round(random.uniform(0, 80), 1),
        "city": zone["city"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": f"DEV{driver_id[-3:]}",
    }

    # --- Deliberate fault injection ---

    # 3% chance of duplicate event
    if random.random() < 0.03:
        event["_is_duplicate"] = True

    # 4% chance of null coordinates
    if random.random() < 0.04:
        event["latitude"] = None
        event["longitude"] = None

    # 2% chance of wrong timestamp format
    if random.random() < 0.02:
        event["timestamp"] = "INVALID_TIMESTAMP"

    # 5% chance of missing order_id
    if random.random() < 0.05:
        event["order_id"] = None

    return event


def send_events(batch_size: int = 5, rounds: int = 3):
    """Send batches of GPS events to Event Hubs."""

    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        eventhub_name=EVENT_HUB_NAME
    )

    drivers = [f"DRV{i:04d}" for i in range(1, 21)]  # 20 simulated drivers

    with producer:
        for round_num in range(1, rounds + 1):
            print(f"\nRound {round_num}/{rounds} — sending {batch_size} events...")

            event_data_batch = producer.create_batch()

            for _ in range(batch_size):
                driver = random.choice(drivers)
                zone = random.choice(DELIVERY_ZONES)
                event = generate_event(driver, zone)

                event_data_batch.add(EventData(json.dumps(event)))
                print(f"  → {event['driver_id']} | {event['event_type']} | {event['city']} | {event['timestamp']}")

            producer.send_batch(event_data_batch)
            print(f"Batch sent successfully.")

            if round_num < rounds:
                time.sleep(2)

    print("\nSimulator complete.")


if __name__ == "__main__":
    print("Starting GPS telemetry simulator...")
    print(f"Target: {EVENT_HUB_NAME}")
    send_events(batch_size=5, rounds=3)