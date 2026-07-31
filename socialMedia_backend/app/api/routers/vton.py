from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
import os

router = APIRouter()

class VtonRequest(BaseModel):
    garment_url: str
    model_image_b64: str

class VtonResponse(BaseModel):
    image_url: Optional[str] = None
    status: str
    message: Optional[str] = None

FASHN_API_KEY = os.getenv("FASHN_API_KEY")
FASHN_API_URL = "https://api.fashn.ai/v1/run"
FASHN_STATUS_URL = "https://api.fashn.ai/v1/status"

@router.post("/tryon", response_model=VtonResponse)
async def vton_tryon(req: VtonRequest):
    """
    Experimental Fashn.ai VTON Endpoint.
    """
    if not FASHN_API_KEY:
        # Mock mode if no API key
        await asyncio.sleep(2)
        # We simulate the tryon by returning a realistic placeholder image of a model wearing clothes
        return VtonResponse(
            image_url="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80", 
            status="mocked",
            message="API Key yok. Örnek bir VTON sonucu (deneme modeli) simüle edildi."
        )
    
    # Real Fashn.ai Call
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {FASHN_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Start job
            payload = {
                "model_name": "tryon-max",
                "inputs": {
                    "product_image": req.garment_url,
                    "model_image": req.model_image_b64 # Data URI (e.g. data:image/jpeg;base64,...)
                }
            }
            
            res = await client.post(FASHN_API_URL, json=payload, headers=headers)
            
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Fashn API Error: {res.text}")
                
            job_data = res.json()
            job_id = job_data.get("id")
            if not job_id:
                raise HTTPException(status_code=500, detail="Fashn API returned no job ID")
            
            # Poll for result (max 15 attempts = 30 seconds)
            for _ in range(15):
                await asyncio.sleep(2)
                status_res = await client.get(f"{FASHN_STATUS_URL}/{job_id}", headers=headers)
                if status_res.status_code == 200:
                    status_data = status_res.json()
                    status = status_data.get("status")
                    if status == "completed":
                        # output might be a list of URLs
                        output = status_data.get("output", [])
                        if isinstance(output, list) and len(output) > 0:
                            return VtonResponse(status="completed", image_url=output[0])
                    elif status == "failed":
                        raise HTTPException(status_code=500, detail=f"Fashn VTON failed: {status_data.get('error')}")
                    # else still processing, continue loop
                    
            raise HTTPException(status_code=504, detail="Fashn VTON Timeout")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
