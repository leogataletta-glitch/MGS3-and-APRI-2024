import sys, pickle
sys.path.insert(0, '/home/claude/project')
from compute_banner_data import ALL_THEMES_FULL, base_n, SECTION_FILTER

out_path = sys.argv[1]

# Keep only what's needed: category, question, note, multi, and rows (label -> per-group n)
slim = []
for t in ALL_THEMES_FULL:
    slim.append({
        'category': t['category'],
        'question': t['question'],
        'note': t.get('note', ''),
        'rows': t['rows'],  # list of (label, {group_name: n})
    })

with open(out_path, 'wb') as f:
    pickle.dump({'base_n': base_n, 'themes': slim, 'section_filter': SECTION_FILTER}, f)

print("dumped", out_path, "themes:", len(slim), "section_filter:", repr(SECTION_FILTER))
