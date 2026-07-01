import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import ( auth, users, cars, bookings, rentals, price, damage, recommendation, analytics )
from app.routers import damage

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(name)s: %(message)s', )

logger = logging.getLogger(__name__)

# Create all DB tables on startup (idempotent — safe to run repeatedly)
Base.metadata.create_all(bind=engine)
logger.info('Database tables verified.')

app = FastAPI(
    title='AutoVerse API',
    description='AI-Powered Car Marketplace',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
)

# CORS — allow Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware, 
    allow_origins=['*'], # tighten in production to your Render frontend URL
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Register all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(cars.router)
app.include_router(bookings.router)
app.include_router(rentals.router)
app.include_router(price.router)
app.include_router(damage.router)
app.include_router(recommendation.router)
app.include_router(analytics.router)
app.include_router(damage.router)

@app.get('/', tags=['Health'])
def health_check():
    return {'status': 'ok', 'service': 'AutoVerse API v1.0'}