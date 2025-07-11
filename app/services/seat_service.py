from sqlalchemy.future import select
from app.models.seat import Seat
from app.utils.logger import logger

async def get_available_seats(session, flight_id: int):
    result = await session.execute(
        select(Seat).where(Seat.flight_id == flight_id, Seat.is_available == True)
    )
    return result.scalars().all()

async def create_default_seats(session, flight_id: int):
    logger.info(f"🎫 Creando 30 asientos para el vuelo {flight_id}")
    rows = ['A', 'B', 'C', 'D', 'E', 'F']
    seats = []

    for row in range(1, 6):  # Filas 1-5
        for letter in rows:  # Columnas A-F
            seat_number = f"{row}{letter}"
            seats.append(
                Seat(
                    flight_id=flight_id,
                    seat_number=seat_number,
                    is_available=True
                )
            )

    session.add_all(seats)
    await session.commit()
    logger.info("✅ Asientos creados correctamente.")
