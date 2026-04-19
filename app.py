"""
Synchronous Perplexity AI example.
"""
from config import PERPLEXITY_COOKIES
from services.perplexity_client import PerplexityService

pplx = PerplexityService(PERPLEXITY_COOKIES)

response = pplx.ask(
  query="What is your usage limit and how do you handle rate limiting?",
  incognito=True,
)
print(response['answer'])
