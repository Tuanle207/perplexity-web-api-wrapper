"""
Streaming Perplexity AI example.
"""
from services.perplexity_client import PerplexityService

pplx = PerplexityService()

# First query
first = pplx.ask("What is FastAPI?")
print("First response:", first)

# Streaming follow-up query
print("\nStreaming follow-up response:")
for chunk in pplx.ask("Give me a short example project structure", follow_up=first, stream=True):
    print(chunk)
