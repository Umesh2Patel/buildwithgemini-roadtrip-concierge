# 🚗 Roadie - EV Road Trip Concierge & Personalized Companion

> **Roadie** is an AI-powered personalized EV road trip concierge built with Google's Agent Development Kit (ADK). Roadie dynamically plans long-distance Tesla itineraries by combining EV route metrics, Tesla Supercharger stops, and proactive social drop-ins (visiting friends saved in memory) and specialty food/grocery stops.

![Roadie Concierge Demo](./demo.gif)

---

## 🌟 Key Features

- **🚗 EV Route Optimization:** Calculates driving distance, duration, and battery consumption (e.g. Tesla Model Y) with recommended Supercharger charging stops.
- **🤝 Proactive Friend Drop-Ins:** Cross-references long-term memory to detect friends living along your route (e.g., Sam in San Ramon, Joe in Tracy, Jack in Davis) and proactively suggests social visits.
- **🛒 Favorite Grocery & Snack Stops:** Automatically identifies vegetarian, Indian, or favorite specialty food markets along the route (e.g., New India Bazar, Taj Supermarket, Berkeley Bowl) for road trip refueling.
- **🎨 Interactive A2UI Cards:** Emits structured Agent-to-User Interface (A2UI) cards for sleek, responsive route displays in both the web frontend and ADK dev tools.
- **🎥 Scenic Video Generation:** Generates short video clips of scenic stops using Google's Omni model (`gemini-omni-flash-preview` / `veo-3.1-generate-001`), saving them to ADK Playground Artifacts and streaming directly to a public Cloud Storage bucket.

---

## ☁️ Google Cloud & Vertex AI Architecture

| Google Cloud Tool | Usage in Project |
| :--- | :--- |
| **Vertex AI Memory Bank** | Persists long-term facts, friend locations, and snack preferences across sessions. |
| **Google Cloud Firestore** | Stores and queries road trip stops, locations, and favorite stores. |
| **Google Cloud Storage (GCS)** | Public bucket (`roadtrip-concierge-assets-50be`) for hosting generated video assets and media. |
| **Vertex AI RAG Engine** | Grounding and document retrieval for personalized travel guides and local knowledge. |
| **Google Omni & Veo (`gemini-omni-flash-preview`)** | Generates short scenic videos for road trip highlights. |
| **A2UI (Agent-to-User Interface)** | Formats responses into structured cards rendered natively by the web UI. |
| **Google Cloud Run** | Serverless hosting for the web chat frontend and FastAPI agent proxy. |

---

## 🚀 Quick Start & Local Development

### 1. Prerequisites
- **uv**: Fast Python package installer (`uv pip install -r requirements.txt`)
- **agents-cli**: Google Agents CLI (`uv tool install google-agents-cli`)
- **Google Cloud SDK**: Logged in with Application Default Credentials (`gcloud auth application-default login`)

### 2. Local Setup
```bash
# Clone the repository
git clone https://github.com/Umesh2Patel/buildwithgemini-roadtrip-concierge.git
cd buildwithgemini-roadtrip-concierge

# Install dependencies
agents-cli install
```

### 3. Launch Agent Playground
```bash
agents-cli playground
```

### 4. Run Frontend Locally
```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="projects/637055637838/locations/us-east1/reasoningEngines/8644325233202823168"
export AGENT_DIRECTORY="app"
python3 main.py
```
Visit `http://localhost:8080` in your browser.

---

## 🌍 Cloud Run Deployment

Deploy the frontend proxy to Cloud Run:
```bash
gcloud run deploy roadtrip-concierge-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/637055637838/locations/us-east1/reasoningEngines/8644325233202823168",AGENT_DIRECTORY="app"
```

Live Cloud Run Web App: [Roadie Frontend](https://roadtrip-concierge-frontend-637055637838.us-east1.run.app)
