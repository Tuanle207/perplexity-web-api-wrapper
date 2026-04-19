# Batch Processor Reference Implementation

This document describes a reusable batch processing pattern for API operations. The implementation processes large datasets in batches through an API, with resumability, error handling, and progress tracking.

## Overview

The batch processor handles these key challenges:
- **Large datasets**: Process 450K+ items in manageable chunks
- **Resumability**: Detect completed work and continue after interruptions
- **Error handling**: Retry with delays, stop after consecutive failures
- **Progress tracking**: State persistence and real-time updates
- **Rate limiting**: Configurable delays between batches

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      run_batch_processor.py                 │
│                    (CLI Entry Point)                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 WordsBatchProcessor                         │
│                  (Core Processor)                           │
├─────────────────────────────────────────────────────────────┤
│  __init__()           │ Initialize with config             │
│  get_total_words()    │ Count input items                  │
│  get_completed_batches() │ Scan output for done work       │
│  get_next_batch_range()  │ Calculate next unprocessed      │
│  load_words()         │ Read slice of input file           │
│  build_prompt()       │ Inject data into template          │
│  process_batch()      │ Execute single batch               │
│  process_all()        │ Main loop with state management    │
│  save_state()         │ Persist progress to JSON           │
│  load_state()         │ Restore previous progress          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  PerplexityService                          │
│                 (API Client Wrapper)                        │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Pattern

### config.py

```python
# API credentials
API_COOKIES = {
    "session_token": "your_token_here",
}

# Batch processing settings
BATCH_SIZE = 50              # Items per batch
BATCH_DELAY_SECONDS = 30     # Delay between successful batches
BATCH_MODE = "pro"           # API mode/endpoint
BATCH_MODEL = None           # Specific model to use

# File paths
WORDS_INPUT_FILE = "raw/words.txt"
WORDS_OUTPUT_DIR = "output/words"
PROMPT_TEMPLATE_FILE = "prompt-template.md"
BATCH_STATE_FILE = "batch_state.json"
```

## Core Processor Class

### Class Structure

```python
class BatchProcessor:
    """Process items in batches through an API."""

    def __init__(
        self,
        auth: Optional[dict] = None,
        batch_size: int = BATCH_SIZE,
        delay_seconds: float = BATCH_DELAY_SECONDS,
        mode: str = BATCH_MODE,
        model: str = BATCH_MODEL,
    ):
        self.auth = auth
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.mode = mode
        self.model = model
        self.client = APIClient(auth)

        # Ensure output directory exists
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

        # Load prompt template
        self.prompt_template = self._load_template()
```

### Key Methods

#### 1. Count Total Items

```python
def get_total_items(self) -> int:
    """Count total items in input file."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)
```

#### 2. Scan Completed Batches

```python
def get_completed_batches(self) -> Set[str]:
    """Scan output directory for completed batch files."""
    completed = set()
    output_path = Path(OUTPUT_DIR)

    if not output_path.exists():
        return completed

    for file in output_path.glob('*.json'):
        batch_id = file.stem  # e.g., "1-50" from "1-50.json"
        if re.match(r'^\d+-\d+$', batch_id):
            completed.add(batch_id)

    return completed
```

#### 3. Calculate Next Batch

```python
def get_next_batch_range(
    self,
    completed_batches: Set[str]
) -> Optional[Tuple[int, int]]:
    """
    Calculate next unprocessed batch range (1-based indexing).

    Returns:
        Tuple of (start, end) or None if all completed
    """
    total = self.get_total_items()
    completed_ranges = set()

    # Parse completed batch IDs
    for batch_id in completed_batches:
        start, end = map(int, batch_id.split('-'))
        completed_ranges.add((start, end))

    # Find first gap in completed ranges
    current = 1
    while current <= total:
        end = min(current + self.batch_size - 1, total)
        if (current, end) not in completed_ranges:
            return (current, end)
        current = end + 1

    return None
```

#### 4. Load Batch Data

```python
def load_items(self, start: int, end: int) -> List[str]:
    """
    Load items from input file for given range (1-based indexing).

    Args:
        start: Starting line number (1-based, inclusive)
        end: Ending line number (1-based, inclusive)

    Returns:
        List of items
    """
    items = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            if start <= i <= end:
                items.append(line.strip())
            elif i > end:
                break
    return items
```

#### 5. Build Prompt

```python
def build_prompt(self, items: List[str]) -> str:
    """
    Build prompt by injecting items into template.

    Args:
        items: List of items to process

    Returns:
        Complete prompt string
    """
    items_text = '\n'.join(items)
    return self.prompt_template.replace('[ITEMS_LIST]', items_text)
```

