#!/usr/bin/env python3
"""
Simple FastAPI test server.
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="AI Companion Test")

@app.get("/")
async def root():
    return {"message": "AI Companion is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting AI Companion test server...")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
