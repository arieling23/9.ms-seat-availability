from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry
import asyncio

from app.resolvers.seat_resolver import Query, Mutation
from app.utils.logger import logger
from app.db import engine, Base
from app.consumers.flight_consumer import consume_flight_created  


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)


app = FastAPI()
logger.info("📦 Instancia FastAPI creada.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("🌐 Middleware CORS configurado.")


@app.on_event("startup")
async def startup():
    logger.info("🚀 Iniciando microservicio ms-seat-availability...")


    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Base de datos inicializada correctamente.")
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {str(e)}")

   
    try:
        asyncio.create_task(consume_flight_created())
        logger.info("📡 Consumidor flight.created iniciado en segundo plano.")
    except Exception as e:
        logger.error(f"❌ Error al iniciar consumidor: {str(e)}")


app.include_router(graphql_app, prefix="/seat")
logger.info("🔌 Ruta /seat registrada para consultas GraphQL.")
