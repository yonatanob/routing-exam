from pydantic import BaseModel
from uuid import UUID


class RouteRule(BaseModel):
    url: str
    target: UUID
    exact_match: bool
    routing_rule_id: UUID


class CreateRouteRule(BaseModel):
    url: str
    target: UUID
    exact_match: bool