#### 6. Process Single Batch

```python
def process_batch(self, start: int, end: int) -> Dict:
    """
    Process a single batch of items.

    Args:
        start: Starting index (1-based)
        end: Ending index (1-based)

    Returns:
        The processed response

    Raises:
        Exception: If processing fails
    """
    print(f'Processing batch {start}-{end}...')

    # Load data
    items = self.load_items(start, end)
    print(f'  Loaded {len(items)} items')

    # Build request
    prompt = self.build_prompt(items)
    print(f'  Built prompt ({len(prompt)} chars)')

    # Send to API
    print(f'  Sending to API (mode={self.mode}, model={self.model})...')
    response = self.client.call(prompt, mode=self.mode, model=self.model)

    # Validate response
    items_count = len(response.get('items', []))
    print(f'  Received {items_count} items')

    # Save to file
    output_path = self.get_output_path(start, end)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response)
    print(f'  Saved to {output_path}')

    return response
```

#### 7. State Persistence

```python
def save_state(
    self,
    processed_batches: List[str],
    current_batch: Optional[str] = None
):
    """Save current processing state to file."""
    state = {
        'total_items': self.get_total_items(),
        'batch_size': self.batch_size,
        'processed_batches': sorted(processed_batches),
        'current_batch': current_batch,
        'last_updated': datetime.now().isoformat(),
    }

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def load_state(self) -> Optional[Dict]:
    """Load previous processing state from file."""
    if not Path(STATE_FILE).exists():
        return None

    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
```

#### 8. Main Processing Loop

```python
def process_all(
    self,
    max_batches: Optional[int] = None,
    on_progress: Optional[Callable] = None,
) -> Dict:
    """
    Process all uncompleted batches.

    Args:
        max_batches: Maximum number of batches to process (None = unlimited)
        on_progress: Callback(batch_start, batch_end, processed, total)

    Returns:
        Summary dict with processing stats
    """
    total_items = self.get_total_items()
    total_batches = (total_items + self.batch_size - 1) // self.batch_size

    print(f'Total items: {total_items}')
    print(f'Total batches: {total_batches}')

    # Get completed batches
    completed_batches = self.get_completed_batches()
    print(f'Already completed: {len(completed_batches)} batches')

    processed_count = 0
    failed_batches = []
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 10
    RETRY_DELAY = 10  # seconds

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
                # Process batch
                self.process_batch(start, end)
                completed_batches.add(batch_id)
                processed_count += 1
                consecutive_failures = 0  # Reset on success

                # Save state
                self.save_state(sorted(completed_batches), batch_id)

                # Progress callback
                if on_progress:
                    on_progress(start, end, processed_count, total_batches)

                # Delay before next batch
                if max_batches is None or processed_count < max_batches:
                    print(f'  Waiting {self.delay_seconds}s...')
                    time.sleep(self.delay_seconds)

            except Exception as e:
                print(f'  ERROR: {e}')
                failed_batches.append(batch_id)
                consecutive_failures += 1

                # Stop if too many consecutive failures
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    print(f'  Stopping: {consecutive_failures} consecutive failures')
                    break

                # Retry delay
                print(f'  Waiting {RETRY_DELAY}s before retry...')
                time.sleep(RETRY_DELAY)

    except KeyboardInterrupt:
        print('\nInterrupted. Saving state...')

    # Final state save
    self.save_state(sorted(completed_batches))

    return {
        'total_items': total_items,
        'total_batches': total_batches,
        'completed_batches': len(completed_batches),
        'processed_this_run': processed_count,
        'failed_batches': failed_batches,
        'consecutive_failures': consecutive_failures,
    }
```

## CLI Entry Point

```python
def progress_callback(start: int, end: int, processed: int, total: int):
    """Callback for progress updates."""
    pct = (processed / total * 100) if total > 0 else 0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] Progress: {processed}/{total} ({pct:.1f}%) - Current: {start}-{end}')


def main():
    parser = argparse.ArgumentParser(
        description='Process items in batches through API'
    )
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE)
    parser.add_argument('--delay', type=float, default=BATCH_DELAY_SECONDS)
    parser.add_argument('--max-batches', type=int, default=None)
    parser.add_argument('--no-progress', action='store_true')

    args = parser.parse_args()

    processor = BatchProcessor(
        auth=API_COOKIES,
        batch_size=args.batch_size,
        delay_seconds=args.delay,
    )

    callback = None if args.no_progress else progress_callback
    result = processor.process_all(
        max_batches=args.max_batches,
        on_progress=callback
    )

    # Print summary
    print()
    print('Summary:')
    print(f'  Total items: {result["total_items"]}')
    print(f'  Completed: {result["completed_batches"]}/{result["total_batches"]}')
    print(f'  Processed this run: {result["processed_this_run"]}')
    if result['failed_batches']:
        print(f'  Failed: {", ".join(result["failed_batches"])}')
```

