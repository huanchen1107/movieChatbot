import csv
import re
import json
import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types as genai_types
from db import load_movies, load_all_categories, count_movies as db_count, avg_score as db_avg_score

BASE = Path(__file__).parent

env_file = BASE / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

movies = load_movies()
all_categories = load_all_categories()


def jaccard(set_a, set_b):
    if not set_a or not set_b:
        return 0
    return len(set_a & set_b) / len(set_a | set_b)


def rank_by_categories(cats, top_n=10):
    query_set = set(cats)
    scored = []
    for m in movies:
        overlap = len(query_set & set(m["categories"]))
        if overlap > 0:
            jac = jaccard(query_set, set(m["categories"]))
            scored.append((overlap, jac, m["score"], m))
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return [item[3] for item in scored[:top_n]]


def similar_movies(query):
    target = None
    for m in movies:
        if query == str(m["id"]) or query.lower() in m["name"].lower():
            target = m
            break
    if not target:
        return None, []
    target_set = set(target["categories"])
    scored = []
    for m in movies:
        if m is target:
            continue
        jac = jaccard(target_set, set(m["categories"]))
        if jac > 0:
            scored.append((jac, m["score"], m))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return target, [item[2] for item in scored[:10]]


def search_movies(keyword):
    kw = keyword.lower()
    results = [m for m in movies if kw in m["name"].lower() or kw in m["country"].lower()
               or any(kw in c.lower() for c in m["categories"])]
    return sorted(results, key=lambda x: x["score"], reverse=True)


def format_movie_html(m):
    cats = " / ".join(m["categories"])
    return f'<div class="chat-movie"><img src="{m["cover"]}" onerror="this.style.display=\'none\'"><div><b>[{m["id"]}] {m["name"]}</b><br><small>Score: {m["score"]} | {cats}<br>{m["country"]} | {m["duration"]} | {m["release_date"]}</small></div></div>'


def process_chat(message: str) -> dict:
    msg = message.strip()
    lower = msg.lower()

    if lower in ["help", "h"]:
        text = """<b>Commands:</b><br>
  <code>top 5</code> — top N by score<br>
  <code>search xxx</code> — search by name<br>
  <code>rank 动画, 冒险</code> — rank by category<br>
  <code>like 霸王别姬</code> — similar movies<br>
  <code>info 3</code> — movie details<br>
  <code>stats</code> — database stats<br>
  <code>cats</code> — list categories"""
        return {"type": "text", "text": text}

    if lower in ["stats"]:
        avg = sum(m["score"] for m in movies) / len(movies)
        return {"type": "text", "text": f"<b>Movies:</b> {len(movies)} | <b>Avg Score:</b> {avg:.2f} | <b>Categories:</b> {len(all_categories)}"}

    if lower in ["cats", "categories"]:
        return {"type": "text", "text": f"<b>Categories ({len(all_categories)}):</b><br>" + ", ".join(f'<span class="chat-tag">{c}</span>' for c in all_categories)}

    m = re.search(r"^top\s*(\d+)$", lower)
    if m:
        n = min(int(m.group(1)), 50)
        results = sorted(movies, key=lambda x: x["score"], reverse=True)[:n]
        html = f"<b>Top {n} by Score:</b><br>" + "".join(format_movie_html(r) for r in results)
        return {"type": "movies", "text": html, "movies": results}

    m = re.search(r"^search\s+(.+)$", lower)
    if m:
        results = search_movies(m.group(1).strip())
        if not results:
            return {"type": "text", "text": f"No results for \"{m.group(1).strip()}\""}
        html = f"<b>Search: \"{m.group(1).strip()}\"</b> ({len(results)} found)<br>" + "".join(format_movie_html(r) for r in results[:10])
        return {"type": "movies", "text": html, "movies": results[:10]}

    m = re.search(r"^rank\s+(.+)$", lower)
    if m:
        cats = [c.strip() for c in m.group(1).split(",") if c.strip()]
        results = rank_by_categories(cats, 10)
        if not results:
            return {"type": "text", "text": f"No movies match: {', '.join(cats)}"}
        html = f"<b>Ranked by: {', '.join(cats)}</b><br>" + "".join(format_movie_html(r) for r in results)
        return {"type": "movies", "text": html, "movies": results}

    m = re.search(r"^like\s+(.+)$", lower)
    if m:
        target, results = similar_movies(m.group(1).strip())
        if target is None:
            return {"type": "text", "text": f"Movie not found: \"{m.group(1).strip()}\""}
        html = f"<b>Similar to: {target['name']}</b><br>" + "".join(format_movie_html(r) for r in results)
        return {"type": "movies", "text": html, "movies": [target] + results}

    m = re.search(r"^info\s+(.+)$", lower)
    if m:
        target, results = similar_movies(m.group(1).strip())
        if target is None:
            return {"type": "text", "text": f"Movie not found: \"{m.group(1).strip()}\""}
        html = format_movie_html(target) + "<br><b>Similar:</b><br>" + "".join(format_movie_html(r) for r in results[:5])
        return {"type": "movies", "text": html, "movies": [target] + results[:5]}

    results = search_movies(msg)
    if results:
        html = f"<b>Results for \"{msg}\":</b><br>" + "".join(format_movie_html(r) for r in results[:10])
        return {"type": "movies", "text": html, "movies": results[:10]}

    return {"type": "text", "text": 'Type <code>help</code> for commands'}


