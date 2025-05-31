import runpod
from supabase import Client, create_client
from dotenv import load_dotenv
import os
from dia.model import Dia
import logging


logger = logging.getLogger()
logger.info("Initializing environment variables and services")
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

logger.info("Loading Dia TTS model with float16 precision")
model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")


def upload_podcast_to_storage(podcast_file_name: str) -> None:
    """
    Uploads a podcast audio file to Supabase storage.

    Args:
        podcast_file_name (str): The name of the podcast file to upload

    Raises:
        Exception: If the upload fails
    """
    logger.info(f"Uploading podcast audio to Supabase storage: {podcast_file_name}")
    try:
        with open(podcast_file_name, "rb") as f:
            supabase.storage.from_("podcasts").upload(
                path=podcast_file_name,
                file=f,
                file_options={
                    "cache-control": "3600",
                    "upsert": "false",
                    "content-type": "audio/mpeg",
                },
            )
        logger.info(
            f"Successfully uploaded podcast audio to storage: {podcast_file_name}"
        )
    except Exception as e:
        logger.error(f"Failed to upload podcast audio: {str(e)}")
        raise


def update_podcast_status(podcast_id: str) -> None:
    """
    Updates the podcast status to READY in the database.

    Args:
        podcast_id (str): The ID of the podcast to update

    Raises:
        Exception: If the database update fails
    """
    logger.info(
        f"Updating podcast status to READY in database for podcast_id: {podcast_id}"
    )
    try:
        response = (
            supabase.table("podcasts")
            .update({"status": "READY"})
            .eq("id", podcast_id)
            .execute()
        )
        logger.info(
            f"Successfully updated podcast status in database for podcast_id: {podcast_id}"
        )
    except Exception as e:
        logger.error(f"Failed to update podcast status in database: {str(e)}")
        raise


def validate_input(input_data: dict) -> tuple[str, str]:
    """
    Validates the input data and extracts podcast_id and podcast_script.

    Args:
        input_data (dict): The input data containing podcast_id and podcast_script

    Returns:
        tuple[str, str]: A tuple containing the validated podcast_id and podcast_script

    Raises:
        ValueError: If required input parameters are missing
    """
    podcast_id = input_data.get("podcast_id")
    podcast_script = input_data.get("podcast_script")

    if not podcast_id or not podcast_script:
        logger.error(
            f"Missing required input parameters. podcast_id: {podcast_id}, script_length: {len(podcast_script) if podcast_script else 0}"
        )
        raise ValueError("Missing required input parameters")

    logger.info(
        f"Processing podcast_id: {podcast_id} with script length: {len(podcast_script)} characters"
    )

    return podcast_id, podcast_script


def handler(event):
    #   This function processes incoming requests to your Serverless endpoint.
    #
    #    Args:
    #        event (dict): Contains the input data and request metadata
    #
    #    Returns:
    #       Any: The result to be returned to the client

    logger.info("Starting new podcast generation request")
    podcast_id, podcast_script = validate_input(event["input"])
    podcast_file_name = f"{podcast_id}.mp3"

    logger.info(f"Starting TTS generation for podcast: {podcast_id}")
    output = model.generate(podcast_script, use_torch_compile=True, verbose=True)
    logger.info(f"TTS generation completed for podcast: {podcast_id}")

    logger.info(f"Saving audio file: {podcast_file_name}")
    model.save_audio(podcast_file_name, output)

    upload_podcast_to_storage(podcast_file_name)
    update_podcast_status(podcast_id)

    logger.info(
        f"Successfully completed podcast generation process for podcast_id: {podcast_id}"
    )
    return podcast_id


# Start the Serverless function when the script is run
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
