import time
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

BUCKET_NAME = "roadtrip-concierge-assets-50be"
PROJECT_ID = "qwiklabs-gcp-03-50be59d01b05"


def generate_scenic_roadtrip_video(prompt: str, tool_context: ToolContext) -> str:
    """Generates a short video for an item in the roadtrip concierge domain using Google Video AI models.

    Args:
        prompt: Detailed description of the video to generate (e.g., 'A 5-second video of a Tesla Model Y driving along coastal Highway 1 at sunset').
        tool_context: ADK tool context for saving artifacts.

    Returns:
        The public HTTPS URL of the generated video stored in Cloud Storage.
    """
    video_bytes = None
    filename = f"scenic_roadtrip_{uuid.uuid4().hex[:8]}.mp4"

    # 1. Primary Attempt: Google's Omni model (gemini-omni-flash-preview) in global region
    try:
        client_omni = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        operation = client_omni.models.generate_videos(
            model="gemini-omni-flash-preview",
            source=types.GenerateVideosSource(prompt=prompt),
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                duration_seconds=5,
            ),
        )
        while not operation.done:
            time.sleep(5)
            operation = client_omni.operations.get(operation)
        if operation.response and getattr(operation.response, "generated_videos", None):
            video_bytes = operation.response.generated_videos[0].video.video_bytes
    except Exception as e:
        print(f"Omni model (gemini-omni-flash-preview) global attempt note: {e}")

    # 2. Fallback Attempt: Veo video generation model (veo-3.1-generate-001) in us-central1
    if not video_bytes:
        try:
            client_veo = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
            operation = client_veo.models.generate_videos(
                model="veo-3.1-generate-001",
                source=types.GenerateVideosSource(prompt=prompt),
                config=types.GenerateVideosConfig(
                    aspect_ratio="16:9",
                    duration_seconds=5,
                ),
            )
            while not operation.done:
                time.sleep(5)
                operation = client_veo.operations.get(operation)
            if operation.response and getattr(operation.response, "generated_videos", None):
                video_bytes = operation.response.generated_videos[0].video.video_bytes
        except Exception as fallback_err:
            return f"Video generation error: {fallback_err}"

    if not video_bytes:
        return "Failed to generate video bytes from model response."

    # (1) Save artifact with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload the same video bytes directly to the public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Successfully generated scenic video! Public URL: {public_url}"
