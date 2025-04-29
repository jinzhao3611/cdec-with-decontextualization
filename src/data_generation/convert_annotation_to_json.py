import os
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

def get_valid_relation_types():
    """Return a set of valid relation types."""
    return {
        'coref',  # Coreference
        'subevent',  # Subevent
        'causal',  # Causal
        'temporal',  # Temporal
        'none'  # No relation
    }

def get_relation_mapping():
    """Return a mapping of numeric and string values to standardized relation types."""
    return {
        # Numeric mappings
        '1': 'identity',
        '1.0': 'identity',
        '2': 'concept-instance',
        '2.0': 'concept-instance',
        '3': 'instance-concept',
        '3.0': 'instance-concept',
        '4': 'set-member',
        '4.0': 'set-member',
        '5': 'member-set',
        '5.0': 'member-set',
        '6': 'subevent-whole',
        '6.0': 'subevent-whole',
        '7': 'whole-subevent',
        '7.0': 'whole-subevent',
        '8': 'not-related',
        '8.0': 'not-related',
        '9': 'cannot-decide',
        '9.0': 'cannot-decide',
        # Fix typos
        'concept-iinstance': 'concept-instance',
        'instsance-concept': 'instance-concept',
        'intance-concept': 'instance-concept',
        'membe-set': 'member-set',
        'memeber-set': 'member-set',
        'instance-concpet': 'instance-concept',
        'concept-isntance': 'concept-instance',
        'subevent_whole': 'subevent-whole',
        # Special characters and other values
        '`': 'not-related',
        '·': 'not-related',
        'nan': 'not-related',
        '-1': 'not-related',
        '0': 'not-related',
        '0.0': 'not-related',
        '10': 'not-related',
        '11': 'not-related',
        '11.0': 'not-related',
        '12': 'not-related',
        '13': 'not-related',
        '14': 'not-related'
    }

def clean_relation_type(relation):
    """Clean and standardize a relation type."""
    if pd.isna(relation):
        return 'not-related'
    
    relation = str(relation).lower().strip()
    mapping = get_relation_mapping()
    return mapping.get(relation, 'not-related')

def analyze_relation_types(data):
    """Analyze relation types in the data and report statistics."""
    relation_counts = defaultdict(int)
    invalid_relations = defaultdict(list)
    
    for topic, files in data.items():
        for file_data in files:
            for record in file_data['data']:
                if 'relation' in record:
                    relation = str(record['relation']).lower().strip()
                    relation_counts[relation] += 1
                    
                    if relation not in get_valid_relation_types():
                        invalid_relations[relation].append({
                            'topic': topic,
                            'file': file_data['file_name'],
                            'record': record
                        })
    
    return relation_counts, invalid_relations

def process_excel_file(file_path):
    """Process a single Excel file and return its data as a dictionary."""
    try:
        df = pd.read_excel(file_path)
        # Drop unwanted columns - handle both string and numeric column names
        columns_to_drop = ['comment', 0, '0']
        for col in columns_to_drop:
            if col in df.columns:
                df = df.drop(columns=col)
        
        # Clean relation types if the column exists
        if 'relation' in df.columns:
            df['relation'] = df['relation'].apply(clean_relation_type)
        
        # Convert DataFrame to dictionary
        data = df.to_dict(orient='records')
        return {
            'file_name': os.path.basename(file_path),
            'data': data
        }
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

def process_directory(directory_path):
    """Process all Excel files in a directory and its subdirectories."""
    results = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.xlsx') and not file.startswith('~$'):  # Skip temporary Excel files
                file_path = os.path.join(root, file)
                result = process_excel_file(file_path)
                if result:
                    results.append(result)
    return results

def generate_statistics(data):
    """Generate detailed statistics about the processed annotations."""
    stats = {
        'total_annotations': 0,
        'annotations_by_topic': defaultdict(int),
        'annotations_by_source': defaultdict(int),
        'relation_types_by_topic': defaultdict(lambda: defaultdict(int)),
        'relation_types_by_source': defaultdict(lambda: defaultdict(int))
    }
    
    for topic, files in data.items():
        for file_data in files:
            source = file_data['file_name'].split('_scores')[0]  # Extract source name
            annotations = file_data['data']
            stats['total_annotations'] += len(annotations)
            stats['annotations_by_topic'][topic] += len(annotations)
            stats['annotations_by_source'][source] += len(annotations)
            
            for record in annotations:
                if 'relation' in record:
                    relation = record['relation']
                    stats['relation_types_by_topic'][topic][relation] += 1
                    stats['relation_types_by_source'][source][relation] += 1
    
    return stats

def print_statistics(stats):
    """Print the statistics in a readable format."""
    print("\nDetailed Statistics")
    print("==================")
    print(f"\nTotal number of annotations: {stats['total_annotations']}")
    
    print("\nAnnotations by Topic:")
    print("--------------------")
    for topic, count in sorted(stats['annotations_by_topic'].items()):
        print(f"{topic}: {count} ({count/stats['total_annotations']*100:.2f}%)")
    
    print("\nAnnotations by Source:")
    print("---------------------")
    for source, count in sorted(stats['annotations_by_source'].items()):
        print(f"{source}: {count} ({count/stats['total_annotations']*100:.2f}%)")
    
    print("\nRelation Types by Topic:")
    print("-----------------------")
    for topic in sorted(stats['relation_types_by_topic'].keys()):
        print(f"\n{topic}:")
        total = sum(stats['relation_types_by_topic'][topic].values())
        for relation, count in sorted(stats['relation_types_by_topic'][topic].items()):
            print(f"  {relation}: {count} ({count/total*100:.2f}%)")
    
    print("\nRelation Types by Source:")
    print("------------------------")
    for source in sorted(stats['relation_types_by_source'].keys()):
        print(f"\n{source}:")
        total = sum(stats['relation_types_by_source'][source].values())
        for relation, count in sorted(stats['relation_types_by_source'][source].items()):
            print(f"  {relation}: {count} ({count/total*100:.2f}%)")

def main():
    # Base directory containing the annotation data
    base_dir = 'data/coreference_annotation'
    
    # Topics to process
    topics = ['hong_kong', 'putin', 'rittenhouse', 'shifa']
    
    # Dictionary to store all processed data
    all_data = {}
    
    # Process each topic
    for topic in topics:
        topic_dir = os.path.join(base_dir, topic)
        if os.path.exists(topic_dir):
            print(f"Processing {topic}...")
            topic_data = process_directory(topic_dir)
            all_data[topic] = topic_data
    
    # Generate and print statistics
    stats = generate_statistics(all_data)
    print_statistics(stats)
    
    # Create output directory if it doesn't exist
    output_dir = 'data/processed_annotations'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the combined data to a JSON file
    output_file = os.path.join(output_dir, 'coreference_annotations.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nData has been successfully converted and saved to {output_file}")

if __name__ == "__main__":
    main() 