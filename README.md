# RecipeMaster

RecipeMaster is a full-stack web application that uses a database of 2.2 million recipes to offer three recipe search modes. It includes a pantry system, saved recipes, and text autocompletion for ingredient entry. This was a 3-month group project built 1 year into my coding journey, and I am including it to highlight my ability to ramp up quickly.

## Features

- User signup, login, and logout
- Last-minute recipe search from ingredients on hand
- Creative recipe search for ingredients to buy later
- Pantry and grocery list helpers
- Saved recipes stored in the user session

## Tech Stack

- Python
- Django
- HTML, CSS, and JavaScript
- Google Cloud Platform
- RecipeNLG dataset for recipe source data

## Local Setup

The app can be run locally without the private recipe dataset. Login, navigation, pantry, grocery list entry, and page styling can still be inspected locally, but recipe search results require the deployed private data.

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run migrations:

```bash
python3 manage.py migrate
```

Start the development server:

```bash
python3 manage.py runserver
```

Use the hosted site to try the full recipe search workflow with data:

```text
https://recipemaster.zacharymcgill.site
```

## Recipe Data

The full generated recipe text files are intentionally kept out of Git because they are large and come from the non-commercial RecipeNLG dataset.

The deployed app keeps its generated recipe archive in a private Google Cloud Storage bucket. This avoids committing large derived dataset files to Git and avoids publicly redistributing data from the source dataset. I selected Google Cloud Storage to keep the project free to host for the foreseeable future, assuming low traffic and year-round uptime needs.

Persistent production account data is kept in the project's private Firestore database. Local development uses the default SQLite database unless `USE_FIRESTORE_AUTH=True` is set. This allows the app to run locally for account creation, sign-in, navigation, pantry, grocery list, and saved recipe flows. The deployed site is required for the full recipe search workflow.

## Team

This was a group project from the beginning of our coding journeys. The project is being restored from an older hosted version and cleaned up for portfolio use. The original version was hosted on PythonAnywhere, but the account was deleted unexpectedly. We kept backups, but they were incomplete, so I restored the site as closely as possible while significantly improving the hosting infrastructure so it can remain deployed at no cost.

- Contributor: Zachary McGill
- Contributor: Brandon Coldren
- Contributor: Chez'lene Cornwall

## Postmortem

As the primary implementation contributor, I kept the original visual direction of the project but rebuilt the CSS during the portfolio cleanup. The original project was a valuable early lesson in balancing frontend polish, backend functionality, and team coordination while everyone was still learning. During the restoration, I focused on preserving the spirit of the original app while improving responsiveness, hosting, and maintainability with the skills I have built since then.
