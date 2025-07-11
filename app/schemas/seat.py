import strawberry

@strawberry.type
class SeatType:
    id: int
    flight_id: int
    seat_number: str
    is_available: bool
