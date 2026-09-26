from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableBranch, RunnableParallel
import re

from prompts import (
    classifier_prompt,
    meal_plan_prompt,
    substitution_prompt,
    budget_prompt,
    other_prompt,
    shopping_prompt,
    cost_prompt,
    final_prompt,
)
from schemas import GroceryResponse

load_dotenv()

classifier_model = ChatGroq(model="openai/gpt-oss-20b")
generation_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

parser = StrOutputParser()
pydantic_parser = PydanticOutputParser(pydantic_object=GroceryResponse)

CATEGORY_NAMES = {
    "substitution": "Substitution",
    "budget": "Budget Estimate",
    "meal_plan": "Meal Plan",
    "other": "Out of Scope",
}

classifier_chain = classifier_prompt | classifier_model | parser
conditional_chain = RunnableBranch(
    (
        lambda x: x["category"] == "substitution",
        substitution_prompt | generation_model | parser,
    ),
    (
        lambda x: x["category"] == "budget",
        budget_prompt | generation_model | parser,
    ),
    (
        lambda x: x["category"] == "meal_plan",
        meal_plan_prompt | generation_model | parser,
    ),
    other_prompt | generation_model | parser,
)
parallel_chain = RunnableParallel(
    answer=conditional_chain,
    shopping_list=shopping_prompt | generation_model | parser,
    estimated_cost=cost_prompt | generation_model | parser,
)
structured_chain = (
    final_prompt.partial(format_instruction=pydantic_parser.get_format_instructions())
    | generation_model
    | pydantic_parser
)

def get_response(query: str) -> GroceryResponse:
    category = classifier_chain.invoke({"query": query}).strip().lower()
    if category == "other":
        answer = conditional_chain.invoke({"query": query, "category": category})
        return GroceryResponse(
            answer=answer,
            shopping_list=[],
            estimated_cost_bdt=0,
            category=CATEGORY_NAMES["other"],
            confidence=1,
        )
    result = parallel_chain.invoke({"query": query, "category": category})
    response = structured_chain.invoke(
        {
            **result,
            "category": CATEGORY_NAMES.get(category, "Meal Plan"),
        }
    )
    total = 0.0
    for item in response.shopping_list:
        nums = re.findall(r"\d+(?:\.\d+)?", item)
        if nums:
            total += float(nums[-1])
    response.estimated_cost_bdt = round(total, 2)
    return response
