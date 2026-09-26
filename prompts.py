from langchain_core.prompts import PromptTemplate

classifier_prompt = PromptTemplate(
    template="""Classify the query into one category:

meal_plan - meal planning or what to cook
substitution - ingredient replacements
budget - grocery price, cost, or budget
other - anything unrelated to groceries

Query: {query}

Return only the category name.""",
    input_variables=["query"],
)

meal_plan_prompt = PromptTemplate(
    template="""You are a grocery planning assistant for Bangladeshi households.

Create a practical meal plan for the duration requested in the query.
If no duration is given, use 7 days.
Reply politely and directly without greetings or introductions.

Query: {query}

Use common and affordable Bangladeshi foods.""",
    input_variables=["query"],
)

substitution_prompt = PromptTemplate(
    template="""You are a grocery planning assistant for Bangladeshi households.

Suggest suitable ingredient substitutions for the following request.
Reply politely and directly without greetings or introductions.

Query: {query}

Suggest alternatives that are commonly available in Bangladesh.""",
    input_variables=["query"],
)

budget_prompt = PromptTemplate(
    template="""You are a grocery budget assistant for Bangladeshi households.

Give budget guidance for the following request.
Reply politely and directly without greetings or introductions.

Query: {query}

Use approximate prices in Bangladeshi Taka.""",
    input_variables=["query"],
)

other_prompt = PromptTemplate(
    template="""Reply politely and directly without greetings or introductions.
Explain briefly that you can only help with meal planning, ingredient substitutions, and grocery budgeting.
Do not include a shopping list or cost estimate.

Query: {query}""",
    input_variables=["query"],
)

shopping_prompt = PromptTemplate(
    template="""Create a grocery shopping list for the following request.

For every item include:
- item name
- quantity
- estimated individual price in BDT

Every item must have its own estimated price.
Use approximate Bangladesh market prices.
Do not list any item without a price.

Query: {query}""",
    input_variables=["query"],
)

cost_prompt = PromptTemplate(
    template="""Estimate grocery costs for the following request using approximate Bangladesh market prices.

Show each item with quantity and estimated individual price in BDT.
End with the total cost in BDT as the sum of all item prices.

Query: {query}""",
    input_variables=["query"],
)

final_prompt = PromptTemplate(
    template="""Create a final structured response from the following information.

Answer:
{answer}

Shopping List:
{shopping_list}

Estimated Cost:
{estimated_cost}

Category:
{category}

Every shopping_list entry must include item name, quantity, and estimated individual price in BDT.
Do not include any item without a price.
Put the price as the last number in each shopping_list entry.
Set confidence between 0 and 1.
Reply politely and directly without greetings or introductions.

{format_instruction}""",
    input_variables=[
        "answer",
        "shopping_list",
        "estimated_cost",
        "category",
        "format_instruction",
    ],
)
