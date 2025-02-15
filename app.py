from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datasets import Dataset, DatasetDict
from huggingface_hub import login, HfApi
from typing import List
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify specific origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Get Hugging Face token from environment variable
TOKEN = os.getenv("token")  # Make sure to set HF_TOKEN environment variable

# Ensure the token is available
if not TOKEN:
    raise ValueError("HF_TOKEN environment variable is missing.")

# Authentication for Hugging Face
login(token=TOKEN)

# Define the data folder and recipe model
DATASET_PATH = "/app/data"

if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)

class Recipe(BaseModel):
    ingredients: List[str]
    instructions: str

# Function to load the existing dataset or create a new one
def load_or_create_dataset():
    dataset_files = [f for f in os.listdir(DATASET_PATH) if f.endswith(".json")]
    all_recipes = []

    for file_name in dataset_files:
        file_path = os.path.join(DATASET_PATH, file_name)
        with open(file_path, "r") as f:
            recipe_data = json.load(f)
            all_recipes.append(recipe_data)

    return Dataset.from_dict({"data": all_recipes}) if all_recipes else None

@app.put("/add/recipe")
async def add_recipe(filename: str, recipe: Recipe):
    # Define the file path based on the filename query parameter
    file_path = os.path.join(DATASET_PATH, f"{filename}.json")

    # Check if the file already exists
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists")

    # Prepare the data to be written in JSON format
    recipe_data = recipe.dict()  # Convert Recipe model to dictionary

    # Write the data to the new file as JSON
    try:
        with open(file_path, "w") as f:
            json.dump(recipe_data, f, indent=4)

        # Load the updated dataset
        dataset = load_or_create_dataset()

        # If dataset does not exist, initialize a new one
        if not dataset:
            dataset = Dataset.from_dict({"data": [recipe_data]})

        # Push the updated dataset to the Hugging Face Hub
        dataset.push_to_hub("sharktide/recipes")

        return {"message": f"Recipe '{filename}' added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")
