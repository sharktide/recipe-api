from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datasets import Dataset, DatasetDict, DatasetInfo
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

TOKEN = os.getenv("token")


class Recipe(BaseModel):
    ingredients: List[str]
    instructions: str

DATASET_PATH = "/mnt/data/sharktide/recipes/data"

# Ensure the 'data' folder exists
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)

# Authentication for Hugging Face
login(token=TOKEN)

@app.put("/add/recipe")
async def add_recipe(filename: str, recipe: Recipe):
    # Define the file path based on the filename query parameter
    file_path = os.path.join(DATASET_PATH, f"{filename}.json")

    # Check if the file already exists
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists")

    # Prepare the data to be written in JSON format
    recipe_data = recipe.dict()  # Convert Recipe model to dictionary

    # Write the data to the new file
    try:
        with open(file_path, "w") as f:
            json.dump(recipe_data, f, indent=4)
        
        dataset = Dataset.from_json(file_path)  # Load the new file
        dataset.push_to_hub("sharktide/recipes")  # Push the dataset to the Hugging Face Hub
        
        return {"message": f"Recipe '{filename}' added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")
