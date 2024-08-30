from fastapi import FastAPI, Query, HTTPException
from tasks import fetch_parcelle_data, celery_app
from fastapi.responses import StreamingResponse
from middleware import RateLimitMiddleware
from celery.result import AsyncResult
from rapport import create_pdf
from celery import Celery
from io import BytesIO

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get("/parcelle_rapport")
async def parcelle_rapport(
    parcelle: str = Query(..., title="Parcelles", description="Numéro parcellaire"),
    token: str = Query(..., title="Token", description="Token ConsultDF"),
):
    """
    Retourne un pdf comprenant tous les rapports pour une liste de parcelles
    """
    task = fetch_parcelle_data.delay(parcelle, token)
    result = task.get(timeout=35)
    if result == 401:
        raise HTTPException(status_code=401, detail="Accès non autorisé - jeton invalide")
    if result == 403:
        raise HTTPException(status_code=403, detail="Accès non autorisé - Le jeton ne dispose pas des autorisations nécessaires")
    if result == 404:
        raise HTTPException(status_code=404, detail="Pas de données pour cette parcelle")
    return StreamingResponse(BytesIO(result), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={parcelle}.pdf"})
