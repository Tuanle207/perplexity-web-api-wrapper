"""
Asynchronous Perplexity AI example.
"""
import asyncio
from services.perplexity_async_client import AsyncPerplexityService

async def main():
    pplx = AsyncPerplexityService()
    await pplx.connect()

    response = await pplx.ask("Summarize Python context managers")
    print(response)

asyncio.run(main())
