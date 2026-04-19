"""
Perplexity AI example with your own account cookies.
"""
from services.perplexity_client import PerplexityService

# Use your own Perplexity account cookies
cookies = {
    "cookie_name": "cookie_value"
}

pplx = PerplexityService(cookies=cookies)
response = pplx.ask("Use reasoning mode", stream=False)
print(response)
