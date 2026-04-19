"""
Asynchronous Perplexity AI service wrapper.
"""
import perplexity_async


class AsyncPerplexityService:
    """Wrapper for Perplexity AI asynchronous client."""

    def __init__(self, cookies: dict | None = None):
        self.cookies = cookies
        self.client = None

    async def connect(self):
        self.client = await (
            perplexity_async.Client(self.cookies)
            if self.cookies
            else perplexity_async.Client()
        )

    async def ask(self, query: str, follow_up=None, stream: bool = False):
        return await self.client.search(
            query,
            mode="auto",
            model=None,
            sources=["web"],
            files={},
            stream=stream,
            language="en-US",
            follow_up=follow_up,
            incognito=False,
        )
