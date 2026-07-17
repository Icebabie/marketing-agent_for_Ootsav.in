from typing import Optional, Literal

from pydantic import BaseModel


class UserIntent(BaseModel):
    campaign: Optional[str] = None
    content_type: Optional[str] = None
    language_style: Optional[str] = None
    design_preference: Optional[str] = None
    additional_context: Optional[list[str]] = None

class ReviewIntent(BaseModel):
    action: Literal[
        "accept",
        "edit",
        "restart",
    ]

    edit_request: Optional[str] = None