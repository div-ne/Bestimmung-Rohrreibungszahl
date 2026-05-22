import os
import numpy as np
import pandas as pd
import streamlit as st
import CoolProp.CoolProp as cp

APP_TITLE = "Rohrreibungszahl-Rechner"
APP_VERSION = "0.2.0V"
MOODY_SOURCE = "https://en.wikipedia.org/wiki/Moody_chart"
REPO_URL = "https://github.com/div-ne/Bestimmung-Rohrreibungszahl/"
MOODY_IMAGE = os.path.join(os.path.dirname(__file__), "assets", "moody-diagram.jpg")

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


def calculate_lambda(fluid, temperature_c, pressure_bar, diameter_mm, velocity_ms, roughness_mm):
    k = roughness_mm * 1e-3
    di = diameter_mm * 1e-3
    p = pressure_bar * 1e5
    t = 273.15 + temperature_c
    nu = cp.PropsSI('V', 'T', t, 'P', p, fluid) / cp.PropsSI('D', 'T', t, 'P', p, fluid)
    re = di * velocity_ms / nu
    epsilon_k = k / di
    lambda_hagenpoiseulle = 64 / re
    lambda_blasius = 0.3164 / re**0.25
    lambda_nikuradse = (-2 * np.log10(k / 3.71 / di))**-2
    lambda_prandtl = 0.02
    for _ in range(10):
        lambda_prandtl = (2 * np.log10(re * np.sqrt(lambda_prandtl)))**-2
    lambda_colebrookwhite = 0.02
    for _ in range(10):
        lambda_colebrookwhite = (-2 * np.log10(2.51 / re / lambda_colebrookwhite + k / 3.71 / di))**-2
    check_moody_diagram = re * np.sqrt(lambda_nikuradse) * k / di
    if re < 2320:
        lambda_result = lambda_hagenpoiseulle
        selected = "Hagen-Poiseuille"
        flow_type = "laminare Strömung"
    elif check_moody_diagram >= 200:
        lambda_result = lambda_nikuradse
        selected = "Nikuradse"
        flow_type = "hydraulisch raues Rohr"
    elif epsilon_k < 0.001 and re < 10000:
        lambda_result = lambda_blasius
        selected = "Blasius"
        flow_type = "hydraulisch glattes Rohr, Re < 100000"
    elif epsilon_k < 0.0002 and re < 100000:
        lambda_result = lambda_blasius
        selected = "Blasius"
        flow_type = "hydraulisch glattes Rohr, Re < 100000"
    elif epsilon_k < 0.00002 and re < 1000000:
        lambda_result = lambda_prandtl
        selected = "Prandtl"
        flow_type = "hydraulisch glattes Rohr, Re > 100000"
    elif epsilon_k < 0.00001:
        lambda_result = lambda_prandtl
        selected = "Prandtl"
        flow_type = "hydraulisch glattes Rohr, Re > 100000"
    else:
        lambda_result = lambda_colebrookwhite
        selected = "Colebrook-White"
        flow_type = "Übergangsbereich zwischen hydraulisch glatt und hydraulisch rau"
    overview = pd.DataFrame(
        [
            ("Fluid", fluid),
            ("Temperatur [°C]", round(temperature_c, 3)),
            ("Druck [bar]", round(pressure_bar, 5)),
            ("Innendurchmesser [mm]", round(diameter_mm, 4)),
            ("Strömungsgeschwindigkeit [m/s]", round(velocity_ms, 4)),
            ("Rohrauheit [mm]", round(roughness_mm, 6)),
            ("Kinematische Viskosität ν [m²/s]", nu),
            ("Reynolds-Zahl Re [-]", f"{re:.0f}"),
            ("Relative Rauheit k/d [-]", f"{epsilon_k:.2e}"),
            ("Berechnungsgrundlage", selected),
            ("Strömungstyp", flow_type),
            ("Rohrreibungszahl λ [-]", lambda_result),
        ],
        columns=["Parameter", "Wert"],
    )
    formulas = pd.DataFrame(
        [
            ("Hagen-Poiseuille", lambda_hagenpoiseulle, "laminare Strömung"),
            ("Blasius", lambda_blasius, "hydraulisch glattes Rohr, Re < 100000"),
            ("Nikuradse", lambda_nikuradse, "hydraulisch raues Rohr"),
            ("Prandtl", lambda_prandtl, "hydraulisch glattes Rohr, Re > 100000"),
            ("Colebrook-White", lambda_colebrookwhite, "Übergangsbereich zwischen hydraulisch glatt und hydraulisch rau"),
        ],
        columns=["Formel", "Rohrreibungszahl λ [-]", "Zuordnung"],
    )
    return overview, formulas


