from pydantic import BaseModel
from typing import Optional


class FlowResponse(BaseModel):
    client_ip: str
    client_port: int
    server_ip: str
    server_port: int
    protocol: str
    ip_version: int
    packets_sent: int
    packets_received: int
    bytes_sent: int
    bytes_received: int
    sni: Optional[str] = None
    decision: Optional[str] = None
    start_time: float