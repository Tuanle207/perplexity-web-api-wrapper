"""
Main entry point for running the words batch processor.
"""
import argparse
import sys
import time
from datetime import datetime, timedelta

from config import (
    BATCH_DELAY_SECONDS,
    BATCH_MODEL,
    BATCH_MODE,
    BATCH_SIZE,
    PROCESS_START_INDEX,
    PROCESS_END_INDEX,
    PERPLEXITY_COOKIES,
)
from services.words_batch_processor import WordsBatchProcessor


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f'{seconds:.1f}s'
    elif seconds < 3600:
        minutes = seconds / 60
        return f'{minutes:.1f}m'
    else:
        hours = seconds / 3600
        return f'{hours:.1f}h'


def progress_callback(start: int, end: int, processed: int, total: int, eta_seconds: int = 0):
    """Callback for progress updates."""
    pct = (processed / total * 100) if total > 0 else 0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Format ETA
    if eta_seconds > 0:
        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        seconds = eta_seconds % 60
        if hours > 0:
            eta_str = f'{hours}h {minutes}m'
        elif minutes > 0:
            eta_str = f'{minutes}m {seconds}s'
        else:
            eta_str = f'{seconds}s'
    else:
        eta_str = 'N/A'

    print(f'[{timestamp}] Progress: {processed}/{total} batches ({pct:.1f}%) - Current: {start}-{end} - ETA: {eta_str}')


def main():
    parser = argparse.ArgumentParser(
        description='Process words in batches through Perplexity AI'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=BATCH_SIZE,
        help=f'Number of words per batch (default: {BATCH_SIZE})',
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=BATCH_DELAY_SECONDS,
        help=f'Delay between batches in seconds (default: {BATCH_DELAY_SECONDS})',
    )
    parser.add_argument(
        '--mode',
        type=str,
        default=BATCH_MODE,
        choices=['auto', 'pro', 'reasoning', 'deep research'],
        help=f'Perplexity search mode (default: {BATCH_MODE})',
    )
    parser.add_argument(
        '--model',
        type=str,
        default=BATCH_MODEL,
        help=f'Model to use (default: {BATCH_MODEL})',
    )
    parser.add_argument(
        '--max-batches',
        type=int,
        default=None,
        help='Maximum number of batches to process (default: unlimited)',
    )
    parser.add_argument(
        '--start-index',
        type=int,
        default=PROCESS_START_INDEX,
        help=f'Start processing from this word index (1-based, default: {PROCESS_START_INDEX})',
    )
    parser.add_argument(
        '--end-index',
        type=int,
        default=PROCESS_END_INDEX,
        help=f'End processing at this word index (1-based, default: {PROCESS_END_INDEX})',
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress callback',
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Number of concurrent workers (default: 1, use >1 for concurrent processing)',
    )

    args = parser.parse_args()

    print('=' * 60)
    print('Words Batch Processor')
    print('=' * 60)
    print(f'Batch size: {args.batch_size}')
    print(f'Delay: {args.delay}s')
    print(f'Mode: {args.mode}')
    print(f'Model: {args.model}')
    print(f'Workers: {args.workers}')
    if args.start_index:
        print(f'Start index: {args.start_index}')
    if args.end_index:
        print(f'End index: {args.end_index}')
    if args.max_batches:
        print(f'Max batches: {args.max_batches}')
    print('=' * 60)

    # Create processor
    processor = WordsBatchProcessor(
        cookies=PERPLEXITY_COOKIES,
        batch_size=args.batch_size,
        delay_seconds=args.delay,
        mode=args.mode,
        model=args.model,
        process_start_index=args.start_index,
        process_end_index=args.end_index,
        max_workers=args.workers,
    )

    # Run processing
    callback = None if args.no_progress else progress_callback
    start_time = time.time()
    result = processor.process_all(max_batches=args.max_batches, on_progress=callback)
    elapsed_time = time.time() - start_time

    # Print summary
    print()
    print('=' * 60)
    print('Processing Summary')
    print('=' * 60)
    print(f'Total words: {result["total_words"]}')
    print(f'Total batches in range: {result["total_batches"]}')
    print(f'Completed batches: {result["completed_batches"]}')
    print(f'Processed this run: {result["processed_this_run"]}')
    print(f'Elapsed time: {format_duration(elapsed_time)}')
    if result['processed_this_run'] > 0:
        avg_time_per_batch = elapsed_time / result['processed_this_run']
        print(f'Avg time per batch: {format_duration(avg_time_per_batch)}')
    if result['failed_batches']:
        print(f'Failed batches: {", ".join(result["failed_batches"])}')
    print('=' * 60)


if __name__ == '__main__':
    main()
