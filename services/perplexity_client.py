"""
Synchronous Perplexity AI service wrapper.
"""
import json
import perplexity


class PerplexityService:
    """Wrapper for Perplexity AI synchronous client."""

    def __init__(self, cookies: dict | None = None):
        self.client = perplexity.Client(cookies) if cookies else perplexity.Client()

    def ask(self, query: str, follow_up=None, stream: bool = False, incognito: bool = False, mode: str = "auto", model: str = None):
        return self.client.search(
            query,
            mode=mode,
            model=model,
            sources=["web"],
            files={},
            stream=stream,
            language="en-US",
            follow_up=follow_up,
            incognito=incognito,
        )

    def ask_advanced(self, query: str, mode: str = "auto", model: str = None, incognito: bool = False) -> dict:
        """
        Send query and parse JSON response.

        Args:
            query: The prompt to send
            mode: Search mode ('auto', 'pro', 'reasoning', 'deep research')
            model: Model to use (depends on mode)
            incognito: Whether to use incognito mode

        Returns:
            Parsed JSON response as dict

        Raises:
            ValueError: If response is not valid JSON or missing 'items' key
        """
        response = self.ask(query, stream=False, incognito=incognito, mode=mode, model=model)

        # The response contains 'answer' field with the JSON content
        if 'answer' not in response:
            raise ValueError("Response missing 'answer' field")

        # try:
        #     parsed = json.loads(response['answer'])
        # except json.JSONDecodeError as e:
        #     raise ValueError(f"Invalid JSON in response: {e}")

        # if 'items' not in parsed:
        #     raise ValueError("Response JSON missing 'items' key")

        return response['answer']
