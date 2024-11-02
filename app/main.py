from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import batch, random, categories
import logging

app = FastAPI(
    title="ASCIIme API",
    description="API for fetching anime GIFs from various sources",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(batch.router, prefix="/api", tags=["batch"])
app.include_router(random.router, prefix="/api", tags=["random"])
app.include_router(categories.router, prefix="/api", tags=["categories"])

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    