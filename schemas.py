from pydantic import BaseModel, Field

class GroceryResponse(BaseModel):
    answer: str = Field(
        description="Full main answer. For meal plans include every day with Breakfast, Lunch, and Dinner. Do not summarize."
    )
    shopping_list: list[str] = Field(description="List of grocery items")
    estimated_cost_bdt: float = Field(
        ge=0, description="Estimated grocery cost in Bangladeshi Taka"
    )
    category: str = Field(description="Category of the grocery query")
    confidence: float = Field(
        ge=0, le=1, description="Confidence in the estimated cost"
    )
