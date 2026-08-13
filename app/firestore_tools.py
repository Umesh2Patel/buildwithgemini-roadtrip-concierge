"""Firestore tools for RoadTrip Concierge agent."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-50be59d01b05"
COLLECTION_NAME = "roadtrip_stops"

_db = firestore.Client(project=PROJECT_ID)


def search_roadtrip_stops(category: str = None, city: str = None) -> str:
    """Search for road trip stops saved in Firestore by category or city.

    Args:
        category: Optional category filter (e.g., 'grocery', 'food_joint', 'tesla_charging').
        city: Optional city filter (e.g., 'Sacramento', 'Pleasanton', 'Berkeley').

    Returns:
        Formatted string listing matching stops and their addresses/notes.
    """
    collection_ref = _db.collection(COLLECTION_NAME)
    query = collection_ref

    if category:
        query = query.where("category", "==", category.lower())
    if city:
        query = query.where("city", "==", city.title())

    docs = list(query.stream())
    if not docs:
        filters = []
        if category:
            filters.append(f"category='{category}'")
        if city:
            filters.append(f"city='{city}'")
        filter_str = ", ".join(filters) if filters else "no filters"
        return f"No road trip stops found in Firestore for {filter_str}."

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(
            f"• {data.get('name')} [{data.get('category', 'stop')}]\n"
            f"  Address: {data.get('address')}\n"
            f"  City: {data.get('city')}\n"
            f"  Notes: {data.get('notes', 'N/A')}\n"
            f"  Rating: {data.get('rating', 'N/A')}"
        )

    return "\n\n".join(results)


def add_roadtrip_stop(
    name: str,
    category: str,
    city: str,
    address: str,
    notes: str = "",
    rating: float = 4.5,
) -> str:
    """Add a new favorite road trip stop to the Firestore database.

    Args:
        name: Name of the stop/establishment (e.g., 'Trader Joe's').
        category: Category of stop ('grocery', 'food_joint', 'tesla_charging', 'landmark', 'friend_visit').
        city: City where the stop is located.
        address: Full street address.
        notes: Additional helpful notes about this stop.
        rating: Rating out of 5.0 (default: 4.5).

    Returns:
        Confirmation message upon adding to Firestore.
    """
    doc_id = name.lower().replace(" ", "-").replace("'", "").replace(".", "")
    doc_ref = _db.collection(COLLECTION_NAME).document(doc_id)

    stop_data = {
        "id": doc_id,
        "name": name,
        "category": category.lower(),
        "city": city.title(),
        "address": address,
        "notes": notes,
        "rating": rating,
    }

    doc_ref.set(stop_data)
    return f"Successfully added '{name}' in {city} to Firestore roadtrip_stops collection!"


def get_stop_details(stop_name: str) -> str:
    """Retrieve detailed information for a specific stop from Firestore.

    Args:
        stop_name: Name or partial name of the stop to search for.

    Returns:
        Detailed stop information string.
    """
    collection_ref = _db.collection(COLLECTION_NAME)
    docs = list(collection_ref.stream())

    matching = []
    for doc in docs:
        data = doc.to_dict()
        if stop_name.lower() in data.get("name", "").lower() or stop_name.lower() in doc.id:
            matching.append(data)

    if not matching:
        return f"No stop found matching '{stop_name}' in Firestore."

    data = matching[0]
    return (
        f"Stop Details for '{data.get('name')}':\n"
        f"• Category: {data.get('category')}\n"
        f"• Address: {data.get('address')}\n"
        f"• City: {data.get('city')}\n"
        f"• Rating: {data.get('rating')}\n"
        f"• Notes: {data.get('notes')}"
    )
