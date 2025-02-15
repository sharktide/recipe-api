from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datasets import Dataset, DatasetDict, DatasetInfo
from huggingface_hub import login, HfApi
from typing import List
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from huggingface_hub import CommitScheduler
from huggingface_hub import logging

logging.set_verbosity_debug()


# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify specific origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

TOKEN = os.getenv("token")


class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    instructions: str

DATASET_PATH = "/app/data"

# Ensure the 'data' folder exists
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)

# Authentication for Hugging Face
login(token=TOKEN)

JSON_DATASET_DIR = Path("json_dataset")
JSON_DATASET_DIR.mkdir(parents=True, exist_ok=True)

# Define path for the JSON file to save data
JSON_DATASET_PATH = JSON_DATASET_DIR / f"train-{uuid4()}.json"

scheduler = CommitScheduler(
    repo_id="sharktide/recipes",
    repo_type="dataset",
    folder_path=JSON_DATASET_DIR,
    path_in_repo="data",
)

@app.get("/status")
def status():
    return {"status": "200"}


@app.put("/add/recipe")
def save_json(filename: str, recipe: Recipe):
    with JSON_DATASET_PATH.open("a") as f:
        json.dump({
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions
        }, f)
        f.write("\n")
    return {"Status": "Added to cache"}

        
    
