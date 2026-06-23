import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Demokratie jetzt — Projekt-Dashboard",
    page_icon="🗳️",
    layout="wide",
)


@st.cache_data
def load_data(path: str = "projekte.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["startdatum"] = pd.to_datetime(df["startdatum"], errors="coerce")
    df["enddatum"] = pd.to_datetime(df["enddatum"], errors="coerce")
    df["jahr"] = df["startdatum"].dt.year
    return df


df = load_data()

st.title("🗳️ Demokratie jetzt — Projekt-Dashboard")
st.caption("Öffentliche Übersicht über unsere Projekte, Teilnehmende und Wirkung.")

# Sidebar filters
st.sidebar.header("Filter")

min_datum = df["startdatum"].min().date()
max_datum = df["startdatum"].max().date()
zeitraum = st.sidebar.slider(
    "Zeitraum (Startdatum)",
    min_value=min_datum,
    max_value=max_datum,
    value=(min_datum, max_datum),
    format="DD.MM.YYYY",
)

kategorien = sorted(df["kategorie"].dropna().unique().tolist())
kategorie_filter = st.sidebar.multiselect("Kategorie", kategorien, default=kategorien)

regionen = sorted(df["region"].dropna().unique().tolist())
region_filter = st.sidebar.multiselect("Region", regionen, default=regionen)

status_werte = sorted(df["status"].dropna().unique().tolist())
status_filter = st.sidebar.multiselect("Status", status_werte, default=status_werte)

filtered = df[
    (df["startdatum"].dt.date >= zeitraum[0])
    & (df["startdatum"].dt.date <= zeitraum[1])
    & df["kategorie"].isin(kategorie_filter)
    & df["region"].isin(region_filter)
    & df["status"].isin(status_filter)
]

if filtered.empty:
    st.warning("Keine Projekte für die aktuelle Filterauswahl.")
    st.stop()

# KPIs
col1, col2, col3, col4 = st.columns(4)

anzahl_projekte = len(filtered)
teilnehmende = int(filtered["ist_teilnehmende"].fillna(0).sum())
neuwaehler = int(filtered["ist_neuwähler_aktiviert"].fillna(0).sum())

ziel_tn = filtered["ziel_teilnehmende"].fillna(0).sum()
zielerreichung = (teilnehmende / ziel_tn * 100) if ziel_tn > 0 else 0

col1.metric("Projekte", f"{anzahl_projekte}")
col2.metric("Teilnehmende", f"{teilnehmende:,}".replace(",", "."))
col3.metric("Neuwähler aktiviert", f"{neuwaehler:,}".replace(",", "."))
col4.metric("Zielerreichung", f"{zielerreichung:.0f} %")

st.markdown("---")

# Budget summary (aggregate only — per user decision: transparency yes, but only totals)
budget_geplant = int(filtered["budget_geplant"].fillna(0).sum())
budget_verbraucht = int(filtered["budget_verbraucht"].fillna(0).sum())
bcol1, bcol2 = st.columns(2)
bcol1.metric("Budget geplant (Summe)", f"{budget_geplant:,} €".replace(",", "."))
bcol2.metric("Budget verbraucht (Summe)", f"{budget_verbraucht:,} €".replace(",", "."))

st.markdown("---")

# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("Projekte nach Kategorie")
    by_cat = filtered.groupby("kategorie").size().reset_index(name="Anzahl")
    fig = px.bar(by_cat, x="kategorie", y="Anzahl", color="kategorie")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Anzahl Projekte")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Teilnehmende nach Region")
    by_region = (
        filtered.groupby("region")["ist_teilnehmende"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = px.bar(by_region, x="ist_teilnehmende", y="region", orientation="h")
    fig.update_layout(xaxis_title="Teilnehmende", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Teilnehmende nach Zielgruppe")
    by_zg = (
        filtered.groupby("zielgruppe")["ist_teilnehmende"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = px.bar(by_zg, x="ist_teilnehmende", y="zielgruppe", orientation="h")
    fig.update_layout(xaxis_title="Teilnehmende", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Wirkungsscore Ø nach Kategorie")
    by_wirk = (
        filtered.dropna(subset=["wirkungsscore"])
        .groupby("kategorie")["wirkungsscore"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = px.bar(by_wirk, x="wirkungsscore", y="kategorie", orientation="h", color="wirkungsscore", color_continuous_scale="Blues")
    fig.update_layout(xaxis_title="Ø Wirkungsscore", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Projektliste (ohne Zielerreichung pro Projekt — user decision)
st.subheader("Projektliste")
anzeige_spalten = [
    "projekt_id",
    "projektname",
    "kategorie",
    "region",
    "zielgruppe",
    "startdatum",
    "enddatum",
    "status",
    "ist_teilnehmende",
    "ist_neuwähler_aktiviert",
    "wirkungsscore",
    "zufriedenheit_schnitt",
]
st.dataframe(
    filtered[anzeige_spalten].rename(
        columns={
            "projekt_id": "ID",
            "projektname": "Projektname",
            "kategorie": "Kategorie",
            "region": "Region",
            "zielgruppe": "Zielgruppe",
            "startdatum": "Start",
            "enddatum": "Ende",
            "status": "Status",
            "ist_teilnehmende": "Teilnehmende",
            "ist_neuwähler_aktiviert": "Neuwähler",
            "wirkungsscore": "Wirkungsscore",
            "zufriedenheit_schnitt": "Zufriedenheit",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption(f"Stand: {len(df)} Projekte gesamt im Datensatz · gefiltert: {len(filtered)}")
