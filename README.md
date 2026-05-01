# Tollywood Timeline

**A decade-by-decade dataset of Telugu cinema from 1930 to 2024.**

Built primarily using data from [Indiancine.ma](https://indiancine.ma) and [Wikipedia](https://en.wikipedia.org).
No Kaggle, Wikidata, OMDb, or TMDb were used as primary data sources.

---

## 🚀 Live Demo
**View the project here:** [https://indian-cinema-project.onrender.com](https://indian-cinema-project.onrender.com)

---

## Project Overview

This project filters the full IMDb dataset to extract films with a Telugu-language Indian release, groups them into decade segments (1930s–2020s), and presents them through a clean timeline-style website.

Each decade is capped at 100 films. When a decade has more than 100 films, the most-voted titles are kept first (using IMDb rating data), so the most well-known films rise to the top.

---

## ☁️ Deployment Note
To bypass GitHub's **100MB file limit** and ensure compatibility with cloud hosting (Vercel/Render), the raw IMDb datasets (~1.7 GB) are excluded via `.gitignore`. The application relies on the pre-processed "clean" CSV files located in the `data/clean/` directory. This allows for lightweight deployments and faster build times without sacrificing the integrity of the filmography data.

---

## Folder Structure

```text
imdb_south_asian_project/
├── data/
│   └── clean/                  ← Processed CSVs used for production
│       ├── tollywood_1930s.csv
│       ├── ... (through 2020s)
│       ├── people.csv          ← Cast/crew connected to Tollywood films
│       └── movie_people.csv    ← Film ↔ person connection table
├── templates/
│   ├── base.html               ← Shared navbar/footer
│   ├── index.html              ← Timeline homepage with decade cards
│   ├── decade.html             ← Decade browsing page with movie card grid
│   ├── film_detail.html        ← Single film detail with synopsis and cast
│   ├── films.html              ← Search across all films
│   ├── people.html             ← Search people
│   └── person_detail.html      ← Person detail with filmography
├── static/
│   ├── style.css
│   └── placeholder_poster.svg  ← Used for all poster images
├── app.py                      ← Flask web application
├── requirements.txt
└── README.md