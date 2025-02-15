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

# @app.put("/add/recipe")
# async def add_recipe(filename: str, recipe: Recipe):
#     # Define the file path based on the filename query parameter
#     file_path = os.path.join(DATASET_PATH, f"{filename}.json")

#     # Check if the file already exists
#     if os.path.exists(file_path):
#         raise HTTPException(status_code=400, detail="File already exists")

#     # Prepare the data to be written in JSON format
#     recipe_data = recipe.dict()  # Convert Recipe model to dictionary

#     # Write the data to the new file
#     try:
#         with open(file_path, "w") as f:
#             json.dump(recipe_data, f, indent=4)
        
#         dataset = Dataset.from_json(file_path)  # Load the new file
#         dataset.push_to_hub("sharktide/recipes")  # Push the dataset to the Hugging Face Hub
        
#         return {"message": f"Recipe '{filename}' added successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

@app.put("/add/beta")
def save_json(filename: str, recipe: Recipe) -> None:
    # Save the data to the JSON file
    with JSON_DATASET_PATH.open("a") as f:
        # Writing the recipe details (name, ingredients, instructions) to the JSON file
        json.dump({
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions
        }, f)
        f.write("\n")

        
    
    # Commit and push the changes to the dataset