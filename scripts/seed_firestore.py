#!/usr/bin/env python3
"""Seed script for RoadTrip Concierge Firestore database."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-50be59d01b05"
COLLECTION_NAME = "roadtrip_stops"

SEED_STOPS = [
    {
        "id": "new-india-bazar",
        "name": "New India Bazar",
        "category": "grocery",
        "city": "Pleasanton",
        "address": "3160 Santa Rita Rd, Pleasanton, CA 94566",
        "notes": "Favorite Indian grocery store for road trip snacks, spices, and fresh produce.",
        "rating": 4.7,
    },
    {
        "id": "taj-supermarket",
        "name": "Taj Supermarket",
        "category": "grocery",
        "city": "Sacramento",
        "address": "7933 E Stockton Blvd, Sacramento, CA 95823",
        "notes": "Spacious Indian supermarket near Hwy 99 with great vegetarian snacks and sweets.",
        "rating": 4.6,
    },
    {
        "id": "berkeley-bowl-marketplace",
        "name": "Berkeley Bowl Marketplace",
        "category": "grocery",
        "city": "Berkeley",
        "address": "2020 Oregon St, Berkeley, CA 94703",
        "notes": "Iconic Bay Area market with unbeatable produce and artisan vegan products.",
        "rating": 4.8,
    },
    {
        "id": "corti-brothers",
        "name": "Corti Brothers",
        "category": "food_joint",
        "city": "Sacramento",
        "address": "5810 Folsom Blvd, Sacramento, CA 95819",
        "notes": "Famous Italian specialty market and sandwich counter off US-50.",
        "rating": 4.9,
    },
    {
        "id": "sacramento-supercharger",
        "name": "Sacramento Tesla Supercharger",
        "category": "tesla_charging",
        "city": "Sacramento",
        "address": "1689 Arden Way, Sacramento, CA 95815",
        "notes": "250kW V3 Tesla Supercharger located near shops and restaurants.",
        "rating": 4.5,
    },
    {
        "id": "squeeze-burger",
        "name": "Squeeze Burger",
        "category": "food_joint",
        "city": "Sacramento",
        "address": "5301 Power Inn Rd, Sacramento, CA 95820",
        "notes": "Home of the famous Squeeze with Cheese skirt burger.",
        "rating": 4.6,
    },
]


def seed():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding '{COLLECTION_NAME}' collection in project '{PROJECT_ID}'...")
    for stop in SEED_STOPS:
        doc_ref = collection_ref.document(stop["id"])
        doc_ref.set(stop)
        print(f"  - Seeded stop: {stop['name']} ({stop['city']})")

    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed()
