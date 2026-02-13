import os
import argparse
from pathlib import Path

def parse_filename(filename):
    # crop_{file_index}_{region_index}_{type}.md
    parts = filename.stem.split('_')
    if len(parts) >= 4:
        try:
            file_idx = int(parts[1])
            region_idx = int(parts[2])
            region_type = "_".join(parts[3:]) # in case type has underscores
            return file_idx, region_idx, region_type
        except ValueError:
            pass
    return float('inf'), float('inf'), 'unknown'

def main(input_dir, output_file, sort_by_type=True):
    input_path = Path(input_dir)
    md_files = sorted([f for f in input_path.iterdir() if f.suffix.lower() == '.md'])
    
    if not md_files:
        print(f"No markdown files found in {input_dir}")
        return

    # Parse file metadata
    files_metadata = []
    for f in md_files:
        # Pass the Path object 'f' directly, so .stem works inside parse_filename
        # Or parse_filename handles Path input.
        f_idx, r_idx, r_type = parse_filename(f)
        files_metadata.append({
            'path': f,
            'file_idx': f_idx,
            'region_idx': r_idx,
            'type': r_type
        })
    
    if sort_by_type:
        # Sort by File Index -> Type Priority -> Region Index
        # This ensures page-by-page order, but within page, Title > Text > Figure
        def type_priority(t):
            t = t.lower()
            if 'title' in t: return 0
            if 'text' in t: return 1
            if 'figure' in t: return 2
            if 'table' in t: return 2
            return 3 # Other

        files_metadata.sort(key=lambda x: (
            x['file_idx'],              # Primary: Group by source file
            type_priority(x['type']),   # Secondary: Prioritize Title > Text > Figure
            x['region_idx']             # Tertiary: Maintain reading order within same type
        ))
        print("Sorting by File -> Type Priority (Title -> Text -> Figure/Table)")
    else:
        # Sort by Natural Reading Order
        files_metadata.sort(key=lambda x: (x['file_idx'], x['region_idx']))
        print("Sorting by Natural Reading Order")
    
    # Merge content
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Merged Content from {input_dir}\n\n")
        
        for item in files_metadata:
            try:
                with open(item['path'], 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    
                outfile.write(f"<!-- Source: {item['path'].name} ({item['type']}) -->\n")
                outfile.write(content)
                outfile.write("\n\n")
                
            except Exception as e:
                print(f"Error reading {item['path']}: {e}")
                outfile.write(f"<!-- Error reading {item['path'].name} -->\n\n")

    print(f"Merged {len(files_metadata)} files into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge markdown fragments.")
    parser.add_argument("--input_dir", required=True, help="Input directory containing .md files")
    parser.add_argument("--output_file", required=True, help="Output file path")
    parser.add_argument("--natural_order", action="store_true", help="Sort by natural reading order instead of type priority")
    
    args = parser.parse_args()
    
    main(args.input_dir, args.output_file, sort_by_type=not args.natural_order)
