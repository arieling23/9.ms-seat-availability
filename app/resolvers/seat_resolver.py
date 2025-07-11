# app/resolvers/seat_resolver.py
import strawberry
from strawberry.types import Info
from app.schemas.seat import SeatType
from app.services.seat_service import get_available_seats
from app.services.flight_service import flight_exists
from app.db import async_session
from app.utils.auth import verify_token
from app.utils.logger import logger
from app.models.seat import Seat
from sqlalchemy import select, delete
from sqlalchemy.exc import NoResultFound


@strawberry.type
class Query:
    @strawberry.field
    async def available_seats(self, info: Info, flight_id: int) -> list[SeatType]:
        request = info.context["request"]
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        logger.info(f"📥 Consulta GraphQL: available_seats para flight_id={flight_id}")
        logger.debug(f"🔐 Token recibido: {token}")

        user = verify_token(token)
        if not user:
            logger.warning("⛔ Acceso denegado: Token inválido o no proporcionado.")
            raise Exception("No autorizado")

        logger.info(f"🔓 Usuario autenticado: {user.get('sub', 'desconocido')}")

        if not await flight_exists(flight_id):
            logger.warning(f"❌ Vuelo {flight_id} no existe según ms-flight-catalog.")
            raise Exception("Vuelo no encontrado")

        async with async_session() as session:
            seats = await get_available_seats(session, flight_id)
            logger.info(f"🎫 Se encontraron {len(seats)} asientos disponibles para el vuelo {flight_id}.")

            return [
                SeatType(
                    id=seat.id,
                    seat_number=seat.seat_number,
                    is_available=seat.is_available,
                    flight_id=seat.flight_id
                )
                for seat in seats
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_seat(self, info: Info, flight_id: int, seat_number: str) -> SeatType:
        request = info.context["request"]
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        logger.debug(f"🛠️ Mutación: create_seat para flight_id={flight_id}, seat_number={seat_number}")
        
        user = verify_token(token)
        if not user or user.get("role") != "admin":
            logger.warning("⛔ Acceso denegado: solo administradores pueden crear asientos.")
            raise Exception("Acceso no autorizado")

        async with async_session() as session:
            # ✅ Validar duplicado
            result = await session.execute(
                select(Seat).where(Seat.flight_id == flight_id, Seat.seat_number == seat_number)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise Exception(f"Ya existe el asiento '{seat_number}' para el vuelo {flight_id}")

            new_seat = Seat(flight_id=flight_id, seat_number=seat_number, is_available=True)
            session.add(new_seat)
            await session.commit()
            await session.refresh(new_seat)
            logger.info(f"✅ Asiento {seat_number} creado para vuelo {flight_id}.")

            return SeatType(
                id=new_seat.id,
                seat_number=new_seat.seat_number,
                is_available=new_seat.is_available,
                flight_id=new_seat.flight_id
            )

    @strawberry.mutation
    async def update_seat(
        self, info: Info, seat_id: int, seat_number: str, is_available: bool
    ) -> SeatType:
        token = info.context["request"].headers.get("Authorization", "").replace("Bearer ", "")
        user = verify_token(token)
        if not user or user.get("role") != "admin":
            raise Exception("Acceso no autorizado")

        async with async_session() as session:
            result = await session.execute(select(Seat).where(Seat.id == seat_id))
            seat = result.scalar_one_or_none()
            if not seat:
                raise Exception("Asiento no encontrado")

            seat.seat_number = seat_number
            seat.is_available = is_available
            await session.commit()
            await session.refresh(seat)

            return SeatType(
                id=seat.id,
                seat_number=seat.seat_number,
                is_available=seat.is_available,
                flight_id=seat.flight_id
            )

    @strawberry.mutation
    async def delete_seat(self, info: Info, seat_id: int) -> bool:
        token = info.context["request"].headers.get("Authorization", "").replace("Bearer ", "")
        user = verify_token(token)
        if not user or user.get("role") != "admin":
            raise Exception("Acceso no autorizado")

        async with async_session() as session:
            result = await session.execute(select(Seat).where(Seat.id == seat_id))
            seat = result.scalar_one_or_none()
            if not seat:
                raise Exception("Asiento no encontrado")

            await session.delete(seat)
            await session.commit()
            return True
