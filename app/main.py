from fastapi import FastAPI
from app.routes import sheet_routes, cell_routes

app = FastAPI()

app.include_router(sheet_routes.sheet_router, prefix="/sheets", tags=["sheets"])
app.include_router(cell_routes.cell_router, prefix="/cells", tags=["cells"])

