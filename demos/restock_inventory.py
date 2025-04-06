"""
$ python demos/demo.py
local_llm = ChatOllama(model="granite-3.2-8b-instruct-q8_0:latest")
Executing restock order: 100 units
Restock Order Quantity: 100
"""
from dataclasses import dataclass
from typing import Any

from langchain_community.chat_models import ChatOllama


# Simple reimplementation of core Vulcan concepts
@dataclass
class Fact:
    pass

@dataclass
class Product(Fact):
    kind: str
    price: float
    in_stock: bool
    last_restock_days: int = 14

@dataclass 
class RestockOrder(Fact):
    quantity: int = 0

class RuleEngine:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.facts = {}
        self.rules = []
    
    def fact(self, fact: Fact):
        self.facts[type(fact)] = fact
    
    def rule(self, name: str, when: Any, then: Any):
        self.rules.append((name, when, then))
    
    def evaluate(self):
        if not self.enabled:
            return
            
        for name, condition, action in self.rules:
            if condition():
                action()
    
    def __getitem__(self, fact_type):
        return self.facts.get(fact_type)

def action(order: RestockOrder):
    def wrapper():
        print(f"Executing restock order: {order.quantity} units")
        engine.fact(order)
    return wrapper

def condition(func):
    return func

# Initialize with local LLM
local_llm = ChatOllama(model="granite-3.2-8b-instruct-q8_0:latest")
engine = RuleEngine(enabled=True)

# Define rules
@condition
def needs_restock(p: Product) -> bool:
    return not p.in_stock

@condition
def should_restock(p: Product) -> bool:
    prompt = (
        f"Product: {p.kind}\nPrice: ${p.price}\n"
        f"Last restocked: {p.last_restock_days} days ago\n"
        "Should we restock? Answer only 'yes' or 'no'"
    )
    response = local_llm.invoke(prompt)
    return 'yes' in str(response).lower()

def check_restock_conditions():
    product = engine[Product]
    if product is None:
        return False
    return needs_restock(product) and should_restock(product)

engine.rule(
    name="Auto-restock",
    when=check_restock_conditions,
    then=action(RestockOrder(quantity=100)))
    
if __name__ == "__main__":
    engine.fact(Product(
        kind="Laptop",
        price=899.99,
        in_stock=False,
        last_restock_days=21
    ))
    
    engine.evaluate()
    restock_order = engine[RestockOrder]
    print("Restock Order Quantity:", restock_order.quantity if restock_order is not None else 0)
