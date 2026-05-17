import os
import tarfile
import threading
from pathlib import Path

from django.conf import settings


REQUIRED_RECIPE_FILES = [
    "uniqueIngredients.txt",
    "mostRecentNERLimitRows1.txt",
    "mostRecentNERLimitRows2.txt",
    "dishNames.txt",
    "links.txt",
    "amountsAndIngredients1.txt",
    "amountsAndIngredients2.txt",
    "amountsAndIngredients3.txt",
]

_download_lock = threading.Lock()
_download_now_lock = threading.Lock()
_download_thread = None


def recipe_data_ready():
    data_dir = Path(settings.RECIPE_DATA_DIR)
    return all((data_dir / file_name).exists() for file_name in REQUIRED_RECIPE_FILES)


def download_recipe_data():
    with _download_now_lock:
        if recipe_data_ready():
            print("Recipe data already exists.")
            return True

        bucket_name = os.environ.get("RECIPE_DATA_BUCKET")
        object_name = os.environ.get("RECIPE_DATA_OBJECT", "recipe-data.tar.gz")
        data_dir = Path(settings.RECIPE_DATA_DIR)

        if not bucket_name:
            print("RECIPE_DATA_BUCKET was not set.")
            return False

        try:
            from google.cloud import storage

            print("Downloading recipe data...")
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(object_name)

            data_dir.parent.mkdir(parents=True, exist_ok=True)
            with blob.open("rb") as recipe_file:
                with tarfile.open(fileobj=recipe_file, mode="r|gz") as recipe_data:
                    recipe_data.extractall(data_dir.parent)

            if not recipe_data_ready():
                print("Recipe data download finished, but expected files were not found.")
                return False

            print("Recipe data is ready.")
            return True
        except Exception as exc:
            print(f"Recipe data download failed: {exc}")
            return False


def wait_for_recipe_data():
    if recipe_data_ready():
        return True

    thread = _download_thread
    if thread and thread.is_alive():
        thread.join()

    if recipe_data_ready():
        return True
    return download_recipe_data()


def start_recipe_data_download():
    global _download_thread

    if recipe_data_ready():
        return
    if not os.environ.get("RECIPE_DATA_BUCKET"):
        return

    with _download_lock:
        if _download_thread and _download_thread.is_alive():
            return

        _download_thread = threading.Thread(
            target=download_recipe_data,
            name="recipe-data-download",
            daemon=True,
        )
        _download_thread.start()
