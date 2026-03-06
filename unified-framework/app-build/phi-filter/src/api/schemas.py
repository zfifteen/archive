from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class SignalRequest(BaseModel):
    price: float = Field(..., description="Current asset price", example=150.25)
    support: float = Field(
        ...,
        description="Key support level identified by existing strategy",
        example=148.0,
    )
    resistance: float = Field(
        ...,
        description="Key resistance level identified by existing strategy",
        example=155.0,
    )
    atr: float = Field(
        ...,
        description="Average True Range (volatility measure) for the asset",
        example=2.5,
    )


class SignalResponse(BaseModel):
    passed: bool = Field(
        ..., description="True if the signal passes geometric constraints"
    )
    rejection_reason: Optional[str] = Field(
        None,
        description="Reason for rejection if passed is False",
        example="Signal is outside geometric volatility bands",
    )
    confidence: float = Field(
        ...,
        description="Confidence score (0.0 - 1.0) of the geometric filter",
        example=0.85,
    )
    filter_time_ns: int = Field(
        ..., description="Filtering latency in nanoseconds", example=1200
    )


class BatchSignalRequest(BaseModel):
    signals: List[SignalRequest] = Field(
        ...,
        description="List of signals to process in batch",
        min_items=1,
        max_items=100,
    )


class BatchSignalResponse(BaseModel):
    results: List[SignalResponse] = Field(
        ..., description="List of results corresponding to the input signals"
    )


class FibonacciRequest(BaseModel):
    high: float = Field(..., description="Recent swing high", example=160.0)
    low: float = Field(..., description="Recent swing low", example=140.0)
    current_price: float = Field(..., description="Current asset price", example=152.5)
    atr: float = Field(..., description="Average True Range", example=3.0)


class HarmonicLatticeRequest(BaseModel):
    base_price: float = Field(
        ...,
        description="Base price for lattice generation (e.g., pivot point or sqrt(high*low))",
        example=100.0,
    )
    atr: float = Field(..., description="Average True Range", example=2.0)
    harmonic_ratio: Optional[float] = Field(
        None, description="Custom harmonic ratio (default: 1.618034)"
    )
    k_min: Optional[int] = Field(
        -10, description="Minimum power for harmonic lattice expansion"
    )
    k_max: Optional[int] = Field(
        10, description="Maximum power for harmonic lattice expansion"
    )


class UsageResponse(BaseModel):
    api_key: str = Field(..., description="The API Key being queried")
    total_requests: int = Field(
        ..., description="Total number of requests processed for this key"
    )
    last_request_time: Optional[int] = Field(
        None, description="Unix timestamp of the last request"
    )
    rate_limit_remaining: int = Field(
        ..., description="Remaining requests in the current window"
    )


class WebhookRegistration(BaseModel):
    url: str = Field(
        ...,
        description="The callback URL to receive signal alerts",
        example="https://my-trading-bot.com/webhooks/signals",
    )
    events: List[str] = Field(
        default=["signal.accepted", "signal.rejected"],
        description="List of events to subscribe to",
    )
    secret: Optional[str] = Field(
        None, description="Secret key for HMAC signature verification"
    )


class WebhookResponse(BaseModel):
    webhook_id: str = Field(
        ..., description="Unique identifier for the registered webhook"
    )
    status: str = Field("active", description="Status of the webhook registration")


class BacktestFibonacciRequest(BaseModel):
    highs: List[float] = Field(..., description="Array of historical swing highs")
    lows: List[float] = Field(..., description="Array of historical swing lows")
    prices: List[float] = Field(..., description="Array of historical close prices")
    atrs: List[float] = Field(..., description="Array of historical ATR values")


class BacktestCustomRequest(BaseModel):
    prices: List[float] = Field(..., description="Array of historical signal prices")
    supports: List[float] = Field(..., description="Array of historical support levels")
    resistances: List[float] = Field(
        ..., description="Array of historical resistance levels"
    )
    atrs: List[float] = Field(..., description="Array of historical ATR values")


class BacktestSignal(BaseModel):
    index: int = Field(
        ..., description="The index in the input array where the signal was found"
    )
    price: Optional[float] = Field(None, description="The price at the signal index")
    level_price: Optional[float] = Field(
        None, description="The price of the geometric level (for Fibonacci)"
    )
    ratio: Optional[float] = Field(None, description="The ratio (for Fibonacci)")
    confidence: float = Field(..., description="Filter confidence at this point")


class BacktestResponse(BaseModel):
    total_intervals: int = Field(..., description="Total number of intervals scanned")
    valid_signals_found: int = Field(
        ..., description="Number of signals that passed geometric filtering"
    )
    rejection_rate: float = Field(
        ..., description="Percentage of potential signals rejected by the filter"
    )
    signals: List[BacktestSignal] = Field(
        ..., description="List of valid signals found during the scan"
    )


class CreateAPIKeyRequest(BaseModel):
    description: str = Field("", description="Optional description for the API key")
    expires_days: int = Field(
        365, description="Days until key expires (0 for no expiration)", ge=0
    )
    rate_limit: int = Field(1000, description="Requests per hour", ge=1, le=10000)


class APIKeyResponse(BaseModel):
    key: str = Field(..., description="The API key (only shown once)")
    key_prefix: str = Field(..., description="First 8 characters for identification")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    rate_limit: int = Field(..., description="Requests per hour")


class APIKeyInfo(BaseModel):
    key_prefix: str = Field(..., description="First 8 characters for identification")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    rate_limit: int = Field(..., description="Requests per hour")
    is_active: bool = Field(..., description="Whether the key is active")
    description: str = Field("", description="Key description")


class ListAPIKeysResponse(BaseModel):
    keys: List[APIKeyInfo] = Field(..., description="List of API keys for the user")


class RevokeAPIKeyRequest(BaseModel):
    key_prefix: str = Field(..., description="First 8 characters of the key to revoke")


class UpdateAPIKeyLimitsRequest(BaseModel):
    key_prefix: str = Field(..., description="First 8 characters of the key to update")
    new_rate_limit: int = Field(
        ..., description="New rate limit (requests per hour)", ge=1, le=10000
    )