class ChatRequest(BaseModel):
    message: str
    api_key: str = ""


app = FastAPI(title="Movie API", docs_url="/docs")
app.mount("/posters", StaticFiles(directory=str(BASE / "output" / "posters")), name="posters")


@app.get("/")
def index():
    html = (BASE / "index.html").read_text(encoding="utf-8")
    cats_html = "".join(f'<span class="tag" data-cat="{c}">{c}</span>' for c in all_categories)
    html = html.replace("__CATS__", cats_html)
    return HTMLResponse(html)


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    return process_chat(req.message)


gemini_system_prompt = """You are a friendly movie assistant with access to a database of 100 movies.

The database includes Chinese and international films. Each movie has: id, name (Chinese + English), categories/genres, country, duration, release_date, and score (out of 10).

Categories available: """ + ", ".join(all_categories) + """

When users ask about movies, use the available tools to search, rank, or find movies. Answer in Chinese unless the user asks in English. Be concise but enthusiastic. Recommend movies naturally. When showing results, highlight the score and explain why the user might like them. Keep responses short - max 5-6 movie recommendations per message."""

gemini_tools = [
    {
        "name": "search_movies",
        "description": "Search movies by keyword in name, country, or category",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword"},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "rank_by_categories",
        "description": "Rank movies by preferred categories/genres using similarity. Returns movies that best match the requested categories.",
        "parameters": {
            "type": "object",
            "properties": {
                "categories": {"type": "string", "description": "Comma-separated categories, e.g. '剧情, 爱情'"},
                "top_n": {"type": "integer", "description": "Number of results (max 10)"},
            },
            "required": ["categories"],
        },
    },
    {
        "name": "top_movies",
        "description": "Get top movies by score",
        "parameters": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of movies (max 20)"},
            },
            "required": ["n"],
        },
    },
    {
        "name": "find_similar",
        "description": "Find movies similar to a given movie name or ID. Use when user says 'like 霸王别姬', 'similar to ...', or 'recommend movies like ...'",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Movie name or ID to find similar movies for"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_categories",
        "description": "List all available movie categories/genres",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_stats",
        "description": "Get database statistics (total movies, average score, etc.)",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_tool(name, args):
    if name == "search_movies":
        results = search_movies(args["keyword"])
        return [{"id": m["id"], "name": m["name"], "score": m["score"],
                 "categories": m["categories"], "country": m["country"],
                 "duration": m["duration"], "release_date": m["release_date"]} for m in results[:10]]
    elif name == "rank_by_categories":
        cats = [c.strip() for c in args["categories"].split(",") if c.strip()]
        top_n = min(args.get("top_n", 10), 10)
        results = rank_by_categories(cats, top_n)
        return [{"id": m["id"], "name": m["name"], "score": m["score"],
                 "categories": m["categories"], "country": m["country"],
                 "duration": m["duration"], "release_date": m["release_date"]} for m in results]
    elif name == "top_movies":
        n = min(args.get("n", 10), 20)
        results = sorted(movies, key=lambda x: x["score"], reverse=True)[:n]
        return [{"id": m["id"], "name": m["name"], "score": m["score"],
                 "categories": m["categories"], "country": m["country"]} for m in results]
    elif name == "find_similar":
        target, results = similar_movies(args["query"])
        if target is None:
            return {"error": "Movie not found"}
        return {
            "target": {"id": target["id"], "name": target["name"], "score": target["score"],
                       "categories": target["categories"]},
            "similar": [{"id": m["id"], "name": m["name"], "score": m["score"],
                         "categories": m["categories"]} for m in results[:8]]
        }
    elif name == "list_categories":
        return {"categories": all_categories}
    elif name == "get_stats":
        avg = sum(m["score"] for m in movies) / len(movies)
        return {"total": len(movies), "avg_score": round(avg, 2), "categories_count": len(all_categories)}
    return {}


@app.post("/api/chat/gemini")
def api_chat_gemini(req: ChatRequest):
    api_key = req.api_key or GEMINI_API_KEY
    if not api_key:
        return {"type": "text", "text": "No Gemini API key. Click the gear icon to set one, or set <code>GEMINI_API_KEY</code> env var."}

    client = genai.Client(api_key=api_key)

    contents = [
        genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=req.message)],
        )
    ]

    config = genai_types.GenerateContentConfig(
        system_instruction=gemini_system_prompt,
        tools=[genai_types.Tool(function_declarations=[
            genai_types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters=t["parameters"],
            ) for t in gemini_tools
        ])],
        temperature=0.7,
        max_output_tokens=800,
    )

    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )
    except Exception as e:
        return {"type": "text", "text": f"Gemini error: {e}"}

    if not resp.candidates:
        return {"type": "text", "text": "No response from Gemini."}

    candidate = resp.candidates[0]
    parts = candidate.content.parts if candidate.content else []

    for part in parts:
        if part.function_call:
            fc = part.function_call
            result = execute_tool(fc.name, dict(fc.args))
            function_response = genai_types.Part.from_function_response(
                name=fc.name,
                response={"result": result},
            )
            contents.append(genai_types.Content(
                role="model",
                parts=[part],
            ))
            contents.append(genai_types.Content(
                role="user",
                parts=[function_response],
            ))

            try:
                resp2 = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=config,
                )
                if resp2.candidates and resp2.candidates[0].content:
                    text_parts = [p.text for p in resp2.candidates[0].content.parts if p.text]
                    text = "\n".join(text_parts) if text_parts else "Here are your results!"
                else:
                    text = json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                text = json.dumps(result, ensure_ascii=False, indent=2)

            return {"type": "text", "text": text.replace("\n", "<br>")}

    text_parts = [p.text for p in parts if p.text]
    text = "\n".join(text_parts) if text_parts else "I'm not sure how to help with that."

    return {"type": "text", "text": text.replace("\n", "<br>")}


