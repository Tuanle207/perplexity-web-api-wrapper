"""
Batch processor for words extraction using Perplexity AI.
"""
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Tuple, Set, Dict, List

from config import (
    BATCH_SIZE,
    BATCH_DELAY_SECONDS,
    BATCH_MODE,
    BATCH_MODEL,
    PROCESS_START_INDEX,
    PROCESS_END_INDEX,
    PROMPT_TEMPLATE_FILE,
    WORDS_INPUT_FILE,
    WORDS_OUTPUT_DIR,
    BATCH_STATE_FILE,
)
from services.perplexity_client import PerplexityService


class WordsBatchProcessor:
    """Process words in batches through Perplexity AI."""

    def __init__(
        self,
        cookies: Optional[dict] = None,
        batch_size: int = BATCH_SIZE,
        delay_seconds: float = BATCH_DELAY_SECONDS,
        mode: str = BATCH_MODE,
        model: str = BATCH_MODEL,
        process_start_index: Optional[int] = PROCESS_START_INDEX,
        process_end_index: Optional[int] = PROCESS_END_INDEX,
    ):
        self.cookies = cookies
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.mode = mode
        self.model = model
        self.process_start_index = process_start_index
        self.process_end_index = process_end_index
        self.client = PerplexityService(cookies)

        # Ensure output directory exists
        Path(WORDS_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

        # Load prompt template
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load the prompt template from file."""
        with open(PROMPT_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def get_total_words(self) -> int:
        """Count total words in input file."""
        with open(WORDS_INPUT_FILE, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)

    def get_completed_batches(self) -> Set[str]:
        """Scan output directory for completed batch files."""
        completed = set()
        output_path = Path(WORDS_OUTPUT_DIR)

        if not output_path.exists():
            return completed

        for file in output_path.glob('*.json'):
            # Extract batch range from filename (e.g., "1-50.json" -> "1-50")
            batch_id = file.stem
            if re.match(r'^\d+-\d+$', batch_id):
                completed.add(batch_id)

        return completed

    def get_next_batch_range(self, completed_batches: Set[str]) -> Optional[Tuple[int, int]]:
        """
        Calculate next unprocessed batch range (1-based indexing).
        Respects process_start_index and process_end_index bounds if set.

        Returns:
            Tuple of (start, end) or None if all batches completed
        """
        total = self.get_total_words()
        completed_ranges = set()

        for batch_id in completed_batches:
            start, end = map(int, batch_id.split('-'))
            completed_ranges.add((start, end))

        # Apply processing bounds
        search_start = self.process_start_index if self.process_start_index else 1
        search_end = self.process_end_index if self.process_end_index else total

        # Find the first gap in completed ranges within bounds
        current = search_start
        while current <= search_end:
            end = min(current + self.batch_size - 1, total, search_end)

            if (current, end) not in completed_ranges:
                return (current, end)

            current = end + 1

        return None

    def load_words(self, start: int, end: int) -> list[str]:
        """
        Load words from input file for given range (1-based indexing).

        Args:
            start: Starting line number (1-based, inclusive)
            end: Ending line number (1-based, inclusive)

        Returns:
            List of words
        """
        words = []
        with open(WORDS_INPUT_FILE, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                if start <= i <= end:
                    words.append(line.strip())
                elif i > end:
                    break

        return words

    def build_prompt(self, words: List) -> str:
        """
        Build prompt by injecting words into template.

        Args:
            words: List of words to process

        Returns:
            Complete prompt string
        """
        words_list = '\n'.join(words)
        return self.prompt_template.replace('[WORDS_LIST]', words_list)

    def get_output_path(self, start: int, end: int) -> Path:
        """Generate output file path for batch."""
        return Path(WORDS_OUTPUT_DIR) / f'{start}-{end}.json'

    def process_batch(self, start: int, end: int) -> Dict:
        """
        Process a single batch of words.

        Args:
            start: Starting index (1-based)
            end: Ending index (1-based)

        Returns:
            The processed JSON response

        Raises:
            Exception: If processing fails
        """
        print(f'Processing batch {start}-{end}...')

        # Load words for this batch
        words = self.load_words(start, end)
        print(f'  Loaded {len(words)} words')

        # Build prompt
        prompt = self.build_prompt(words)
        print(f'  Built prompt ({len(prompt)} chars)')

        # Send to Perplexity
        print(f'  Sending to Perplexity (mode={self.mode}, model={self.model})...')
        response = self.client.ask_advanced(prompt, mode=self.mode, model=self.model, incognito=False)

        # Validate response
        items_count = end - start + 1  # Assuming one item per word in response
        print(f'  Received {items_count} items')

        # Save to file
        output_path = self.get_output_path(start, end)
        with open(output_path, 'w', encoding='utf-8') as f:
            # json.dump(response, f, indent=2, ensure_ascii=False)
            # save as txt
            f.write(response)
        print(f'  Saved to {output_path}')

        return response

    def save_state(self, processed_batches: List, current_batch: Optional[str] = None):
        """Save current processing state to file."""
        state = {
            'total_words': self.get_total_words(),
            'batch_size': self.batch_size,
            'processed_batches': sorted(processed_batches),
            'current_batch': current_batch,
            'last_updated': datetime.now().isoformat(),
        }

        with open(BATCH_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> Optional[Dict]:
        """Load previous processing state from file."""
        if not Path(BATCH_STATE_FILE).exists():
            return None

        with open(BATCH_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def process_all(
        self,
        max_batches: Optional[int] = None,
        on_progress: Optional[Callable] = None,
    ) -> Dict:
        """
        Process all uncompleted batches.

        Args:
            max_batches: Maximum number of batches to process (None for unlimited)
            on_progress: Callback function(batch_start, batch_end, processed_count, total_batches, eta_seconds)

        Returns:
            Summary dict with processing stats
        """
        total_words = self.get_total_words()

        # Calculate processing range bounds
        range_start = self.process_start_index if self.process_start_index else 1
        range_end = self.process_end_index if self.process_end_index else total_words
        range_size = range_end - range_start + 1

        # Calculate total batches within processing range
        total_batches = (range_size + self.batch_size - 1) // self.batch_size

        print(f'Total words: {total_words}')
        print(f'Processing range: {range_start:,} - {range_end:,} ({range_size:,} words)')
        print(f'Total batches in range: {total_batches}')
        print(f'Batch size: {self.batch_size}')
        print(f'Mode: {self.mode}, Model: {self.model}')

        # Get completed batches
        completed_batches = self.get_completed_batches()

        # Filter completed batches to only those within our processing range
        completed_in_range = set()
        for batch_id in completed_batches:
            start, end = map(int, batch_id.split('-'))
            # Check if batch overlaps with our processing range
            if end >= range_start and start <= range_end:
                completed_in_range.add(batch_id)

        print(f'Already completed in range: {len(completed_in_range)} batches')

        processed_count = 0
        failed_batches = []
        consecutive_failures = 0
        MAX_CONSECUTIVE_FAILURES = 10
        RETRY_DELAY = 10  # seconds

        # Track timing for ETA calculation
        import time as time_module
        start_time = time_module.time()
        batch_times = []  # Track time for each completed batch

        try:
            while True:
                # Check max batches limit
                if max_batches is not None and processed_count >= max_batches:
                    print(f'Reached max batches limit: {max_batches}')
                    break

                # Get next batch
                batch_range = self.get_next_batch_range(completed_batches)
                if batch_range is None:
                    print('All batches completed!')
                    break

                start, end = batch_range
                batch_id = f'{start}-{end}'

                try:
                    # Track batch start time
                    batch_start_time = time_module.time()

                    # Process batch
                    self.process_batch(start, end)
                    completed_batches.add(batch_id)
                    processed_count += 1
                    consecutive_failures = 0  # Reset on success

                    # Record batch time
                    batch_duration = time_module.time() - batch_start_time
                    batch_times.append(batch_duration)

                    # Calculate ETA
                    avg_time_per_batch = sum(batch_times) / len(batch_times) if batch_times else 0
                    remaining_batches = total_batches - len(completed_batches)
                    eta_seconds = int(avg_time_per_batch * remaining_batches)

                    # Save state
                    self.save_state(sorted(completed_batches), batch_id)

                    # Call progress callback (actual total progress including previous runs)
                    if on_progress:
                        on_progress(start, end, len(completed_batches), total_batches, eta_seconds)

                    # Delay before next batch
                    if processed_count < max_batches if max_batches else True:
                        print(f'  Waiting {self.delay_seconds}s before next batch...')
                        time.sleep(self.delay_seconds)

                except Exception as e:
                    print(f'  ERROR processing batch {batch_id}: {e}')
                    failed_batches.append(batch_id)
                    consecutive_failures += 1

                    # Stop if too many consecutive failures
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        print(f'  Stopping: {consecutive_failures} consecutive failures reached.')
                        break

                    # Delay before retry
                    print(f'  Waiting {RETRY_DELAY}s before retry...')
                    time.sleep(RETRY_DELAY)

                    # Continue with next batch instead of stopping

        except KeyboardInterrupt:
            print('\nInterrupted by user. Saving state...')

        # Final state save
        self.save_state(sorted(completed_batches))

        return {
            'total_words': total_words,
            'total_batches': total_batches,
            'completed_batches': len(completed_batches),
            'processed_this_run': processed_count,
            'failed_batches': failed_batches,
            'consecutive_failures': consecutive_failures,
        }
