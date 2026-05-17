import os
import sys
from pathlib import Path

import django


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
os.environ["BACKGROUND_RECIPE_DATA_DOWNLOAD"] = "False"
django.setup()


from RecipeMaster.recipe_data import download_recipe_data


raise SystemExit(0 if download_recipe_data() else 1)