@app.get("/api/chat/gemini/status")
def api_gemini_status():
    return {"available": bool(gemini_client or GEMINI_API_KEY)}


@app.get("/api/search")
def api_search(q: str = Query(...)):
    results = search_movies(q)
    return {"count": len(results), "movies": results}


@app.get("/api/rank")
def api_rank(categories: str = Query(...), q: str = Query(None), top_n: int = Query(50, ge=1, le=100)):
    cats = [c.strip() for c in categories.split(",") if c.strip()]
    query_set = set(cats)
    scored = []
    for m in movies:
        overlap = len(query_set & set(m["categories"]))
        if overlap > 0:
            jac = jaccard(query_set, set(m["categories"]))
            scored.append((overlap, jac, m["score"], m))
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    results = [item[3] for item in scored[:top_n]]
    if q:
        kw = q.lower()
        results = [m for m in results if kw in m["name"].lower() or kw in m["country"].lower()
                   or any(kw in c.lower() for c in m["categories"])]
    return {"count": len(results), "movies": results}


@app.get("/api/top")
def api_top(n: int = Query(50, ge=1, le=100)):
    results = sorted(movies, key=lambda x: x["score"], reverse=True)[:n]
    return {"count": len(results), "movies": results}


@app.get("/api/movie/{movie_id}")
def api_movie(movie_id: int):
    for m in movies:
        if m["id"] == movie_id:
            return m
    return {"error": "not found"}


@app.get("/api/similar/{movie_id}")
def api_similar(movie_id: int):
    target = None
    for m in movies:
        if m["id"] == movie_id:
            target = m
            break
    if not target:
        return {"error": "not found"}
    target_set = set(target["categories"])
    scored = []
    for m in movies:
        if m is target:
            continue
        jac = jaccard(target_set, set(m["categories"]))
        if jac > 0:
            scored.append((jac, m["score"], m))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return {"count": len(scored), "movies": [item[2] for item in scored[:10]]}


@app.get("/api/categories")
def api_categories():
    counts = {}
    for m in movies:
        for c in m["categories"]:
            counts[c] = counts.get(c, 0) + 1
    return {"categories": [{"name": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)]}


@app.get("/api/stats")
def api_stats():
    avg_score = sum(m["score"] for m in movies) / len(movies)
    countries = {}
    for m in movies:
        for c in m["country"].split("、"):
            c = c.strip()
            if c:
                countries[c] = countries.get(c, 0) + 1
    top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "total": len(movies),
        "avg_score": round(avg_score, 2),
        "categories_count": len(all_categories),
        "top_countries": [{"name": k, "count": v} for k, v in top_countries],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
