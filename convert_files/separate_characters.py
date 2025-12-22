#!/usr/bin/env python3
import sys
import os

def process_file(input_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    input_dir = os.path.dirname(input_path)
    output_path = os.path.join(input_dir, f"{base_name}_separated_cleaned.txt")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed_lines = []
    for line in lines:
        line = line.rstrip('\n')
        line = line.replace(' ', '_')
        separated = ' '.join(line)
        processed_lines.append(separated)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in processed_lines:
            f.write(line + '\n')
    
    print(f"Processed {len(processed_lines)} lines")
    print(f"Output saved to: {output_path}")
    return output_path

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python separate_characters.py <input_file_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    process_file(input_path)

