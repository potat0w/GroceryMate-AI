# GroceryMate AI

A Streamlit grocery planning chatbot built with LangChain. It routes queries with **RunnableBranch**, generates multiple outputs with **RunnableParallel**, and returns validated responses using **Pydantic structured output**.

Focused on Bangladeshi households: meal plans, ingredient substitutions, and budget estimates in BDT.

## Features

- Chat interface with history and optional clear-chat
- Query classification into `meal_plan`, `substitution`, or `budget`
- Parallel generation of answer, shopping list, and cost estimate
- Structured response validated by a Pydantic schema
- Hybrid LLMs: **Groq** for classification, **Gemini** for generation and structuring
- API keys loaded from `.env` (never committed)

## Project Structure

```
project/
├── app.py              # Streamlit chat UI
├── chatbot.py          # LangChain chains (Branch, Parallel, Pydantic)
├── prompts.py          # PromptTemplate definitions
├── schemas.py          # GroceryResponse Pydantic model
├── requirements.txt
├── .env.example
└── README.md
```

## Workflow

```
User Question
      │
      ▼
Groq Classifier → category
      │
      ▼
RunnableBranch (Gemini)
  meal_plan | substitution | budget
      │
      ▼
RunnableParallel (Gemini)
  answer + shopping_list + estimated_cost
      │
      ▼
Pydantic Structured Output (Gemini)
      │
      ▼
Streamlit Chat UI
```

## RunnableBranch

After classification, `RunnableBranch` selects one specialist prompt pipeline:

| Category       | Pipeline              |
|----------------|-----------------------|
| `substitution` | Substitution assistant |
| `budget`       | Budget estimate assistant |
| default        | Meal plan assistant   |

Implemented in `chatbot.py` as `conditional_chain`.

## RunnableParallel

For every request, `RunnableParallel` runs three generators at once:

- **answer** — branched specialist response
- **shopping_list** — grocery items for the query
- **estimated_cost** — approximate cost in BDT

Implemented as `parallel_chain` in `chatbot.py`.

## Pydantic Structured Output

`schemas.py` defines `GroceryResponse`:

- `answer` — main reply
- `shopping_list` — list of items
- `estimated_cost_bdt` — cost in Taka (`> 0`)
- `category` — query category label
- `confidence` — cost confidence (`0`–`1`)

A final LangChain step uses `PydanticOutputParser` so the model output is validated before display in Streamlit.

## Installation

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/potat0w/GroceryMate-AI.git
cd GroceryMate-AI
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create `.env` from the example and add your keys:

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
```

3. Run the app:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

## Example Queries

- **Meal plan:** “Make a cheap weekly meal plan for a family of 4”
- **Substitution:** “What can I use instead of chicken for curry?”
- **Budget:** “Estimate grocery cost for a week for 2 people in Dhaka”

## Tech Stack

- Python, Streamlit
- LangChain (`PromptTemplate`, `RunnableBranch`, `RunnableParallel`, `PydanticOutputParser`)
- ChatGroq (`openai/gpt-oss-20b`) — classifier
- ChatGoogleGenerativeAI (`gemini-3.5-flash-lite`) — generation & structured output
- Pydantic v2

## Notes

- Do not commit `.env` or API keys.
- Free-tier rate limits may apply; wait and retry if you see `429` / TPM errors.
