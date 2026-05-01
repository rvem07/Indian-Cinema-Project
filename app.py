"""
app.py  –  Tollywood Timeline Flask App
Data source: indiancine.ma (scraped via their JSON API)

Run: python3 app.py
Open: http://127.0.0.1:5000
"""

import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR  = os.path.dirname(__file__)
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")

MOVIES_PATH       = os.path.join(CLEAN_DIR, "all_tollywood_movies.csv")
PEOPLE_PATH       = os.path.join(CLEAN_DIR, "people.csv")
MOVIE_PEOPLE_PATH = os.path.join(CLEAN_DIR, "movie_people.csv")

RESULTS_PER_PAGE = 500

DECADES = ["1930s", "1940s", "1950s", "1960s", "1970s",
           "1980s", "1990s", "2000s", "2010s", "2020s"]

# ─── Load Data ────────────────────────────────────────────────────────────────

def load_csv(path, name):
    if not os.path.exists(path):
        print(f"WARNING: {name} not found. Run: python3 scripts/scrape_indiancine.py")
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str).fillna("")
    print(f"Loaded {len(df):,} rows  ← {name}")
    return df


print("Loading Tollywood datasets...")
films_df        = load_csv(MOVIES_PATH,       "all_tollywood_movies.csv")
people_df       = load_csv(PEOPLE_PATH,       "people.csv")
movie_people_df = load_csv(MOVIE_PEOPLE_PATH, "movie_people.csv")
print("Datasets ready.\n")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_all_genres():
    if films_df.empty or "genres" not in films_df.columns:
        return []
    genre_set = set()
    for genre_str in films_df["genres"]:
        for g in str(genre_str).split(","):
            g = g.strip()
            if g:
                genre_set.add(g)
    return sorted(genre_set)


def build_decade_stats():
    stats = []
    for label in DECADES:
        if films_df.empty or "decade" not in films_df.columns:
            count = 0
        else:
            count = int((films_df["decade"] == label).sum())
        stats.append({"label": label, "count": count})
    return stats


# ─── Home ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    overall_stats = {
        "num_films":       len(films_df),
        "num_decades":     len(DECADES),
        "num_connections": len(movie_people_df),
    }
    return render_template("index.html",
                           stats=overall_stats,
                           decade_stats=build_decade_stats())


# ─── Decade Page ──────────────────────────────────────────────────────────────

@app.route("/decade/<decade_str>")
def decade(decade_str):
    if decade_str not in DECADES:
        return render_template("decade.html", decade_str=decade_str,
                               movies=[], query="", genre="", genres=[],
                               total=0, shown=0, valid=False)

    if films_df.empty:
        return render_template("decade.html", decade_str=decade_str,
                               movies=[], query="", genre="", genres=[],
                               total=0, shown=0, valid=True)

    query = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    sort  = request.args.get("sort", "year_asc").strip()

    results = films_df[films_df["decade"] == decade_str].copy()

    if query:
        results = results[results["title"].str.contains(query, case=False, na=False)]

    if genre:
        results = results[results["genres"].str.contains(genre, case=False, na=False)]

    if sort == "alpha_asc":
        results = results.sort_values("title", ascending=True)
    elif sort == "alpha_desc":
        results = results.sort_values("title", ascending=False)
    elif sort == "year_desc":
        results = results.sort_values("year", ascending=False)
    else:
        results = results.sort_values("year", ascending=True)

    total   = len(results)
    results = results.head(RESULTS_PER_PAGE)

    return render_template("decade.html",
                           decade_str=decade_str,
                           movies=results.to_dict("records"),
                           query=query, genre=genre, sort=sort,
                           genres=get_all_genres(),
                           total=total, shown=len(results), valid=True)


# ─── Movie Detail ─────────────────────────────────────────────────────────────

@app.route("/movie/<film_id>")
def movie_detail(film_id):
    if films_df.empty:
        return render_template("film_detail.html", film=None, cast=[])

    rows = films_df[films_df["film_id"] == film_id]
    if rows.empty:
        return render_template("film_detail.html", film=None, cast=[])

    film = rows.iloc[0].to_dict()

    cast = []
    if not movie_people_df.empty:
        cast = movie_people_df[movie_people_df["film_id"] == film_id].to_dict("records")

    return render_template("film_detail.html", film=film, cast=cast)


# Legacy URL redirect
@app.route("/film/<film_id>")
def film_detail(film_id):
    return redirect(url_for("movie_detail", film_id=film_id), code=301)


# ─── All Films Search ─────────────────────────────────────────────────────────

@app.route("/films")
def films():
    if films_df.empty:
        return render_template("films.html", films=[], query="", year="",
                               genre="", genres=[], total=0, shown=0)

    query = request.args.get("q", "").strip()
    year  = request.args.get("year", "").strip()
    genre = request.args.get("genre", "").strip()

    results = films_df.copy()

    if query:
        results = results[results["title"].str.contains(query, case=False, na=False)]
    if year:
        results = results[results["year"] == year]
    if genre:
        results = results[results["genres"].str.contains(genre, case=False, na=False)]

    total   = len(results)
    results = results.head(RESULTS_PER_PAGE)

    return render_template("films.html",
                           films=results.to_dict("records"),
                           query=query, year=year, genre=genre,
                           genres=get_all_genres(),
                           total=total, shown=len(results))


# ─── People ───────────────────────────────────────────────────────────────────

@app.route("/people")
def people():
    if people_df.empty:
        return render_template("people.html", people=[], query="", total=0, shown=0)

    query   = request.args.get("q", "").strip()
    results = people_df.copy()

    if query:
        results = results[results["person_name"].str.contains(query, case=False, na=False)]

    total   = len(results)
    results = results.head(RESULTS_PER_PAGE)

    return render_template("people.html",
                           people=results.to_dict("records"),
                           query=query, total=total, shown=len(results))


# ─── Person Detail ────────────────────────────────────────────────────────────

@app.route("/person/<person_id>")
def person_detail(person_id):
    if people_df.empty:
        return render_template("person_detail.html", person=None, filmography=[])

    rows = people_df[people_df["person_id"] == person_id]
    if rows.empty:
        return render_template("person_detail.html", person=None, filmography=[])

    person     = rows.iloc[0].to_dict()
    filmography = []
    if not movie_people_df.empty:
        filmography = movie_people_df[
            movie_people_df["person_id"] == person_id
        ].to_dict("records")

    return render_template("person_detail.html", person=person, filmography=filmography)


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
