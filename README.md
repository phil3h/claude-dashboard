# Demokratie jetzt — Projekt-Dashboard

Öffentliches Dashboard zu Projekten von Demokratie jetzt (Workshops, Kampagnen, Bildungsprojekte etc.).

## Lokal starten

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dashboard öffnet sich unter http://localhost:8501

## Daten

`projekte.csv` — Liste aller Projekte mit Kennzahlen (Teilnehmende, Neuwähler, Wirkung).

## Deployment

Gehostet via [Streamlit Community Cloud](https://share.streamlit.io) — automatisches Update bei jedem Push auf `main`.
