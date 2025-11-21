"""Validate documentation.json against setup.md requirements."""

import json
from pathlib import Path

def validate_dataset():
    """Validate the documentation dataset."""
    data_path = Path(__file__).parent / "data" / "documentation.json"
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print("DATASET VALIDATION REPORT")
    print("=" * 60)
    
    # Check total entries
    total_entries = len(data)
    print(f"\n1. Total Entries: {total_entries}")
    if 20 <= total_entries <= 50:
        print("   [OK] Within required range (20-50 entries)")
    else:
        print(f"   [ERROR] Outside required range (20-50 entries)")
    
    # Check categories
    categories = {}
    for entry in data:
        cat = entry.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n2. Categories: {len(categories)}")
    if 8 <= len(categories) <= 10:
        print("   [OK] Within required range (8-10 categories)")
    else:
        print(f"   [WARNING] Outside recommended range (8-10 categories)")
    
    print("\n   Category breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"     - {cat}: {count} entries")
    
    # Check required fields
    required_fields = ['id', 'category', 'question', 'answer', 'tags', 'metadata']
    issues = []
    
    for i, entry in enumerate(data):
        entry_id = entry.get('id', f'entry_{i+1}')
        for field in required_fields:
            if field not in entry:
                issues.append(f"Entry {entry_id}: Missing '{field}'")
    
    print(f"\n3. Required Fields Check:")
    if not issues:
        print("   [OK] All entries have all required fields")
    else:
        print(f"   [ERROR] Found {len(issues)} issues:")
        for issue in issues[:10]:
            print(f"     - {issue}")
        if len(issues) > 10:
            print(f"     ... and {len(issues) - 10} more")
    
    # Check metadata structure
    metadata_issues = []
    for i, entry in enumerate(data):
        entry_id = entry.get('id', f'entry_{i+1}')
        metadata = entry.get('metadata', {})
        if 'last_updated' not in metadata:
            metadata_issues.append(f"Entry {entry_id}: Missing 'last_updated' in metadata")
        if 'author' not in metadata:
            metadata_issues.append(f"Entry {entry_id}: Missing 'author' in metadata")
    
    print(f"\n4. Metadata Structure:")
    if not metadata_issues:
        print("   [OK] All entries have complete metadata")
    else:
        print(f"   [ERROR] Found {len(metadata_issues)} metadata issues:")
        for issue in metadata_issues[:5]:
            print(f"     - {issue}")
    
    # Check answer length
    answer_lengths = []
    for entry in data:
        answer = entry.get('answer', '')
        word_count = len(answer.split())
        answer_lengths.append(word_count)
    
    avg_words = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
    min_words = min(answer_lengths) if answer_lengths else 0
    max_words = max(answer_lengths) if answer_lengths else 0
    within_range = sum(1 for w in answer_lengths if 50 <= w <= 200)
    
    print(f"\n5. Answer Length Analysis:")
    print(f"   - Min words: {min_words}")
    print(f"   - Max words: {max_words}")
    print(f"   - Avg words: {avg_words:.1f}")
    print(f"   - Within 50-200 words: {within_range}/{total_entries}")
    if within_range == total_entries:
        print("   [OK] All answers within recommended range (50-200 words)")
    else:
        print(f"   [WARNING] {total_entries - within_range} answers outside recommended range")
    
    # Check tags
    tag_counts = []
    for entry in data:
        tags = entry.get('tags', [])
        tag_counts.append(len(tags))
    
    avg_tags = sum(tag_counts) / len(tag_counts) if tag_counts else 0
    min_tags = min(tag_counts) if tag_counts else 0
    
    print(f"\n6. Tags Analysis:")
    print(f"   - Min tags per entry: {min_tags}")
    print(f"   - Avg tags per entry: {avg_tags:.1f}")
    if min_tags >= 3:
        print("   [OK] All entries have multiple tags (good for retrieval)")
    else:
        print("   [WARNING] Some entries have fewer than 3 tags")
    
    # Check unique IDs
    ids = [entry.get('id') for entry in data]
    unique_ids = set(ids)
    print(f"\n7. ID Uniqueness:")
    if len(ids) == len(unique_ids):
        print("   [OK] All IDs are unique")
    else:
        duplicates = len(ids) - len(unique_ids)
        print(f"   [ERROR] Found {duplicates} duplicate IDs")
    
    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)
    
    all_good = (
        20 <= total_entries <= 50 and
        len(issues) == 0 and
        len(metadata_issues) == 0 and
        len(ids) == len(unique_ids)
    )
    
    if all_good:
        print("[SUCCESS] Dataset is CORRECT and meets all requirements!")
        print("\nYour documentation.json is ready for use in the RAG pipeline.")
    else:
        print("[WARNING] Dataset has some issues that should be addressed.")
        print("\nPlease review the issues above and fix them.")
    
    print("=" * 60)

if __name__ == "__main__":
    validate_dataset()

