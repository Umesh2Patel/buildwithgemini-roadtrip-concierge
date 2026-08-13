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


from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from app.firestore_tools import (
    add_roadtrip_stop,
    get_stop_details,
    search_roadtrip_stops,
)
from app.route_tools import calculate_route_metrics


code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name="projects/637055637838/locations/us-east1/reasoningEngines/8644325233202823168"
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are Roadie, a personalized long-distance travel and road trip concierge.\n\n"
        "COMPREHENSIVE MEMORY & PERSONALIZATION INSTRUCTIONS:\n"
        "- Remember and track ALL user preferences shared across conversations, including but not limited to:\n"
        "  1. Meal & Dietary Preferences: Vegetarian/vegan/gluten-free, favorite cuisines (e.g. Indian, Mexican), favorite food joints, and preferred grocery store chains.\n"
        "  2. Social & Friend Contacts: Friends' names, cities/locations, and visit preferences.\n"
        "  3. Vehicle & Charging Preferences: Tesla/EV vehicle model, charging stop preferences, battery range, and preferred charging networks.\n"
        "  4. Travel & Driving Preferences: Driving pace, maximum continuous driving hours, preferred scenic routes, favorite landmarks, and hotel/lodging preferences.\n"
        "- Preloaded memories automatically inject past facts at the beginning of each conversation turn. Actively reference and apply all relevant stored preferences whenever answering queries, planning itineraries, or suggesting stops.\n"
        "- Whenever the user shares any new preference or fact, explicitly acknowledge and confirm it so it gets processed by Memory Bank for long-term cross-session persistence.\n"
        "- Use your Firestore tools (`search_roadtrip_stops`, `add_roadtrip_stop`, `get_stop_details`) to look up and store saved favorite stops along driving routes.\n"
        "- Use `calculate_route_metrics` to compute accurate driving distances, drive times, EV battery consumption, and required Tesla charging stops whenever origin and destination are discussed.\n"
        "- You have a secure Python sandbox code executor to execute custom Python code for complex mathematical calculations, data formatting, or custom algorithms."
    ),
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
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