## File Naming Convention

Batch files use **1-based indexing** with range notation:

```
1-50.json       # Items 1-50
51-100.json     # Items 51-100
101-150.json    # Items 101-150
```

Helper method:
```python
def get_output_path(self, start: int, end: int) -> Path:
    """Generate output file path for batch."""
    return Path(OUTPUT_DIR) / f'{start}-{end}.json'
```

## State File Format

```json
{
  "total_items": 456506,
  "batch_size": 50,
  "processed_batches": ["1-50", "51-100"],
  "current_batch": "101-150",
  "last_updated": "2026-04-18T18:45:30.123456"
}
```

## Adapting to Other APIs

### 1. Replace API Client

```python
# Original
from services.perplexity_client import PerplexityService
self.client = PerplexityService(cookies)

# Adapted for OpenAI
from openai import OpenAI
self.client = OpenAI(api_key=auth)

# Adapted for Anthropic
from anthropic import Anthropic
self.client = Anthropic(api_key=auth)
```

### 2. Modify Process Batch

```python
# Original (Perplexity)
response = self.client.ask_advanced(prompt, mode=self.mode, model=self.model)

# Adapted (OpenAI)
response = self.client.chat.completions.create(
    model=self.model or "gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

# Adapted (Anthropic)
response = self.client.messages.create(
    model=self.model or "claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
)
```

### 3. Adjust Response Handling

```python
# Original
f.write(response)  # Raw text

# For JSON responses
import json
json.dump(response, f, indent=2, ensure_ascii=False)

# For specific field
f.write(response.content)
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **1-based indexing** | More intuitive for batch file names (1-50 vs 0-49) |
| **Range notation** | Easy to see what each file contains |
| **State file** | Enables resumability after crashes/interruptions |
| **Consecutive failure limit** | Prevents infinite retry loops on persistent errors |
| **Retry delay** | Gives API time to recover from rate limits |
| **Progress callback** | Allows custom monitoring without modifying core logic |
| **JSON state** | Human-readable, easy to debug |

## Common Customizations

### Different Output Formats

```python
# Save as JSON
with open(output_path, 'w') as f:
    json.dump(response, f, indent=2)

# Save as plain text
with open(output_path, 'w') as f:
    f.write(response)

# Save as CSV
import csv
with open(output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(response)
```

### Different Batch Selection

```python
# Sequential (current)
current = 1
while current <= total:
    end = min(current + batch_size - 1, total)
    # process current-end
    current = end + 1

# Random sampling
import random
batches = random.sample(all_batches, k=num_batches)

# Priority-based
batches = sorted(all_batches, key=priority_score)
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_all(self, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for batch_range in self.get_all_batches():
            future = executor.submit(self.process_batch, *batch_range)
            futures.append(future)

        for future in futures:
            result = future.result()
```

## Usage Examples

```bash
# Test with small batch
python run_batch_processor.py --batch-size 5 --max-batches 1

# Process with default settings
python run_batch_processor.py

# Custom batch size and delay
python run_batch_processor.py --batch-size 100 --delay 10

# Resume from state (automatic)
python run_batch_processor.py  # Detects completed batches
```

## Error Recovery Scenarios

| Scenario | Behavior |
|----------|----------|
| **Network timeout** | Retry after 10s delay |
| **Invalid API response** | Log error, retry next batch |
| **10 consecutive failures** | Stop processing, save state |
| **Keyboard interrupt** | Save state, exit cleanly |
| **Partial batch file** | Detected as incomplete, reprocessed |
| **Process crash** | State file enables resume |

## Performance Considerations

- **Batch size**: Larger = fewer API calls, more memory usage
- **Delay**: Prevents rate limiting but slows total time
- **State file I/O**: Minimal overhead, write after each batch
- **File scanning**: O(n) where n = output file count
- **Memory**: One batch loaded at a time

## Testing Checklist

- [ ] Process single batch successfully
- [ ] Resume after interruption
- [ ] Handle API errors gracefully
- [ ] Verify output file format
- [ ] Test with different batch sizes
- [ ] Confirm consecutive failure limit works
- [ ] Validate state file accuracy
- [ ] Test CLI arguments
