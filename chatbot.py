import sys
import io
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import re
from pathlib import Path
from db import load_movies, load_all_categories, search_movies

movies = load_movies()
all_categories = load_all_categories()

def search_by_name(keyword):
    kw = keyword.lower()
    results = [m for m in movies if kw in m["name"].lower()]
    return sorted(results, key=lambda x: x["score"], reverse=True)

def search_by_category(categories):
    cats = [c.strip() for c in categories if c.strip()]
    results = []
    for m in movies:
        if any(c in m["categories"] for c in cats):
            results.append(m)
    return sorted(results, key=lambda x: x["score"], reverse=True)

def search_by_country(keyword):
    results = []
    kw = keyword.lower()
    for m in movies:
        if kw in m["country"].lower():
            results.append(m)
    return sorted(results, key=lambda x: x["score"], reverse=True)

def rank_top(n=10):
    return sorted(movies, key=lambda x: x["score"], reverse=True)[:n]

def jaccard(set_a, set_b):
    if not set_a or not set_b:
        return 0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0

def rank_by_categories(categories):
    if not categories:
        return rank_top(10)
    query_set = set(c.strip() for c in categories if c.strip())
    if not query_set:
        return rank_top(10)
    scored = []
    for m in movies:
        movie_set = set(m["categories"])
        overlap = len(query_set & movie_set)
        if overlap > 0:
            jac = jaccard(query_set, movie_set)
            scored.append((overlap, jac, m["score"], m))
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return [item[3] for item in scored[:10]]

def similar_movies(movie_id_or_name):
    target = None
    for m in movies:
        if m["id"] == movie_id_or_name or movie_id_or_name.lower() in m["name"].lower():
            target = m
            break
    if not target:
        return []
    target_set = set(target["categories"])
    scored = []
    for m in movies:
        if m is target:
            continue
        jac = jaccard(target_set, set(m["categories"]))
        if jac > 0:
            scored.append((jac, m["score"], m))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [item[2] for item in scored[:10]]

def stats():
    cat_counts = {}
    country_counts = {}
    total_score = 0
    for m in movies:
        for c in m["categories"]:
            cat_counts[c] = cat_counts.get(c, 0) + 1
        for c in m["country"].split("、"):
            c = c.strip()
            if c:
                country_counts[c] = country_counts.get(c, 0) + 1
        total_score += m["score"]

    avg_score = total_score / len(movies)
    top_cat = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_country = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\n  Total movies: {len(movies)}")
    print(f"  Average score: {avg_score:.2f}")
    print(f"  Top categories: {', '.join(f'{k}({v})' for k, v in top_cat)}")
    print(f"  Top countries:  {', '.join(f'{k}({v})' for k, v in top_country)}")

def show_movie(m):
    cats = " / ".join(m["categories"])
    print(f"\n  [{m['id']}] {m['name']}")
    print(f"  Score: {m['score']}  |  {cats}")
    print(f"  {m['country']}  |  {m['duration']}  |  {m['release_date']}")

def show_list(results, limit=10, label="Results"):
    if not results:
        print(f"\n  No movies found.")
        return
    print(f"\n  {label} ({min(len(results), limit)} of {len(results)}):")
    print(f"  {'Rank':<5} {'ID':<5} {'Score':<7} Name")
    print(f"  {'-'*55}")
    for i, m in enumerate(results[:limit], 1):
        cats = " / ".join(m["categories"])
        print(f"  {i:<5} {m['id']:<5} {m['score']:<7.1f} {m['name'][:45]}")
        print(f"         {cats}")

def handle_command(cmd):
    cmd = cmd.strip()
    if not cmd:
        return True

    lower = cmd.lower()

    if lower in ["help", "?", "/help", "h"]:
        print("""
  Commands:
    top [N]              - Rank top N movies by score
    search <keyword>     - Search movies by name
    category <cats>      - Search by categories (comma separated)
    country <keyword>    - Search by country
    rank <cats>          - Rank by category preference (sklearn similarity)
    like <id or name>    - Find similar movies (sklearn)
    info <id or name>    - Show movie details
    stats                - Show database statistics
    cats                 - List all categories
    help                 - Show this help
    quit / exit          - Exit
  Examples:
    top 5
    search 肖申克
    category 剧情, 科幻
    country 美国
    rank 动画, 冒险
    like 霸王别姬
    info 3
""")
        return True

    if lower in ["quit", "exit", "q", "bye"]:
        print("\n  Goodbye!")
        return False

    if lower == "cats":
        print(f"\n  Categories ({len(all_categories)}):")
        for c in all_categories:
            print(f"    {c}")
        return True

    if lower == "stats":
        stats()
        return True

    m = re.match(r"^top\s*(\d+)?$", lower)
    if m:
        n = int(m.group(1)) if m.group(1) else 10
        results = rank_top(n)
        show_list(results, n, f"Top {n}")
        return True

    m = re.match(r"^search\s+(.+)$", lower)
    if m:
        results = search_by_name(m.group(1).strip())
        show_list(results, 10, "Search")
        return True

    m = re.match(r"^category\s+(.+)$", lower)
    if m:
        cats = m.group(1).split(",")
        results = search_by_category(cats)
        show_list(results, 10, "By Category")
        return True

    m = re.match(r"^country\s+(.+)$", lower)
    if m:
        results = search_by_country(m.group(1).strip())
        show_list(results, 10, "By Country")
        return True

    m = re.match(r"^rank\s+(.+)$", lower)
    if m:
        cats = m.group(1).split(",")
        results = rank_by_categories(cats)
        show_list(results, 10, "Ranked (sklearn)")
        return True

    m = re.match(r"^like\s+(.+)$", lower)
    if m:
        results = similar_movies(m.group(1).strip())
        show_list(results, 10, f"Similar to '{m.group(1).strip()}'")
        return True

    m = re.match(r"^info\s+(.+)$", lower)
    if m:
        query = m.group(1).strip()
        found = None
        for mv in movies:
            if mv["id"] == query or query.lower() in mv["name"].lower():
                found = mv
                break
        if found:
            show_movie(found)
            similar = similar_movies(query)
            if similar:
                print(f"\n  Similar movies:")
                for sm in similar[:5]:
                    print(f"    [{sm['id']}] {sm['name']} (score: {sm['score']})")
        else:
            print(f"\n  Movie not found: {query}")
        return True

    keywords = cmd.split()
    cats_found = [c for c in all_categories if any(c in kw for kw in keywords)]
    if cats_found:
        results = search_by_category(cats_found)
        show_list(results, 10, f"Matched: {', '.join(cats_found)}")
        return True

    results = search_by_name(cmd)
    if results:
        show_list(results, 10, "Search")
        return True

    print(f"\n  Unknown command. Type 'help' for available commands.")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("  Movie Chatbot (scikit-learn powered)")
    print(f"  {len(movies)} movies  |  {len(all_categories)} categories")
    print("  Type 'help' to get started, 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            cmd = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break
        if not handle_command(cmd):
            break
