import math
import numpy as np
import pandas as pd
import streamlit as st

APP_TITLE = "Rohrreibungszahl-Rechner"
APP_VERSION = "0.1.0V"

ROUGHNESS_ROWS = [
    ("Gezogene und gepresste Rohre aus Kupfer, Messing, Bronze, Aluminium, Glas oder Kunststoff", "neu, technisch glatt", "0.001 … 0.0015"),
    ("Gezogene und gepresste Rohre aus Kupfer, Messing, Bronze, Aluminium, Glas oder Kunststoff", "gebraucht", "0.010 … 0.0300"),
    ("Gummischlauch", "neu, handelsüblich", "0.0016"),
    ("Rohre aus Gusseisen", "neu, handelsüblich", "0.25 … 0.5"),
    ("Rohre aus Gusseisen", "angerostet", "1.00 … 1.5"),
    ("Rohre aus Gusseisen", "verkrustet", "1.50 … 3.0"),
    ("Rohre aus Gusseisen", "nach mehrjährigem Betrieb gereinigt", "0.30 … 1.5"),
    ("Rohre aus Gusseisen", "städtliche Kanalisation", "1.20"),
    ("Neue nahtlose Stahlrohre, gewalzt oder gezogen", "mit Walzhaut", "0.02 … 0.06"),
    ("Neue nahtlose Stahlrohre, gewalzt oder gezogen", "gebeizt", "0.03 … 0.04"),
    ("Neue nahtlose Stahlrohre, gewalzt oder gezogen", "bei engen Rohren", "… 0.10"),
    ("Neue längsgeschweisste Stahlrohre", "mit Walzhaut", "0.04 … 0.1"),
    ("Neue längsgeschweisste Stahlrohre", "leicht verkrustet", "1.00 … 1.5"),
    ("Neue längsgeschweisste Stahlrohre", "stark verkrustet", "2.00 … 4.0"),
    ("Neue längsgeschweisste Stahlrohre", "gebraucht und gereinigt", "0.15 … 0.2"),
    ("Neue Stahlrohre mit Überzug", "Metallspritzung", "0.08 … 0.09"),
    ("Neue Stahlrohre mit Überzug", "tauchverzinkt", "0.07 … 0.10"),
    ("Neue Stahlrohre mit Überzug", "handelsüblich verzinkt", "0.10 … 0.16"),
    ("Neue Stahlrohre mit Überzug", "bituminiert", "0.050"),
    ("Neue Stahlrohre mit Überzug", "zementiert", "0.180"),
    ("Neue Stahlrohre mit Überzug", "galvanisiert", "0.008"),
    ("Gebrauchte Stahlrohre", "gleichmässige Rostnarben", "0.15"),
    ("Gebrauchte Stahlrohre", "leichte Verkrustung", "0.15 … 0.4"),
    ("Gebrauchte Stahlrohre", "mittlere Verkrustung", "1.50"),
    ("Gebrauchte Stahlrohre", "starke Verkrustung", "2.00 … 4.0"),
    ("Asbest-Zementrohre", "neu, handelsüblich", "0.03 … 0.1"),
    ("Betonrohre, Druckstollen", "handelsüblich Glattstrich", "0.3 … 0.8"),
    ("Betonrohre, Druckstollen", "handelsüblich mittelglatt", "1.0 … 2.0"),
    ("Betonrohre, Druckstollen", "handelsüblich rau", "2.0 … 3.0"),
    ("Betonrohre, Druckstollen", "mehrjähriger Betrieb mit Wasser", "0.2 … 0.3"),
    ("Neues Tonrohr", "Drainagerohr, gebrannt", "0.6 … 0.8"),
    ("Neues Tonrohr", "aus rohen Tonziegeln", "9.0"),
    ("Medizinisches, Kälte- oder Heizungsgewinderohr", "neu, handelsüblich", "0.045"),
    ("Medizinisches, Kälte- oder Heizungsstahlrohr nahtlos", "neu, handelsüblich", "0.045"),
    ("Medizinisches, Kälte- oder Heizungskupferrohr", "neu, handelsüblich", "0.0005 … 0.0015"),
    ("Medizinisches, Kälte- oder Heizungspräzisionsstahlrohr", "neu, handelsüblich", "0.001 … 0.0015"),
    ("Medizinisches, Kälte- oder Heizungskunststoffrohr", "neu, handelsüblich", "0.001 … 0.0015"),
]

