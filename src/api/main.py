"""FastAPI application for the Site Uptime Watcher API."""
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator, HttpUrl
import uvicorn

from src.endpoint_manager import EndpointManager

app = FastAPI(
    title="Site Uptime Watcher API",
    description="API for managing site uptime monitoring endpoints",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

class EndpointBase(BaseModel):
    """Base model for endpoint data with common attributes."""
    url: HttpUrl
    regex: Optional[str] = None
    interval: int

    @validator('interval')
    # pylint: disable=no-self-argument
    def validate_interval(cls, v):
        """Validate that the interval is between 5 and 300 seconds."""
        if v < 5 or v > 300:
            raise ValueError('Interval must be between 5 and 300 seconds')
        return v

class EndpointCreate(EndpointBase):
    """Model for creating a new endpoint."""

class EndpointUpdate(BaseModel):
    """Model for updating an existing endpoint."""
    url: Optional[HttpUrl] = None
    regex: Optional[str] = None
    interval: Optional[int] = None

    @validator('interval')
    # pylint: disable=no-self-argument
    def validate_interval(cls, v):
        """Validate that the interval is between 5 and 300 seconds if provided."""
        if v is not None and (v < 5 or v > 300):
            raise ValueError('Interval must be between 5 and 300 seconds')
        return v

class EndpointResponse(EndpointBase):
    """Model for endpoint response data including the endpoint ID."""
    endpoint_id: int

    # pylint: disable=too-few-public-methods
    class Config:
        """Configuration for the EndpointResponse model."""
        orm_mode = True

# Dependency to get endpoint manager
def get_endpoint_manager():
    """Create and initialize an EndpointManager instance for dependency injection."""
    manager = EndpointManager()
    manager.check_readiness()
    return manager

@app.get("/")
async def read_root():
    """Serve the main HTML page for the API."""
    return FileResponse("src/api/static/index.html")

@app.get("/endpoints", response_model=List[EndpointResponse])
async def list_endpoints(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    manager: EndpointManager = Depends(get_endpoint_manager)
):
    """List all endpoints with pagination."""
    try:
        # Fetch all endpoints without partitioning
        endpoints = manager.fetch_all_endpoints()
        return endpoints[skip:skip+limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.post("/endpoints", response_model=EndpointResponse, status_code=201)
async def create_endpoint(
    endpoint: EndpointCreate,
    manager: EndpointManager = Depends(get_endpoint_manager)
):
    """Create a new endpoint."""
    try:
        new_endpoint = manager.create_endpoint(
            url=str(endpoint.url),
            regex=endpoint.regex,
            interval=endpoint.interval
        )
        return new_endpoint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/endpoints/{endpoint_id}", response_model=EndpointResponse)
async def get_endpoint(
    endpoint_id: int,
    manager: EndpointManager = Depends(get_endpoint_manager)
):
    """Get a specific endpoint by ID."""
    try:
        endpoint = manager.get_endpoint(endpoint_id)
        if endpoint is None:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        return endpoint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.put("/endpoints/{endpoint_id}", response_model=EndpointResponse)
async def update_endpoint(
    endpoint_id: int,
    endpoint_update: EndpointUpdate,
    manager: EndpointManager = Depends(get_endpoint_manager)
):
    """Update an existing endpoint."""
    try:
        # Check if endpoint exists
        existing = manager.get_endpoint(endpoint_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        # Update only provided fields
        update_data = {}
        if endpoint_update.url is not None:
            update_data["url"] = str(endpoint_update.url)
        if endpoint_update.regex is not None:
            update_data["regex"] = endpoint_update.regex
        if endpoint_update.interval is not None:
            update_data["interval"] = endpoint_update.interval
        
        updated_endpoint = manager.update_endpoint(endpoint_id, update_data)
        return updated_endpoint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.delete("/endpoints/{endpoint_id}", status_code=204)
async def delete_endpoint(
    endpoint_id: int,
    manager: EndpointManager = Depends(get_endpoint_manager)
):
    """Delete an endpoint."""
    try:
        # Check if endpoint exists
        existing = manager.get_endpoint(endpoint_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        manager.delete_endpoint(endpoint_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8080"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
    
