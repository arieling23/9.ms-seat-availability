import httpx 
from app.utils.logger import logger

# Dirección del microservicio ms-flight-catalog
FLIGHT_CATALOG_URL = "http://54.91.170.59:8082/api/flight-catalog"  # Cambia el puerto si es necesario

async def flight_exists(flight_id: int) -> bool:
    query = """
    query ($id: Int!) {
        flight(id: $id) {
            id
        }
    }
    """
    variables = {"id": flight_id}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                FLIGHT_CATALOG_URL,
                json={"query": query, "variables": variables},
                timeout=5.0
            )
            if response.status_code != 200:
                logger.error(f"Error HTTP al consultar vuelo {flight_id}: código {response.status_code}")
                return False

            data = response.json()
            flight = data.get("data", {}).get("flight")

            if flight:
                logger.info(f"✅ Vuelo {flight_id} verificado desde ms-flight-catalog.")
                return True
            else:
                logger.warning(f"⚠️ Vuelo {flight_id} no encontrado en ms-flight-catalog.")
                return False

    except Exception as e:
        logger.error(f"❌ Error al consultar vuelo {flight_id} en ms-flight-catalog: {str(e)}")
        return False
