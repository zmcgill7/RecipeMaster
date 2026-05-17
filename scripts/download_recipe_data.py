import os
import tarfile
from pathlib import Path

from google.cloud import storage


bucket_name = os.environ.get("RECIPE_DATA_BUCKET")
object_name = os.environ.get("RECIPE_DATA_OBJECT", "recipe-data.tar.gz")
data_dir = Path(os.environ.get("RECIPE_DATA_DIR", "local_data"))

if data_dir.exists():
    print("Recipe data already exists.")
    raise SystemExit

if not bucket_name:
    print("RECIPE_DATA_BUCKET was not set.")
    raise SystemExit(1)

print("Downloading recipe data...")
client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob(object_name)

print("Extracting recipe data...")
with blob.open("rb") as recipe_file:
    recipe_data = tarfile.open(fileobj=recipe_file, mode="r|gz")
    recipe_data.extractall(data_dir.parent)
    recipe_data.close()

print("Recipe data is ready.")
