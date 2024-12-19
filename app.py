from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from middleware import RateLimitMiddleware
from tasks import fetch_parcelle_data
from io import BytesIO

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    """
    Extract the JWT token from the Authorization header.
    """
    return credentials.credentials


@app.get("/parcelle_rapport")
async def parcelle_rapport(
    parcelle: str = Query(..., title="Parcelles", description="Numéro parcellaire"),
    token: str = Depends(get_token),
):
    """
    Retourne un pdf comprenant tous les rapports pour une liste de parcelles
    """
    task = fetch_parcelle_data.delay(parcelle, token)
    result = task.get(timeout=35)
    if result == 401:
        raise HTTPException(
            status_code=401, detail="Accès non autorisé - jeton invalide"
        )
    if result == 403:
        raise HTTPException(
            status_code=403,
            detail="Accès non autorisé - Le jeton ne dispose pas des autorisations nécessaires",
        )
    if result == 404:
        raise HTTPException(
            status_code=404, detail="Pas de données pour cette parcelle"
        )
    return StreamingResponse(
        BytesIO(result),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={parcelle}.pdf"},
    )
