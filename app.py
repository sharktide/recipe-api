from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datasets import Dataset, DatasetDict, DatasetInfo
from huggingface_hub import login, HfApi, CommitScheduler, logging
from typing import List
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import requests
import warnings

logging.set_verbosity_debug()


# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (temp)
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

TOKEN = os.getenv("token")


class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    instructions: str

DATASET_PATH = "/app/data"

if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)

login(token=TOKEN)

JSON_DATASET_DIR = Path("json_dataset")
JSON_DATASET_DIR.mkdir(parents=True, exist_ok=True)


JSON_DATASET_PATH = JSON_DATASET_DIR / f"train-{uuid4()}.json"

scheduler = CommitScheduler(
    repo_id="sharktide/recipes",
    repo_type="dataset",
    folder_path=JSON_DATASET_DIR,
    path_in_repo="data",
)

def check_huggingface_recipe_name(name: str) -> bool:
    url = "https://datasets-server.huggingface.co/rows?dataset=sharktide%2Frecipes&config=default&split=train"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        existing_names = [row['row']['name'] for row in data['rows']]
        return name in existing_names
    if response.status_code == 404:
        warnings.Warn("Dataset is empty, or unreachable")
        return False
    else:
        raise HTTPException(status_code=500, detail="Error accessing store")


def check_local_cache_recipe_name(name: str) -> bool:
    for file in os.listdir(JSON_DATASET_DIR):
        file_path = JSON_DATASET_DIR / file
        if file_path.suffix == ".json":
            with open(file_path, "r") as f:
                for line in f:
                    try:
                        recipe_data = json.loads(line)
                        if recipe_data['name'] == name:
                            return True
                    except json.JSONDecodeError:
                        continue
    return False


@app.get("/status")
def status():
    return {"status": "200"}


@app.put("/add/recipe")
def add_recipe(recipe: Recipe):
    
    if check_huggingface_recipe_name(recipe.name):
        raise HTTPException(status_code=400, detail="Recipe name already exists in the store.")
    
    if check_local_cache_recipe_name(recipe.name):
        raise HTTPException(status_code=400, detail="Recipe name already exists in the local cache.")
    
    try:
        with JSON_DATASET_PATH.open("a") as f:
            json.dump({
                "name": recipe.name,
                "time": recipe.time,
                "creator": recipe.creator
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions
            }, f)
            f.write("\n")
        return {"Status": "Recipe added successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving recipe: {str(e)}")

        
    
