# GroceryMate AI

A Streamlit grocery planning chatbot built with LangChain. It routes queries with **RunnableBranch**, generates multiple outputs with **RunnableParallel**, and returns validated responses using **Pydantic structured output**.

Focused on Bangladeshi households: meal plans, ingredient substitutions, and budget estimates in BDT.

**Live demo:** [https://grocerymate-ai.streamlit.app/](https://grocerymate-ai.streamlit.app/)

## Features

- Chat interface with history and optional clear-chat
- Query classification into `meal_plan`, `substitution`, `budget`, or `other`
- Out-of-scope queries get a short polite refusal (no shopping list or cost)
- Parallel generation of answer, shopping list, and cost estimate for grocery queries
- Shopping list items include name, quantity, and estimated individual price in BDT
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
Groq Classifier → meal_plan | substitution | budget | other
      │
      ├─ other ──► RunnableBranch (other_prompt)
      │              → short polite refusal only
      │              → skips shopping, cost, and parallel
      │
      └─ grocery ► RunnableBranch (Gemini)
                     meal_plan | substitution | budget
                           │
                           ▼
                     RunnableParallel (Gemini)
                       answer
                       shopping_list  (name, quantity, price)
                       estimated_cost (item prices + total)
                           │
                           ▼
                     Pydantic Structured Output (Gemini)
                           │
                           ▼
                     Streamlit Chat UI
```

### LangChain pipeline graph

Generated with `parallel_chain.get_graph().print_ascii()` and `structured_chain.get_graph().print_ascii()`:

**RunnableParallel** (`answer` via Branch + `shopping_list` + `estimated_cost`):

```
                    +----------------------------------------------------+
                    | Parallel<answer,shopping_list,estimated_cost>Input |
                    +----------------------------------------------------+
                            ******              *             ******
                      ******                     *                  ******
                   ***                           *                        ******
    +----------------+                  +----------------+                      ***
    | PromptTemplate |                  | PromptTemplate |                        *
    +----------------+                  +----------------+                        *
             *                                   *                                *
             *                                   *                                *
             *                                   *                                *
+------------------------+          +------------------------+                    *
| ChatGoogleGenerativeAI |          | ChatGoogleGenerativeAI |                    *
+------------------------+          +------------------------+                    *
             *                                   *                                *
             *                                   *                                *
             *                                   *                                *
    +-----------------+                 +-----------------+                 +--------+
    | StrOutputParser |                 | StrOutputParser |               **| Branch |
    +-----------------+*****            +-----------------+         ******  +--------+
                            ******               *            ******
                                  ******        *       ******
                                        ***     *    ***
                    +-----------------------------------------------------+
                    | Parallel<answer,shopping_list,estimated_cost>Output |
                    +-----------------------------------------------------+
```

**Pydantic structured output:**

```
      +-------------+
      | PromptInput |
      +-------------+
             *
             *
             *
    +----------------+
    | PromptTemplate |
    +----------------+
             *
             *
             *
+------------------------+
| ChatGoogleGenerativeAI |
+------------------------+
             *
             *
             *
 +----------------------+
 | PydanticOutputParser |
 +----------------------+
             *
             *
             *
    +-----------------+
    | GroceryResponse |
    +-----------------+
```

## RunnableBranch

After classification, `RunnableBranch` (`conditional_chain`) selects one specialist prompt:

| Category       | Pipeline                    |
|----------------|-----------------------------|
| `substitution` | Substitution assistant      |
| `budget`       | Budget estimate assistant   |
| `meal_plan`    | Meal plan assistant         |
| default        | Out-of-scope (`other`)      |

If the classifier returns `other`, only this branch runs. Shopping list, cost estimate, and `RunnableParallel` are not used.

## RunnableParallel

For `meal_plan`, `substitution`, and `budget` queries, `RunnableParallel` (`parallel_chain`) runs three generators at once:

- **answer** — branched specialist response
- **shopping_list** — items with name, quantity, and estimated price in BDT
- **estimated_cost** — per-item prices and total cost in BDT

## Pydantic Structured Output

`schemas.py` defines `GroceryResponse`:

- `answer` — main reply
- `shopping_list` — list of items (each with name, quantity, and price)
- `estimated_cost_bdt` — total cost in Taka (`>= 0`), summed in code from shopping-list item prices
- `category` — display label (`Meal Plan`, `Substitution`, `Budget Estimate`, or `Out of Scope`)
- `confidence` — cost confidence (`0`–`1`)

For grocery queries, a final LangChain step uses `PydanticOutputParser` so the model output is validated before display. For `other`, a short refusal is returned directly with an empty shopping list and cost `0`.

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

- **Meal plan:** “Make a cheap 5-day meal plan for a family of 4”
- **Substitution:** “What can I use instead of chicken for curry?”
- **Budget:** “Estimate grocery cost for a week for 2 people in Dhaka”
- **Out of scope:** “Who won the cricket match yesterday?”

## Tech Stack

- Python, Streamlit
- LangChain (`PromptTemplate`, `RunnableBranch`, `RunnableParallel`, `PydanticOutputParser`)
- ChatGroq (`openai/gpt-oss-20b`) — classifier
- ChatGoogleGenerativeAI (`gemini-3.5-flash-lite`) — generation & structured output
- Pydantic v2

## Notes

- Do not commit `.env` or API keys.
- Free-tier rate limits may apply; wait and retry if you see `429` / TPM errors.
- Responses are polite and direct, without greetings or introductions.
- Meal plans use the duration in the query; if none is given, they default to 7 days.
