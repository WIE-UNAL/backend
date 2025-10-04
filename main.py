from fastapi import FastAPI, HTTPException
import httpx
from typing import Dict, Any

app = FastAPI(title="Event Title API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Event Title API - Vercel Backend"}

@app.get("/event/{event_id}")
async def get_event_title(event_id: str):
    """
    Obtiene el título de un evento específico de la API de IEEE
    """
    try:
        # URL de la API externa con el ID dinámico
        api_url = f"https://events.vtools.ieee.org/RST/events/api/public/v6/events/list?id={event_id}"
        
        # Realizar la llamada HTTP
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response.raise_for_status()  # Lanza excepción si hay error HTTP
            
        # Parsear la respuesta JSON
        data = response.json()
        
        # Verificar que existe la estructura esperada
        if not data.get("data") or len(data["data"]) == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Extraer el título del primer evento
        event_data = data["data"][0]
        title = event_data["attributes"]["title"]
        
        return {
            "event_id": event_id,
            "title": title,
            "status": "success"
        }
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from external API: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Unexpected response format: missing {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/event/{event_id}/full")
async def get_event_full_data(event_id: str):
    """
    Obtiene toda la información del evento (opcional para debugging)
    """
    try:
        api_url = f"https://events.vtools.ieee.org/RST/events/api/public/v6/events/list?id={event_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response.raise_for_status()
            
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# Para Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)