from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableBranch, RunnableParallel

from prompts import (
    classifier_prompt,
    meal_plan_prompt,
    substitution_prompt,
    budget_prompt,
    shopping_prompt,
    cost_prompt,
    final_prompt,
)
from schemas import GroceryResponse

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile")
parser = StrOutputParser()
pydantic_parser = PydanticOutputParser(pydantic_object=GroceryResponse)

CATEGORY_NAMES = {
    "substitution": "Substitution",
    "budget": "Budget Estimate",
    "meal_plan": "Meal Plan",
}

classifier_chain = classifier_prompt | model | parser
conditional_chain = RunnableBranch(
    (lambda x: x["category"] == "substitution", substitution_prompt | model | parser),
    (lambda x: x["category"] == "budget", budget_prompt | model | parser),
    meal_plan_prompt | model | parser,
)
parallel_chain = RunnableParallel(
    answer=conditional_chain,
    shopping_list=shopping_prompt | model | parser,
    estimated_cost=cost_prompt | model | parser,
)
structured_chain = (
    final_prompt.partial(format_instruction=pydantic_parser.get_format_instructions())
    | model
    | pydantic_parser
)


def get_response(query: str) -> GroceryResponse:
    category = classifier_chain.invoke({"query": query}).strip().lower()
    result = parallel_chain.invoke({"query": query, "category": category})
    return structured_chain.invoke(
        {
            **result,
            "category": CATEGORY_NAMES.get(category, "Meal Plan"),
        }
    )
