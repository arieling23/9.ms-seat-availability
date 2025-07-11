import json
import asyncio
import aio_pika
from app.db import async_session
from app.services.seat_service import create_default_seats
from app.utils.logger import logger

RABBITMQ_URL = "amqp://ariel:rabbit123@10.0.1.30:5672"  
async def consume_flight_created():
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue("flight.created", durable=True)

        logger.info("🎧 Escuchando eventos 'flight.created'...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode("utf-8"))
                        flight_id = data.get("id")

                        if flight_id is not None:
                            logger.info(f"📩 Evento recibido: Vuelo creado con ID={flight_id}")
                            async with async_session() as session:
                                await create_default_seats(session, flight_id)
                        else:
                            logger.warning("⚠️ Evento 'flight.created' sin campo 'id'.")
                    except Exception as e:
                        logger.error(f"❌ Error al procesar evento 'flight.created': {str(e)}")

    except Exception as conn_error:
        logger.critical(f"❌ Error al conectar con RabbitMQ: {str(conn_error)}")
