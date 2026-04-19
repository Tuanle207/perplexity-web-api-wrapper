"""
Split the words.txt file into multiple batch files.
"""
import argparse
from pathlib import Path


def split_words_file(
    input_file: str,
    output_dir: str,
    batch_size: int = 50,
    start_index: int = 1,
    max_batches: int = None,
):
    """
    Split a large words file into multiple batch files.

    Args:
        input_file: Path to input words file (1 word per line)
        output_dir: Directory to save batch files
        batch_size: Number of words per batch
        start_index: Starting index for batch numbering (1-based)
        max_batches: Maximum number of batches to create (None for unlimited)
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f'Input file not found: {input_file}')

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    total_words = 0
    batch_count = 0
    current_batch = []
    current_word_index = start_index

    print(f'Splitting {input_file} into batches of {batch_size}...')
    print(f'Output directory: {output_dir}')

    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if not word:
                continue

            current_batch.append(word)
            total_words += 1

            # When batch is full, write to file
            if len(current_batch) >= batch_size:
                batch_count += 1
                end_index = current_word_index + len(current_batch) - 1

                # Create batch filename: words_1-50.txt, words_51-100.txt, etc.
                batch_filename = f'words_{current_word_index}-{end_index}.txt'
                batch_filepath = output_path / batch_filename

                with open(batch_filepath, 'w', encoding='utf-8') as batch_file:
                    batch_file.write('\n'.join(current_batch))

                print(f'  Created batch {batch_count}: {batch_filename} ({len(current_batch)} words)')

                current_word_index = end_index + 1
                current_batch = []

                # Check max batches limit
                if max_batches is not None and batch_count >= max_batches:
                    print(f'Reached max batches limit: {max_batches}')
                    break

        # Handle remaining words in last partial batch
        if current_batch:
            batch_count += 1
            end_index = current_word_index + len(current_batch) - 1
            batch_filename = f'words_{current_word_index}-{end_index}.txt'
            batch_filepath = output_path / batch_filename

            with open(batch_filepath, 'w', encoding='utf-8') as batch_file:
                batch_file.write('\n'.join(current_batch))

            print(f'  Created batch {batch_count}: {batch_filename} ({len(current_batch)} words) [partial]')

    print(f'\nSummary:')
    print(f'  Total words processed: {total_words}')
    print(f'  Total batches created: {batch_count}')
    print(f'  Output directory: {output_path}')


def main():
    parser = argparse.ArgumentParser(
        description='Split words.txt file into multiple batch files'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='raw/words.txt',
        help='Input words file path (default: raw/words.txt)',
    )
    parser.add_argument(
        '--output',
        type=str,
        default='raw/batches',
        help='Output directory for batch files (default: raw/batches)',
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Number of words per batch (default: 50)',
    )
    parser.add_argument(
        '--start-index',
        type=int,
        default=1,
        help='Starting index for batch numbering (default: 1)',
    )
    parser.add_argument(
        '--max-batches',
        type=int,
        default=None,
        help='Maximum number of batches to create (default: unlimited)',
    )

    args = parser.parse_args()

    try:
        split_words_file(
            input_file=args.input,
            output_dir=args.output,
            batch_size=args.batch_size,
            start_index=args.start_index,
            max_batches=args.max_batches,
        )
    except Exception as e:
        print(f'Error: {e}')
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
