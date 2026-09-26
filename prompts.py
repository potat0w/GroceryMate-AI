from langchain_core.prompts import PromptTemplate

classifier_prompt = PromptTemplate(
    template="""Classify the following grocery query into one of these categories:

meal_plan
substitution
budget
other

Query: {query}

Return only the category name.""",
    input_variables=["query"],
)

meal_plan_prompt = PromptTemplate(
    template="""You are a grocery planning assistant for Bangladeshi households.

Create a practical meal plan for the duration requested in the query.
If no duration is given, use 7 days.
Reply politely and directly.

Query: {query}

Use common and affordable Bangladeshi foods.""",
    input_variables=["query"],
)

substitution_prompt = PromptTemplate(
    template="""You are a grocery planning assistant for Bangladeshi households.

Suggest suitable ingredient substitutions for the following request:

{query}

Suggest alternatives that are commonly available in Bangladesh.""",
    input_variables=["query"],
)

budget_prompt = PromptTemplate(
    template="""You are a grocery budget assistant for Bangladeshi households.

Give budget guidance for the following request:

{query}

Use approximate prices in Bangladeshi Taka.""",
    input_variables=["query"],
)

other_prompt = PromptTemplate(
    template="""Politely explain that you can only help with meal planning,
ingredient substitutions, and grocery budgeting.

Query: {query}""",
    input_variables=["query"],
)

shopping_prompt = PromptTemplate(
    template="""Category: {category}

If category is other, return an empty shopping list.
Otherwise, generate a shopping list for the following grocery request:

{query}

Use common grocery items available in Bangladesh.""",
    input_variables=["query", "category"],
)

cost_prompt = PromptTemplate(
    template="""Category: {category}

If category is other, return an estimated cost of 0.
Otherwise, estimate grocery costs for the following request using approximate Bangladesh market prices.

Show each item with its approximate price.
End with the total cost in BDT.

Query: {query}""",
    input_variables=["query", "category"],
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

Include estimated individual item prices in the shopping_list.
Use the total from estimated_cost as estimated_cost_bdt.
Set confidence between 0 and 1.

{format_instruction}""",
    input_variables=[
        "answer",
        "shopping_list",
        "estimated_cost",
        "category",
        "format_instruction",
    ],
)
