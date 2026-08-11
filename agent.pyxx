import json
from google.adk.agents import Agent


def get_menu(query: str = "") -> str:
    """Retrieve relevant coffee menu items."""
    with open("menu.json", "r") as f:
        menu = json.load(f)

    if not query:
        return json.dumps(menu)

    query_words = query.lower().split()
    results = []

    for item in menu:
        text = (
            item["name"]
            + " "
            + item["description"]
            + " "
            + " ".join(item["tags"])
        ).lower()

        if any(word in text for word in query_words):
            results.append(item)

    if not results:
        results = menu

    return json.dumps(results[:3])


root_agent = Agent(
    name="barista_agent",
    model="gemini-2.5-flash",
    description="A personalized AI coffee shop assistant.",
    instruction="""
You are a personalized AI coffee shop assistant.

Use the get_menu tool before making recommendations.

Rules:
1. Never recommend a product that is not in the menu.
2. Consider the customer's budget and preferences.
3. Consider hot/cold, strong/mild and sweet/low-sweet preferences.
4. Always check allergens when the customer mentions an allergy.
5. Never invent prices or products.
6. If the requested product is unavailable, suggest an available alternative.
7. Keep responses concise and useful.
""",
    tools=[get_menu],
)
