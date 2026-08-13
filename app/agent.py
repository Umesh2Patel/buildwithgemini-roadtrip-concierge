# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


MODEL = "gemini-3.6-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send the session to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

from app.a2ui_utils import a2ui_callback
from app.firestore_tools import (
    add_roadtrip_stop,
    get_stop_details,
    search_roadtrip_stops,
)
from app.route_tools import calculate_route_metrics


code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name="projects/637055637838/locations/us-east1/reasoningEngines/8644325233202823168"
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Roadie, a personalized long-distance travel and road trip concierge.\n\n"
        "PROACTIVE PERSONALIZATION & ROUTE PLANNING RULES:\n"
        "1. Whenever planning a route or itinerary between cities (e.g., SF to Lake Tahoe, Sacramento, or East Bay):\n"
        "   - MANDATORY FRIEND STOPS: Check if any friends from memory (e.g. Sam in San Ramon, Joe in Tracy, Jack in Davis) live in or near cities along the route. PROACTIVELY propose a social stop/visit with them in the itinerary!\n"
        "   - MANDATORY GROCERY & FOOD STOPS: Check favorite grocery stores from memory (e.g. New India Bazar in Pleasanton, Taj Supermarket in Sacramento, Berkeley Bowl in Berkeley) or query Firestore using `search_roadtrip_stops`. PROACTIVELY recommend stopping at these grocery/snack spots for road trip snacks matching vegetarian/Indian/Mexican preferences!\n"
        "   - EV CHARGING: Compute route metrics with `calculate_route_metrics` and align Tesla Supercharger stops near these friend or grocery stops where possible.\n"
        "2. INCLUDE ALL STOPS IN THE A2UI CARD: Ensure the generated A2UI Card/Column explicitly lists:\n"
        "   - Driving Distance & Battery Consumption\n"
        "   - Recommended Supercharger Stops\n"
        "   - Friend Drop-in Stops (e.g. 'Friend Stop: Visit Jack in Davis, CA')\n"
        "   - Favorite Grocery & Food Stops (e.g. 'Grocery Stop: Grab veggie snacks at Taj Supermarket in Sacramento')"
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    tools=[
        get_weather,
        get_current_time,
        search_roadtrip_stops,
        add_roadtrip_stop,
        get_stop_details,
        calculate_route_metrics,
        PreloadMemoryTool(),
    ],
    code_executor=code_executor,
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

