"""
Main application entry point for AI Companion.
"""

import asyncio
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import our modules (avoiding relative imports)
import importlib.util

# Load config manager
config_spec = importlib.util.spec_from_file_location("config_manager", src_path / "config" / "config_manager.py")
config_module = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_module)

# Load logging
logging_spec = importlib.util.spec_from_file_location("logging", src_path / "core" / "logging.py")
logging_module = importlib.util.module_from_spec(logging_spec)
logging_spec.loader.exec_module(logging_module)


class CompanionApp:
    """Main AI Companion application."""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.app = None
        self.memory_manager = None
        self.behavior_tree = None
        
    async def initialize(self):
        """Initialize the application."""
        try:
            # Load configuration
            self.config = config_module.get_config()
            
            # Setup logging
            self.logger = logging_module.setup_logging(
                log_level=self.config.log_level,
                debug_mode=self.config.debug
            )
            
            self.logger.info("AI Companion starting up...")
            
            # Initialize components (placeholder for now)
            # self.memory_manager = MemoryManager(self.config.data_directory)
            # self.behavior_tree = BehaviorTreeManager(self.config.data_directory)
            
            self.logger.info("AI Companion initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize AI Companion: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the application."""
        if self.logger:
            self.logger.info("AI Companion shutting down...")


# Global app instance
companion = CompanionApp()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    await companion.initialize()
    yield
    # Shutdown
    await companion.shutdown()


# Create FastAPI app
app = FastAPI(
    title="AI Companion",
    description="Intelligent AI companion with dynamic behavior trees and adaptive memory",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Companion API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2025-07-26T08:34:12Z",  # Will be dynamic
        "version": "1.0.0"
    }


@app.get("/api/status")
async def get_status():
    """Get system status."""
    try:
        status = {
            "memory_manager": "initialized" if companion.memory_manager else "not_initialized",
            "behavior_tree": "initialized" if companion.behavior_tree else "not_initialized",
            "config_loaded": companion.config is not None
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(message: dict):
    """Chat endpoint for text interaction."""
    try:
        user_message = message.get("message", "")
        
        # Placeholder response
        response = {
            "response": f"I received your message: {user_message}",
            "timestamp": "2025-07-26T08:34:12Z",
            "type": "text"
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/stats")
async def get_memory_stats():
    """Get memory system statistics."""
    if not companion.memory_manager:
        return {"error": "Memory manager not initialized"}
    
    # Placeholder stats
    return {
        "total_memories": 0,
        "working_memory": 0,
        "episodic_memories": 0,
        "semantic_memories": 0,
        "procedural_memories": 0
    }


@app.get("/api/behavior-tree/states")
async def get_behavior_states():
    """Get behavior tree states."""
    if not companion.behavior_tree:
        return {"error": "Behavior tree not initialized"}
    
    # Placeholder response
    return {
        "states": [
            {
                "id": "root",
                "name": "Root State",
                "type": "root",
                "children": []
            }
        ]
    }


def main():
    """Main entry point."""
    print("Starting AI Companion...")
    
    # Load config to get host and port
    try:
        config = config_module.get_config()
        host = config.host
        port = config.port
    except Exception:
        host = "localhost"
        port = 8000
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