st.markdown(
    f"""
    <div style='display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; margin-bottom:0.2rem;'>
        <div style='font-size:3rem; font-weight:700; line-height:1.1;'>{APP_TITLE}</div>
        <div style='color:#9ca3af; font-size:1rem; line-height:1.1;'>{APP_VERSION}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Berechnung der Rohrreibungszahl auf Basis von Fluid, Temperatur, Druck, Geometrie und Strömungsgeschwindigkeit.")

left, right = st.columns([1, 1.2])

with left:
    fluid = st.text_input("Fluid", value="H2O")
    temperature_c = st.number_input("Temperatur [°C]", value=10.0, step=0.1)
    pressure_bar = st.number_input("Druck [bar]", value=1.01325, step=0.00001, format="%.5f")
    diameter_mm = st.number_input("Innendurchmesser [mm]", value=50.0, step=0.1)
    velocity_ms = st.number_input("Strömungsgeschwindigkeit [m/s]", value=2.0, step=0.1)
    roughness_mm = st.number_input("Rohrrauigkeit [mm]", value=0.0015, step=0.0001, format="%.4f")
    run = st.button("Berechnen", use_container_width=True)

with right:
    st.subheader("Ergebnis")
    if run:
        try:
            overview_df, formulas_df = calculate_lambda(fluid, float(temperature_c), float(pressure_bar), float(diameter_mm), float(velocity_ms), float(roughness_mm))
            st.dataframe(overview_df, use_container_width=True, hide_index=True)
            with st.expander("Formeln im Vergleich"):
                st.dataframe(formulas_df, use_container_width=True, hide_index=True)
            csv_export = pd.concat(
                [
                    overview_df.assign(Bereich="Ergebnis"),
                    formulas_df.rename(columns={"Formel": "Parameter", "Rohrreibungszahl λ [-]": "Wert"}).assign(Bereich="Formelvergleich"),
                ],
                ignore_index=True,
            )
            st.download_button(
                label="CSV herunterladen",
                data=csv_export.to_csv(index=False, sep=";").encode("utf-8"),
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
        f"""
Mit diesem Tool wird die **Rohrreibungszahl λ** auf Grundlage der übergebenen Stoff- und Strömungsdaten berechnet.

Dafür gibst du ein:
- **Fluid**,
- **Temperatur**,
- **Druck**,
- **Innendurchmesser**,
- **Strömungsgeschwindigkeit**,
- **Rohrauigkeit**.

Aus diesen Eingaben wird zunächst über **CoolProp** die kinematische Viskosität bestimmt. Anschließend wird daraus die **Reynolds-Zahl** berechnet und die Rohrreibungszahl mit mehreren Formeln bewertet.

Die App zeigt nicht nur die **Rohrreibungszahl λ**, sondern auch die **ausgewählte Berechnungsgrundlage** und den zugehörigen **Strömungstyp** an. So ist direkt erkennbar, ob der berechnete Wert einer laminaren Strömung, einem hydraulisch glatten Rohr, einem hydraulisch rauen Rohr oder dem Übergangsbereich zugeordnet wurde.

Berücksichtigt werden:
- Gesetz von **Hagen-Poiseuille**,
- Formel nach **Blasius**,
- Formel nach **Nikuradse**,
- Formel nach **Prandtl**,
- sowie **Colebrook-White**.

Über den Bereich **Formeln im Vergleich** kannst du zusätzlich die Werte aller berücksichtigten Gleichungen öffnen und direkt miteinander vergleichen.

Die Tabelle **Rohrrauheitswerte** unten hilft bei der Wahl plausibler Eingaben für die Rauheit k.

Repository:
[{REPO_URL}]({REPO_URL})
"""
    )
with st.expander("Rohrrauheitswerte"):
    st.caption("Orientierungswerte für die Eingabe von k [mm].")
    roughness_df = pd.DataFrame(ROUGHNESS_ROWS, columns=["Werkstoff und Rohrart", "Zustand der Rohre", "k [mm]"])
    st.dataframe(roughness_df, use_container_width=True, hide_index=True)
with st.expander("Moody-Diagramm"):
    st.caption("Zur Orientierung für Strömungsbereiche und relative Rauheit.")
    if os.path.exists(MOODY_IMAGE):
        st.image(MOODY_IMAGE, use_container_width=True)
    st.markdown(f"Quelle: [Wikipedia – Moody chart]({MOODY_SOURCE})")
