# CO2 Storage Geochemistry & Rock Physics Agent

An LLM agent (Gemini 2.5 Flash) for CO2 geological storage research. It drives validated PHREEQC geochemistry and carbonate rock physics simulations via tool calling, and interprets the results in natural language.

All numbers come from deterministic simulation tools — the agent never fabricates or estimates values. Every run logs the full tool-call trace for reproducibility.

---

## What you can ask

### CO2-Brine Geochemistry (no rock)

- **Solubility at a fixed state** — dissolved CO2 in brine at a specific temperature and pressure.
- **Solubility vs. pressure** — how dissolved CO2 varies across the full pressure range at fixed temperature.
- **Solubility vs. temperature** — how dissolved CO2 varies with temperature at fixed pressure.
- **Detailed solution properties** — ion activities, molar volumes, pH, density, ionic strength, osmotic coefficient, CO2 fugacity.

Available backends: `phreeqc_phreeqc`, `phreeqc_pitzer`, `phreeqc_pitzer_mod`, `duan_sun_2006`, `carbonex`.

### CO2-Brine-Rock Geochemistry (with minerals)

- **Mineral trapping at a fixed state** — CO2 dissolution and mineral equilibrium (precipitation / dissolution of carbonates, silicates, clays, and sulphides).
- **Mineral trapping vs. pressure / temperature** — how the mineral assemblage shifts along a P or T sweep.
- **Mineralogy and porosity change** — full post-reaction weight fractions and updated porosity. This is the preferred starting point for 4D seismic workflows.

Supported minerals: Calcite, Dolomite, Quartz, K-feldspar, Albite, Kaolinite, Illite, Chlorite, Siderite, Pyrite, Anhydrite.

Supported ions: Na+, Cl-, Mg+2, Ca+2, K+, SO4-2, HCO3-, CO3-2.

### Carbonate Rock Physics

- **Seismic state at one condition** — Vp, Vs, bulk density, acoustic impedance, Vp/Vs ratio, and elastic moduli at a given porosity, CO2 saturation, temperature, and pressure. Runs the full pipeline: VRH mineral average → Batzle-Wang fluid mix → Berryman DEM dry frame → Gassmann fluid substitution.
- **Saturation sweep** — Vp, Vs, and impedance curves as CO2 saturation varies from 0 to 1, including % change from the brine-saturated baseline.
- **4D seismic contrast** — ΔVp, ΔVs, Δdensity, ΔIp (absolute and %) between a pre-injection baseline and a post-injection monitor state. Porosity may differ between states to represent geochemical dissolution or precipitation.

---

## Key workflow: 4D seismic feasibility

The agent chains geochemistry into rock physics automatically:

1. Run PHREEQC equilibrium on the initial reservoir (no CO2) to get the pre-injection baseline mineralogy and porosity.
2. Run PHREEQC equilibrium with CO2 at reservoir pressure to get the post-injection mineralogy and porosity.
3. Feed both states into the rock physics pipeline to compute Vp / Vs / Ip and their 4D contrasts.

**Example prompt:** *"Given a carbonate reservoir at 80 °C and 20 MPa with a 1 mol/kg NaCl brine, 20 % porosity, and a mineralogy of 75 % calcite / 20 % quartz / 5 % dolomite — what is the expected 4D Vp change after CO2 injection?"*

---

## Units

| Quantity | Geochemistry tools | Rock physics tools |
|---|---|---|
| Temperature | Kelvin (K) | Celsius (°C) |
| Pressure | MPa | MPa |
| Salinity | ion molalities (mol/kg) | ppm by weight |
| Velocity | — | km/s |
| Acoustic impedance | — | MRayl |

The agent converts your inputs automatically and states any conversion it performs before calling a tool.

---

## Caveats

- **Seismic nonuniqueness:** A small free-gas CO2 saturation causes nearly the same Vp drop as a large one. The agent always reports ΔVs alongside ΔVp and flags this ambiguity.
- **Model assumptions:** The Berryman DEM and Gassmann equations assume isotropic, low-frequency, fluid-saturated pores. Results are screening-level estimates, not precise predictions; the agent will say so.
- **PHREEQC is required:** The geochemistry backend must be installed and on PATH with its standard databases.
