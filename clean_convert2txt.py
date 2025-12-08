#!/usr/bin/env python3
"""
Convert hiero-transformer data from TLA into a format compatible with Ramses-trl.

This script converts JSON data files from the hiero-transformer repository (TLA format)
into paired source/target text files compatible with Ramses-trl training format.
The script applies cleaning operations to the data before conversion.
Entries missing either source or target are skipped to maintain alignment.

Ramses-trl: https://github.com/ramses-project/ramses-trl

Example usage:
    # Convert Egyptian hieroglyphs to transliteration (default)
    python clean_convert2txt.py training_and_validation/test_data.json
    
    # Convert Egyptian hieroglyphs to German translation
    python clean_convert2txt.py training_and_validation/test_data.json --source egy --target de
    
    # Convert transliteration to English translation
    python clean_convert2txt.py training_and_validation/test_data.json --source tnt --target en
"""

import json
import argparse
import sys
from pathlib import Path

from utils import clean_graphics, clean_wChar, clean_traduction


FIELD_MAPPING = {
    "egy": "source",
    "tnt": "transliteration",
    "en": "target",
    "de": "target",
    "lkey": "lKey",
    "worldClass": "wordClass"
}

LANG_FILTER_MAPPING = {
    "en": "en",
    "de": "de"
}

CLEAN_FUNCTION_MAPPING = {
    "egy": clean_graphics,
    "tnt": clean_wChar,
    "en": clean_traduction,
    "de": clean_traduction
}


def format_egy(text):
    """Format Egyptian hieroglyph codes - already space-separated."""
    return text.strip()


def format_tnt(text):
    """Format transliteration: replace word spaces with underscores, then add spaces between all characters."""
    text = text.strip().replace(" ", "_")
    return " ".join(text)


def format_text(text, lang_type):
    """Format text based on language type."""
    if lang_type == "egy":
        return format_egy(text)
    elif lang_type == "tnt":
        return format_tnt(text)
    else:
        return text.strip()


def clean_text(text, lang_type):
    """Apply appropriate cleaning function based on language type."""
    clean_func = CLEAN_FUNCTION_MAPPING.get(lang_type)
    if clean_func:
        return clean_func(text)
    return text


def convert_json_to_txt(json_path, source="egy", target="tnt"):
    """
    Convert JSON data to paired text files with cleaning operations applied.
    
    Args:
        json_path: Path to input JSON file
        source: Source language type (default: egy)
        target: Target language type (default: tnt)
    
    Returns:
        tuple: (source_file_path, target_file_path, stats_dict)
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    source_field = FIELD_MAPPING.get(source)
    target_field = FIELD_MAPPING.get(target)
    
    if not source_field:
        raise ValueError(f"Unknown source type: {source}. Valid options: {list(FIELD_MAPPING.keys())}")
    if not target_field:
        raise ValueError(f"Unknown target type: {target}. Valid options: {list(FIELD_MAPPING.keys())}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    source_lines = []
    target_lines = []
    skipped = 0
    
    for entry in data:
        source_text = entry.get(source_field)
        target_text = entry.get(target_field)
        
        if source_text is None or target_text is None:
            skipped += 1
            continue
        
        if source_text == "" or target_text == "":
            skipped += 1
            continue
        
        if target in LANG_FILTER_MAPPING:
            metadata = entry.get("metadata", {})
            target_lang = metadata.get("target_lang")
            if target_lang != LANG_FILTER_MAPPING[target]:
                skipped += 1
                continue
        
        source_cleaned = clean_text(source_text, source)
        target_cleaned = clean_text(target_text, target)
        
        if source_cleaned == "" or target_cleaned == "":
            skipped += 1
            continue
        
        source_formatted = format_text(source_cleaned, source)
        target_formatted = format_text(target_cleaned, target)
        
        if source_formatted == "" or target_formatted == "":
            skipped += 1
            continue
        
        source_lines.append(source_formatted)
        target_lines.append(target_formatted)
    
    output_dir = json_path.parent
    source_filename = f"source_{source}2{target}_cleaned.txt"
    target_filename = f"target_{source}2{target}_cleaned.txt"
    
    source_path = output_dir / source_filename
    target_path = output_dir / target_filename
    
    with open(source_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(source_lines))
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(target_lines))
    
    stats = {
        "total_entries": len(data),
        "processed_entries": len(source_lines),
        "skipped_entries": skipped
    }
    
    return source_path, target_path, stats


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON translation data to paired text files with cleaning operations"
    )
    parser.add_argument(
        "json_file",
        type=str,
        help="Path to input JSON file (e.g., test_data.json)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="egy",
        choices=["egy", "tnt"],
        help="Source language type (default: egy)"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="tnt",
        choices=["en", "de", "tnt", "lkey", "worldClass"],
        help="Target language type (default: tnt)"
    )
    
    args = parser.parse_args()
    
    try:
        source_path, target_path, stats = convert_json_to_txt(
            args.json_file,
            source=args.source,
            target=args.target
        )
        
        print(f"Conversion completed successfully!")
        print(f"Source file: {source_path}")
        print(f"Target file: {target_path}")
        print(f"\nStatistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Processed entries: {stats['processed_entries']}")
        print(f"  Skipped entries: {stats['skipped_entries']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

