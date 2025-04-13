from functools import partial

from langchain_ollama import ChatOllama

from vulcan_core import Fact, RuleEngine, action, condition


# Define the fact schema
class Inventory(Fact):
    apples: int
    apple_kind: str


class AppleQualities(Fact):
    delicious: bool = False
    suitable_for_baking: bool = False


class QueuedOrder(Fact):
    apples: int = 0


# Configure the models
# gpt_4o = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=100)
# gpt_4o_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=100)
granite = ChatOllama(model="granite-3.2-8b-instruct-q8_0:latest")
condition = partial(condition, model=granite)

# Define the rule set
engine = RuleEngine()

engine.rule(
    when=condition(f"Are {Inventory.apple_kind} considered delicious by most people?"),  
    then=action(lambda: partial(AppleQualities, delicious=True)),
)

engine.rule(
    when=condition(f"Are {Inventory.apple_kind} suitable for baking pies?", model=granite),  
    then=action(lambda: partial(AppleQualities, suitable_for_baking=True)),
)

engine.rule(
    when=condition(lambda: AppleQualities.delicious and AppleQualities.suitable_for_baking),
    then=action(QueuedOrder(apples=50)),
)

# Add initial facts
engine.fact(Inventory(apples=5, apple_kind="Fuji"))

# Evaluate and print the decision
# We expect 50 apples to be queued for order if the apple variety is both delicious and suitable for baking
engine.evaluate()
print(engine.facts)