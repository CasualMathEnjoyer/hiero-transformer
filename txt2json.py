#!/usr/bin/env python3
"""
Convert paired text files back to JSON format.

This script converts paired source/target text files (created by clean_convert2txt.py)
back into JSON format compatible with the hiero-transformer data structure.
Missing fields are filled with empty strings.
"""

import json
import argparse
import sys
from pathlib import Path


FIELD_MAPPING = {
    "egy": "source",
    "tnt": "transliteration",
    "en": "target",
    "de": "target",
    "lkey": "lKey",
    "worldClass": "wordClass"
}


def unformat_egy(text):
    """Reverse format for Egyptian hieroglyph codes - already space-separated."""
    return text.strip()


def unformat_tnt(text):
    """Reverse format for transliteration: remove spaces between chars, replace underscores with spaces."""
    text = text.strip().replace(" ", "")
    text = text.replace("_", " ")
    return text.strip()


def unformat_text(text, lang_type):
    """Reverse format text based on language type."""
    if lang_type == "egy":
        return unformat_egy(text)
    elif lang_type == "tnt":
        return unformat_tnt(text)
    else:
        return text.strip()


def convert_txt_to_json(source_path, target_path, source_type, target_type, output_path):
    """
    Convert paired text files to JSON format.
    
    Args:
        source_path: Path to source text file
        target_path: Path to target text file
        source_type: Type of source data (egy, tnt, etc.)
        target_type: Type of target data (tnt, en, de, etc.)
        output_path: Path to output JSON file
    
    Returns:
        Path to created JSON file
    """
    source_path = Path(source_path)
    target_path = Path(target_path)
    output_path = Path(output_path)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    if not target_path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")
    
    source_field = FIELD_MAPPING.get(source_type)
    target_field = FIELD_MAPPING.get(target_type)
    
    if not source_field:
        raise ValueError(f"Unknown source type: {source_type}. Valid options: {list(FIELD_MAPPING.keys())}")
    if not target_field:
        raise ValueError(f"Unknown target type: {target_type}. Valid options: {list(FIELD_MAPPING.keys())}")
    
    with open(source_path, 'r', encoding='utf-8') as f:
        source_lines = [line.rstrip('\n') for line in f]
    
    with open(target_path, 'r', encoding='utf-8') as f:
        target_lines = [line.rstrip('\n') for line in f]
    
    if len(source_lines) != len(target_lines):
        raise ValueError(f"Mismatch in number of lines: source has {len(source_lines)}, target has {len(target_lines)}")
    
    data = []
    for source_line, target_line in zip(source_lines, target_lines):
        source_unformatted = unformat_text(source_line, source_type)
        target_unformatted = unformat_text(target_line, target_type)
        
        entry = {
            "source": "",
            "transliteration": "",
            "target": "",
            "lKey": "",
            "wordClass": "",
            "flexCode": "",
            "metadata": {
                "source_lang": "",
                "target_lang": "",
                "id_datapoint": "",
                "id_sentence": "",
                "language": "",
                "date": "",
                "script": "",
                "id_tree": ""
            }
        }
        
        entry[source_field] = source_unformatted
        entry[target_field] = target_unformatted
        
        data.append(entry)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert paired text files to JSON format"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to source text file"
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Path to target text file"
    )
    parser.add_argument(
        "--types",
        type=str,
        required=True,
        help="Comma-separated source and target types (e.g., 'egy,tnt')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output JSON file (default: same directory as source file with .json extension)"
    )
    
    args = parser.parse_args()
    
    types = [t.strip() for t in args.types.split(',')]
    if len(types) != 2:
        raise ValueError("--types must contain exactly two comma-separated values (e.g., 'egy,tnt')")
    
    source_type, target_type = types
    
    if args.output is None:
        source_path = Path(args.source)
        output_path = source_path.parent / f"{source_path.stem}_to_{Path(args.target).stem}.json"
    else:
        output_path = Path(args.output)
    
    try:
        result_path = convert_txt_to_json(
            args.source,
            args.target,
            source_type,
            target_type,
            output_path
        )
        
        print(f"Conversion completed successfully!")
        print(f"Output file: {result_path}")
        print(f"Total entries: {len(json.load(open(result_path, 'r', encoding='utf-8')))}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()




