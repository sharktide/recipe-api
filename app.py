from fastapi import FastAPI
import requests
import json
import time

app = FastAPI()

import os

@app.get("/")
def home():
    return("Status": "Working")