st.set_page_config(page_title=APP_TITLE, layout="wide")


def calc_laminar(Re):
    return 64.0 / Re


def calc_blasius(Re):
    return 0.3164 / (Re ** 0.25)


def calc_nikuradse(k_mm, d_mm):
    return (-2.0 * math.log10((k_mm / 1000.0) / 3.71 / (d_mm / 1000.0))) ** -2


def calc_prandtl(Re, iterations=20):
    lam = 0.02
    for _ in range(iterations):
        lam = (2.0 * math.log10(Re * math.sqrt(lam)) - 0.8) ** -2
    return lam


def calc_colebrook_white(Re, k_mm, d_mm, iterations=25):
    lam = 0.02
    k = k_mm / 1000.0
    d = d_mm / 1000.0
    for _ in range(iterations):
        lam = (-2.0 * math.log10(2.51 / (Re * math.sqrt(lam)) + k / (3.71 * d))) ** -2
    return lam


def friction_factor(Re, k_mm, d_mm):
    if Re <= 0 or d_mm <= 0:
        raise ValueError("Reynolds-Zahl und Durchmesser müssen größer als 0 sein.")
    rel_roughness = (k_mm / 1000.0) / (d_mm / 1000.0)
    lam_hp = calc_laminar(Re)
    lam_blasius = calc_blasius(Re) if Re > 0 else np.nan
    lam_nik = calc_nikuradse(k_mm, d_mm) if k_mm > 0 else np.nan
    lam_pr = calc_prandtl(Re) if Re > 2320 else np.nan
    lam_cw = calc_colebrook_white(Re, k_mm, d_mm) if Re > 2320 else np.nan
    check_moody = Re * math.sqrt(lam_nik) * rel_roughness if k_mm > 0 else np.nan
    if Re < 2320:
        chosen = "Hagen-Poiseuille"
        lam = lam_hp
    else:
        if k_mm > 0 and check_moody >= 200:
            chosen = "Nikuradse / Colebrook-White"
        elif rel_roughness < 0.001 and Re < 10000:
            chosen = "Blasius / Colebrook-White"
        elif rel_roughness < 0.0002 and Re < 100000:
            chosen = "Blasius / Colebrook-White"
        elif rel_roughness < 0.00002 and Re < 1000000:
            chosen = "Prandtl / Colebrook-White"
        elif rel_roughness < 0.00001:
            chosen = "Prandtl / Colebrook-White"
        else:
            chosen = "Colebrook-White"
        lam = lam_cw
    overview = pd.DataFrame(
        [
            ("Reynolds-Zahl", round(Re, 2)),
            ("Rohrrauheit k [mm]", round(k_mm, 6)),
            ("Innendurchmesser d [mm]", round(d_mm, 3)),
            ("Relative Rauheit k/d [-]", round(rel_roughness, 8)),
            ("Ausgewählte Berechnung", chosen),
            ("Rohrreibungszahl λ [-]", round(lam, 6)),
        ],
        columns=["Parameter", "Wert"],
    )
    formula_table = pd.DataFrame(
        [
            ("Hagen-Poiseuille", round(lam_hp, 6) if np.isfinite(lam_hp) else np.nan),
            ("Blasius", round(lam_blasius, 6) if np.isfinite(lam_blasius) else np.nan),
            ("Nikuradse", round(lam_nik, 6) if np.isfinite(lam_nik) else np.nan),
            ("Prandtl", round(lam_pr, 6) if np.isfinite(lam_pr) else np.nan),
            ("Colebrook-White", round(lam_cw, 6) if np.isfinite(lam_cw) else np.nan),
        ],
        columns=["Formel", "Rohrreibungszahl λ [-]"],
    )
    return overview, formula_table


