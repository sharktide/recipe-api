import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from huggingface_hub import login, HfApi
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify specific origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Token for Hugging Face (using the token environment variable as 'token')
TOKEN = os.getenv("token")
if not TOKEN:
    raise ValueError("The 'token' environment variable is missing.")

# Authenticate with Hugging Face Hub
login(token=TOKEN)

# Hugging Face API for dataset handling
hf_api = HfApi()

# Define the folder for storing the dataset locally
JSON_DATASET_DIR = "json_dataset"
os.makedirs(JSON_DATASET_DIR, exist_ok=True)

# Dataset info (to be used when pushing to Hugging Face Hub)
dataset_repo = "sharktide/recipes"  # Change to your repo name on Hugging Face Hub
DATASET_PATH = os.path.join(JSON_DATASET_DIR, "data")

# Define the Recipe model
class Recipe(BaseModel):
    ingredients: List[str]
    instructions: str

@app.put("/add/recipe")
async def add_recipe(filename: str, recipe: Recipe):
    # Define the file path for saving the recipe in JSON format
    file_path = os.path.join(JSON_DATASET_DIR, f"{filename}.json")
    
    # Prepare the data to be saved
    recipe_data = recipe.dict()
    recipe_data["datetime"] = datetime.now().isoformat()  # Add timestamp to the entry
    
    # Save the recipe to the JSON file
    try:
        with open(file_path, "a") as f:
            json.dump(recipe_data, f)
            f.write("\n")  # Add a newline after each entry
        
        # Push the updated data directly to the Hugging Face dataset repo
        hf_api.dataset_push_to_hub(
            repo_id=dataset_repo, 
            path_in_repo="data", 
            folder_path=JSON_DATASET_DIR
        )

        return {"message": f"Recipe '{filename}' added and pushed to Hugging Face dataset."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

