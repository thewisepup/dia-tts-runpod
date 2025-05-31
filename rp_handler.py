import runpod
import time
from supabase import Client, create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


def handler(event):
    #   This function processes incoming requests to your Serverless endpoint.
    #
    #    Args:
    #        event (dict): Contains the input data and request metadata
    #
    #    Returns:
    #       Any: The result to be returned to the client

    print(f"Worker Start")
    input = event["input"]
    podcast_id = input.get("podcast_id")
    print(f"Received podcast_id: {podcast_id}")
    # generate or grab podcast script
    # TTS on podcast script
    # upload podcast audio to supabase
    response = (
        supabase.table("podcasts")
        .update({"status": "READY"})
        .eq("id", podcast_id)
        .execute()
    )
    return podcast_id


# Start the Serverless function when the script is run
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