st.markdown(
    f"""
    <div style='display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:0.2rem;'>
        <div style='font-size:3rem; font-weight:700; line-height:1.1;'>{APP_TITLE}</div>
        <div style='color:#9ca3af; font-size:1rem; line-height:1.1;'>{APP_VERSION}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Berechnung der Rohrreibungszahl auf Basis des Moody-Diagramms und mehrerer anerkannter Gleichungen.")
st.info("Die Rohrreibungszahl wird anhand verschiedener Formeln bestimmt. So wird das gesamte Moody-Diagramm abgedeckt. Folgende Formeln werden betrachtet: Gesetz von Hagen-Poiseuille, Formeln nach Blasius, nach Nikuradse, nach Colebrook & White und nach Prandtl.")

left, right = st.columns([1, 1.15])

with left:
    reynolds = st.number_input("Reynolds-Zahl Re [-]", min_value=1.0, value=100000.0, step=1000.0)
    diameter = st.number_input("Rohrinnendurchmesser d [mm]", min_value=0.001, value=25.0, step=0.1)
    roughness = st.number_input("Rohrrauheit k [mm]", min_value=0.0, value=0.045, step=0.0001, format="%.4f")
    run = st.button("Berechnen", use_container_width=True)

with right:
    st.subheader("Ergebnis")
    if run:
        try:
            overview_df, formulas_df = friction_factor(float(reynolds), float(roughness), float(diameter))
            st.dataframe(overview_df, use_container_width=True, hide_index=True)
            st.markdown("### Formeln im Vergleich")
            st.dataframe(formulas_df, use_container_width=True, hide_index=True)
            csv_data = pd.concat(
                [
                    overview_df.assign(Bereich="Ergebnis"),
                    formulas_df.rename(columns={"Formel": "Parameter", "Rohrreibungszahl λ [-]": "Wert"}).assign(Bereich="Formelvergleich"),
                ],
                ignore_index=True,
            )
            st.download_button(
                label="CSV herunterladen",
                data=csv_data.to_csv(index=False, sep=";").encode("utf-8"),
                file_name="rohrreibungszahl-ergebnis.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Fehler bei der Berechnung: {e}")
    else:
        st.info("Eingaben setzen und auf Berechnen klicken.")

st.markdown("---")
with st.expander("Anleitung"):
    st.markdown(
        """
Mit diesem Tool wird die **Rohrreibungszahl λ** für eine Rohrströmung berechnet.

Dafür werden drei Eingaben benötigt:
- **Reynolds-Zahl Re**,
- **Rohrinnendurchmesser d**,
- **Rohrrauheit k**.

Die Rohrreibungszahl wird anhand verschiedener Formeln bestimmt. So wird das gesamte **Moody-Diagramm** abgedeckt.
Berücksichtigt werden:
- Gesetz von **Hagen-Poiseuille**,
- Formel nach **Blasius**,
- Formel nach **Nikuradse**,
- Formel nach **Prandtl**,
- sowie **Colebrook-White**.

Im Ergebnisbereich wird die ausgewählte Rohrreibungszahl angezeigt. Zusätzlich zeigt die Vergleichstabelle, welche Werte sich aus den einzelnen Formeln ergeben.

Die Tabelle **Rohrrauheitswerte** unten hilft bei der Wahl plausibler Eingaben für die Rauheit k.
"""
    )
with st.expander("Rohrrauheitswerte"):
    st.caption("Orientierungswerte für die Eingabe von k [mm].")
    roughness_df = pd.DataFrame(ROUGHNESS_ROWS, columns=["Werkstoff und Rohrart", "Zustand der Rohre", "k [mm]"])
    st.dataframe(roughness_df, use_container_width=True, hide_index=True)
