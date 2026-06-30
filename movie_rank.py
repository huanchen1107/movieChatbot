import sys
import io
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from pathlib import Path
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
import numpy as np
from db import load_movies, load_all_categories

movies = load_movies()
all_categories = load_all_categories()

names = [m["name"] for m in movies]
ids = [m["id"] for m in movies]
scores = [m["score"] for m in movies]
categories_list = [m["categories"] for m in movies]

mlb = MultiLabelBinarizer()
cat_matrix = mlb.fit_transform(categories_list)

print("=" * 60)
print("  Movie Ranking by Category (scikit-learn)")
print("=" * 60)
print(f"  Movies: {len(rows)}")
print(f"  Unique categories: {len(all_categories)}")
print(f"  Categories: {', '.join(all_categories)}")
print()

print("--- Top categories by movie count ---")
counts = cat_matrix.sum(axis=0)
top_idx = np.argsort(counts)[::-1]
for i in top_idx[:10]:
    print(f"  {all_categories[i]:<6} : {int(counts[i])} movies")

print()


def jaccard(set_a, set_b):
    if not set_a or not set_b:
        return 0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0


def rank_by_category(query_categories):
    query_set = set(query_categories)
    valid = query_set & set(all_categories)
    if not valid:
        print(f"  [!] No matching categories: {query_categories}")
        return
    scored = []
    for i in range(len(rows)):
        movie_set = set(categories_list[i])
        overlap = len(query_set & movie_set)
        if overlap > 0:
            jac = jaccard(query_set, movie_set)
            scored.append((overlap, jac, scores[i], i))
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    print(f"  Query: {', '.join(query_categories)}")
    print(f"  {'Rank':<5} {'ID':<5} {'Score':<7} {'Matches':<8} {'Jaccard':<8} Name")
    print(f"  {'-'*60}")
    for rank, (overlap, jac, score, idx) in enumerate(scored[:10], 1):
        matched_cats = query_set & set(categories_list[idx])
        print(f"  {rank:<5} {ids[idx]:<5} {score:<7.1f} {overlap:<8} {jac:<8.3f} {names[idx]}")
    print()


kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
clusters = kmeans.fit_predict(cat_matrix)

print("--- K-Means Clustering (k=6) ---")
for cluster_id in range(6):
    members = [(i, scores[i], names[i]) for i in range(len(rows)) if clusters[i] == cluster_id]
    members.sort(key=lambda x: x[1], reverse=True)
    top_cats_idx = np.argsort(kmeans.cluster_centers_[cluster_id])[::-1][:3]
    top_cats = [all_categories[i] for i in top_cats_idx]
    avg_score = np.mean([m[1] for m in members])
    print(f"\n  Cluster {cluster_id + 1}: [{', '.join(top_cats)}] ({len(members)} movies, avg score: {avg_score:.2f})")
    for _, score, name in members[:5]:
        print(f"    {score} - {name}")
    if len(members) > 5:
        print(f"    ... and {len(members) - 5} more")

print()

rank_by_category(["剧情"])
rank_by_category(["动作", "科幻"])
rank_by_category(["喜剧", "爱情"])
rank_by_category(["动画", "奇幻", "冒险"])
rank_by_category(["犯罪", "悬疑", "惊悚"])
