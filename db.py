import os
import shutil
import sqlite3
from pathlib import Path

_IS_VERCEL = bool(os.environ.get("VERCEL"))

_SOURCE_DB = Path(__file__).parent / "output" / "movie.db"
_TMP_DB = Path("/tmp") / "movie.db"

if _IS_VERCEL and _SOURCE_DB.exists() and not _TMP_DB.exists():
    shutil.copy2(str(_SOURCE_DB), str(_TMP_DB))

DB_PATH = _TMP_DB if _IS_VERCEL else _SOURCE_DB

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    categories TEXT NOT NULL,
    country TEXT,
    duration TEXT,
    release_date TEXT,
    score REAL,
    cover TEXT,
    poster_file TEXT
);
CREATE INDEX IF NOT EXISTS idx_movies_score ON movies(score DESC);
CREATE INDEX IF NOT EXISTS idx_movies_name ON movies(name);
"""


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def load_movies():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM movies ORDER BY score DESC").fetchall()
    movies = []
    for r in rows:
        movies.append({
            "id": r["id"],
            "name": r["name"],
            "categories": [c.strip() for c in r["categories"].split("/")] if r["categories"] else [],
            "categories_str": r["categories"] or "",
            "country": r["country"] or "",
            "duration": r["duration"] or "",
            "release_date": r["release_date"] or "",
            "score": r["score"] or 0.0,
            "cover": r["cover"] or "",
            "poster_file": r["poster_file"] or "",
        })
    conn.close()
    return movies


def load_all_categories():
    conn = get_conn()
    rows = conn.execute("SELECT categories FROM movies WHERE categories IS NOT NULL AND categories != ''").fetchall()
    cats = set()
    for r in rows:
        for c in r["categories"].split("/"):
            c = c.strip()
            if c:
                cats.add(c)
    conn.close()
    return sorted(cats)


def save_movies(movies):
    conn = get_conn()
    conn.execute("DELETE FROM movies")
    data = []
    for m in movies:
        cats_str = " / ".join(m["categories"]) if isinstance(m["categories"], list) else m.get("categories", "")
        data.append((
            int(m["id"]),
            m["name"],
            cats_str,
            m.get("country", ""),
            m.get("duration", ""),
            m.get("release_date", ""),
            float(m.get("score", 0)),
            m.get("cover", ""),
            m.get("poster_file", ""),
        ))
    conn.executemany(
        "INSERT INTO movies (id, name, categories, country, duration, release_date, score, cover, poster_file) VALUES (?,?,?,?,?,?,?,?,?)",
        data
    )
    conn.commit()
    conn.close()


def search_movies(keyword):
    conn = get_conn()
    kw = f"%{keyword}%"
    rows = conn.execute(
        "SELECT * FROM movies WHERE name LIKE ? OR categories LIKE ? OR country LIKE ? OR duration LIKE ? OR release_date LIKE ? ORDER BY score DESC",
        (kw, kw, kw, kw, kw)
    ).fetchall()
    movies = []
    for r in rows:
        movies.append(dict(r))
        movies[-1]["categories"] = [c.strip() for c in r["categories"].split("/")] if r["categories"] else []
    conn.close()
    return movies


def count_movies():
    conn = get_conn()
    c = conn.execute("SELECT COUNT(*) FROM movies").fetchone()
    conn.close()
    return c[0]


def avg_score():
    conn = get_conn()
    c = conn.execute("SELECT AVG(score) FROM movies").fetchone()
    conn.close()
    return round(c[0], 2) if c[0] else 0.0
