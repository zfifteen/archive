from fastapi import FastAPI
from pydantic import BaseModel


class FilterRequest(BaseModel):
    price: float
    support: float
    resistance: float
    volatility: float
    band_multiplier: float = 2.0


app = FastAPI()


def phi_harmonic_filter(price, support, resistance, volatility, band_multiplier=2.0):
    mid_point = 0.5 * (support + resistance)
    band_width = band_multiplier * volatility
    lower_bound = mid_point - band_width
    upper_bound = mid_point + band_width
    return lower_bound <= price <= upper_bound


@app.post("/filter")
def filter_signal(request: FilterRequest):
    result = phi_harmonic_filter(
        request.price,
        request.support,
        request.resistance,
        request.volatility,
        request.band_multiplier,
    )
    return {"valid": result}
