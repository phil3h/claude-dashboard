import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Demokratie jetzt — Projekt-Dashboard",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#1f4e79"
SECONDARY = "#4a90c2"
ACCENT = "#d97706"
PALETTE = ["#1f4e79", "#4a90c2", "#7fb3d5", "#d97706", "#e8a04f", "#6c8e9e"]
PLOTLY_LAYOUT = dict(
    font=dict(family="sans-serif", size=13, color="#1a1a1a"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor="#e8eef3", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#e8eef3", zeroline=False),
)
PLOTLY_CONFIG = {"displayModeBar": False}


def style_fig(fig: go.Figure, *, title: str = "") -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=14, color="#1a1a1a")))
    return fig


def fmt_int(n: float) -> str:
    return f"{int(n):,}".replace(",", ".")


st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1300px; }
    h1 { color: #1f4e79; font-weight: 700; letter-spacing: -0.02em; }
    h2 { color: #1a1a1a; font-weight: 600; font-size: 1.25rem; margin-top: 1.5rem; }
    h3 { color: #1a1a1a; font-weight: 600; font-size: 1.05rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1f4e79; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.05em; }
    [data-testid="stSidebar"] { background-color: #f5f7fa; }
    .stDataFrame { border: 1px solid #e8eef3; border-radius: 8px; }
    hr { margin: 2rem 0; border-color: #e8eef3; }
    .footer { color: #6c757d; font-size: 0.85rem; text-align: center; margin-top: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(path: str = "projekte.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["startdatum"] = pd.to_datetime(df["startdatum"], errors="coerce")
    df["enddatum"] = pd.to_datetime(df["enddatum"], errors="coerce")
    df["jahr"] = df["startdatum"].dt.year
    return df


df = load_data()

st.title("🗳️ Demokratie jetzt")
st.markdown(
    "<p style='font-size:1.1rem; color:#4a4a4a; margin-top:-0.5rem;'>"
    "Projekt-Dashboard — Workshops, Kampagnen, Wirkung."
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### Filter")
    min_datum = df["startdatum"].min().date()
    max_datum = df["startdatum"].max().date()
    zeitraum = st.slider(
        "Zeitraum (Startdatum)",
        min_value=min_datum,
        max_value=max_datum,
        value=(min_datum, max_datum),
        format="DD.MM.YYYY",
    )
    kategorien = sorted(df["kategorie"].dropna().unique().tolist())
    kategorie_filter = st.multiselect("Kategorie", kategorien, default=kategorien)
    regionen = sorted(df["region"].dropna().unique().tolist())
    region_filter = st.multiselect("Region", regionen, default=regionen)
    status_werte = sorted(df["status"].dropna().unique().tolist())
    status_filter = st.multiselect("Status", status_werte, default=status_werte)
    st.divider()
    st.caption(f"Datensatz: {len(df)} Projekte")

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
st.markdown("## Auf einen Blick")
k1, k2, k3, k4 = st.columns(4)

anzahl_projekte = len(filtered)
teilnehmende = int(filtered["ist_teilnehmende"].fillna(0).sum())
neuwaehler = int(filtered["ist_neuwähler_aktiviert"].fillna(0).sum())
ziel_tn = filtered["ziel_teilnehmende"].fillna(0).sum()
zielerreichung = (teilnehmende / ziel_tn * 100) if ziel_tn > 0 else 0

k1.metric("Projekte", fmt_int(anzahl_projekte))
k2.metric("Teilnehmende", fmt_int(teilnehmende))
k3.metric("Neuwähler aktiviert", fmt_int(neuwaehler))
k4.metric("Zielerreichung", f"{zielerreichung:.0f} %")

# Budget
b1, b2 = st.columns(2)
budget_geplant = int(filtered["budget_geplant"].fillna(0).sum())
budget_verbraucht = int(filtered["budget_verbraucht"].fillna(0).sum())
b1.metric("Budget geplant", f"{fmt_int(budget_geplant)} €")
b2.metric("Budget verbraucht", f"{fmt_int(budget_verbraucht)} €")

st.divider()

# Charts
st.markdown("## Verteilung")

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("#### Projekte nach Kategorie")
    by_cat = filtered.groupby("kategorie").size().reset_index(name="Anzahl").sort_values("Anzahl", ascending=True)
    fig = px.bar(by_cat, x="Anzahl", y="kategorie", orientation="h", color_discrete_sequence=[PRIMARY])
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x} Projekte<extra></extra>")
    style_fig(fig)
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False, height=320)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with c2:
    st.markdown("#### Teilnehmende nach Region")
    by_region = (
        filtered.groupby("region")["ist_teilnehmende"].sum().sort_values(ascending=True).reset_index()
    )
    fig = px.bar(by_region, x="ist_teilnehmende", y="region", orientation="h", color_discrete_sequence=[SECONDARY])
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:,.0f} Teilnehmende<extra></extra>")
    style_fig(fig)
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False, height=320)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

c3, c4 = st.columns(2, gap="large")

with c3:
    st.markdown("#### Teilnehmende nach Zielgruppe")
    by_zg = (
        filtered.groupby("zielgruppe")["ist_teilnehmende"].sum().sort_values(ascending=True).reset_index()
    )
    fig = px.bar(by_zg, x="ist_teilnehmende", y="zielgruppe", orientation="h", color_discrete_sequence=[ACCENT])
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:,.0f} Teilnehmende<extra></extra>")
    style_fig(fig)
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False, height=320)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

with c4:
    st.markdown("#### Wirkungsscore Ø nach Kategorie")
    by_wirk = (
        filtered.dropna(subset=["wirkungsscore"])
        .groupby("kategorie")["wirkungsscore"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig = px.bar(
        by_wirk, x="wirkungsscore", y="kategorie", orientation="h",
        color="wirkungsscore", color_continuous_scale=[[0, "#cfe0ee"], [1, PRIMARY]],
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Wirkung: %{x:.1f}<extra></extra>")
    style_fig(fig)
    fig.update_layout(xaxis_title="", yaxis_title="", coloraxis_showscale=False, height=320)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

st.divider()

# Tabelle
st.markdown("## Projektliste")
anzeige_spalten = [
    "projekt_id", "projektname", "kategorie", "region", "zielgruppe",
    "startdatum", "enddatum", "status",
    "ist_teilnehmende", "ist_neuwähler_aktiviert",
    "wirkungsscore", "zufriedenheit_schnitt",
]
display_df = filtered[anzeige_spalten].rename(
    columns={
        "projekt_id": "ID", "projektname": "Projektname", "kategorie": "Kategorie",
        "region": "Region", "zielgruppe": "Zielgruppe",
        "startdatum": "Start", "enddatum": "Ende", "status": "Status",
        "ist_teilnehmende": "Teilnehmende", "ist_neuwähler_aktiviert": "Neuwähler",
        "wirkungsscore": "Wirkung", "zufriedenheit_schnitt": "Zufriedenheit",
    }
)
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Start": st.column_config.DateColumn(format="DD.MM.YYYY"),
        "Ende": st.column_config.DateColumn(format="DD.MM.YYYY"),
        "Teilnehmende": st.column_config.NumberColumn(format="%d"),
        "Neuwähler": st.column_config.NumberColumn(format="%d"),
        "Wirkung": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
        "Zufriedenheit": st.column_config.NumberColumn(format="%.1f ⭐"),
    },
)

st.markdown(
    f"<div class='footer'>Gefiltert: {len(filtered)} von {len(df)} Projekten · "
    f"Demokratie jetzt · Stand {pd.Timestamp.today().strftime('%d.%m.%Y')}</div>",
    unsafe_allow_html=True,
)
