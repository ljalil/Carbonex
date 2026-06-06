"""
Chainlit entry point — CO2 storage geochemistry and rock physics agent.

Run with:  chainlit run main.py -w
"""

import chainlit as cl
from google import genai
from google.genai import types
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from agent.geochemistry_tools import (
    co2_brine_solubility_fixed,
    co2_brine_solubility_vs_pressure,
    co2_brine_solubility_vs_temperature,
    co2_brine_solution_properties,
    co2_brine_rock_fixed,
    co2_brine_rock_vs_pressure,
    co2_brine_rock_vs_temperature,
    compute_equilibrium_mineralogy_and_porosity,
)
from agent.rock_physics_tools import (
    carbonate_rock_seismic_state,
    carbonate_rock_saturation_sweep,
    carbonate_rock_4d_contrast,
    phreeqc_moles_to_rock_physics_inputs,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOLS = [
    # Geochemistry — CO2-brine (no rock)
    co2_brine_solubility_fixed,
    co2_brine_solubility_vs_pressure,
    co2_brine_solubility_vs_temperature,
    co2_brine_solution_properties,
    # Geochemistry — CO2-brine-rock (with minerals)
    co2_brine_rock_fixed,
    co2_brine_rock_vs_pressure,
    co2_brine_rock_vs_temperature,
    # Geochemistry — mineral equilibrium with explicit porosity tracking
    compute_equilibrium_mineralogy_and_porosity,
    # Rock physics — carbonate model
    carbonate_rock_seismic_state,
    carbonate_rock_saturation_sweep,
    carbonate_rock_4d_contrast,
    # Bridge: geochemistry output (moles) → rock physics input
    phreeqc_moles_to_rock_physics_inputs,
]

# ---------------------------------------------------------------------------
# System instruction
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = (
    "You are a geochemistry and rock-physics assistant for CO2 storage in saline aquifers. "
    "You run PHREEQC, Duan-Sun, and carbonate rock-physics simulations via the provided "
    "tools and interpret the results in natural language. "
    "\n\n"
    "UNIT RULES (non-negotiable): "
    "Geochemistry tools — temperature in Kelvin, pressure in MPa, ion molalities in mol/kg water. "
    "Rock physics tools — temperature in °C, pressure in MPa, salinity in ppm by weight. "
    "If the user gives °C/°F/K, bar, atm, or g/L, convert before calling a tool and state the conversion. "
    "\n\n"
    "INPUT FORMAT: Ion and mineral molality inputs are JSON object strings "
    "(e.g. '{\"Na+\": 1.0, \"Cl-\": 1.0}'). Mineralogy for rock physics is also a "
    "JSON object string of weight fractions (e.g. '{\"calcite\": 0.88, \"quartz\": 0.07}'). "
    "\n\n"
    "WORKFLOW GUIDANCE: "
    "For pure CO2-brine solubility use the co2_brine_* tools. "
    "When rock mineralogy is specified use co2_brine_rock_* tools. "
    "For seismic / 4D feasibility use the carbonate_rock_* tools. "
    "\n\n"
    "PREFERRED CHAINED WORKFLOW when the user provides mineralogy as weight fractions + porosity "
    "and asks about porosity change, geochemical change, or seismic properties after CO2 injection: "
    "1. Call compute_equilibrium_mineralogy_and_porosity(with_co2=False) for the pre-injection "
    "equilibrium state. "
    "2. Call compute_equilibrium_mineralogy_and_porosity(with_co2=True) for the post-injection "
    "state. "
    "3. Pass the returned 'mineralogy_wt_post' and 'porosity_post' directly to "
    "carbonate_rock_seismic_state for post-injection Vp/Vs. "
    "Use porosity_change from the tool output — never compute it yourself. "
    "\n\n"
    "LEGACY WORKFLOW (still valid when the user provides mineral moles directly): "
    "run co2_brine_rock_fixed, then call phreeqc_moles_to_rock_physics_inputs to convert "
    "the ABSOLUTE moles (initial + delta) to weight fractions and porosity, then call "
    "carbonate_rock_seismic_state. "
    "\n\n"
    "INTEGRITY RULES: "
    "Never fabricate or estimate numerical results — only report values returned by tools. "
    "If a tool returns an error, report it plainly. "
    "The seismic CO2 response is nonunique: always state that a small free-gas saturation "
    "causes nearly the same Vp drop as a large one, and report ΔVs alongside ΔVp. "
    "State any unit conversions you performed before quoting a result."
)

# ---------------------------------------------------------------------------
# Gemini client and config
# ---------------------------------------------------------------------------

_client = genai.Client(http_options={"api_version": "v1alpha"})

_config = types.GenerateContentConfig(
    tools=TOOLS,
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.0,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        maximum_remote_calls=20
    ),
)

# ---------------------------------------------------------------------------
# Chainlit message handler
# ---------------------------------------------------------------------------

@cl.set_starter_categories
async def starter_categories():
    return [
        cl.StarterCategory(
            label="About this agent",
            starters=[
                cl.Starter(
                    label="What can you do?",
                    message="What simulations can you run? Give me a brief overview of your capabilities and the kinds of questions I can ask.",
                ),
                cl.Starter(
                    label="What inputs do I need?",
                    message="What inputs do I need to provide for a typical CO2 storage simulation? Walk me through the key parameters.",
                ),
            ],
        ),
        cl.StarterCategory(
            label="CO2-brine geochemistry",
            starters=[
                cl.Starter(
                    label="CO2 solubility at reservoir conditions",
                    message="What is the CO2 solubility in a 1 mol/kg NaCl brine at 60°C and 15 MPa? Use the PHREEQC Pitzer model.",
                ),
                cl.Starter(
                    label="Solubility vs. pressure sweep",
                    message="How does CO2 solubility change with pressure (5–30 MPa) in a 1 mol/kg NaCl brine at 80°C? Use the Duan-Sun 2006 model.",
                ),
                cl.Starter(
                    label="Brine solution properties",
                    message="What are the density and pH of a brine with Na+ 0.5 mol/kg, Cl- 0.5 mol/kg at 50°C and 10 MPa after CO2 equilibration?",
                ),
            ],
        ),
        cl.StarterCategory(
            label="CO2-brine-rock reactions",
            starters=[
                cl.Starter(
                    label="Mineral dissolution after CO2 injection",
                    message="Simulate CO2-brine-rock equilibrium at 60°C and 12 MPa for a brine with Na+ 1 mol/kg, Cl- 1 mol/kg in contact with calcite (1 mol) and quartz (5 mol). Use the phreeqc database.",
                ),
                cl.Starter(
                    label="Mineral reaction vs. pressure",
                    message="How do calcite and dolomite dissolution change as CO2 injection pressure increases from 5 to 25 MPa at 70°C? Brine: Na+ 0.8, Cl- 0.8 mol/kg. Minerals: Calcite 1 mol, Dolomite 0.5 mol.",
                ),
                cl.Starter(
                    label="Porosity change from mineral reactions",
                    message="Estimate the porosity change after CO2 injection at 60°C, 15 MPa. Mineralogy: calcite 0.80, quartz 0.10, dolomite 0.10 weight fractions. Initial porosity: 0.25. Brine: Na+ 1 mol/kg, Cl- 1 mol/kg.",
                ),
            ],
        ),
        cl.StarterCategory(
            label="Rock physics & seismic",
            starters=[
                cl.Starter(
                    label="Seismic velocities for a carbonate",
                    message="Calculate Vp and Vs for a carbonate rock with 80% calcite, 10% quartz, 10% dolomite (weight fractions), porosity 0.20, aspect ratio 0.15, at 60°C, 15 MPa, 30,000 ppm salinity, and 0.5 CO2 saturation.",
                ),
                cl.Starter(
                    label="CO2 saturation sweep",
                    message="How do Vp, Vs, and acoustic impedance change as CO2 saturation increases from 0 to 1 in a carbonate with 85% calcite, 15% quartz, porosity 0.18, aspect ratio 0.12, at 70°C, 20 MPa, 50,000 ppm salinity?",
                ),
                cl.Starter(
                    label="4D seismic feasibility",
                    message="Estimate the 4D seismic contrast (ΔVp, ΔVs, ΔIp) between baseline (no CO2) and post-injection (CO2 saturation 0.3) for a carbonate: 80% calcite, 10% quartz, 10% dolomite, porosity 0.22, AR 0.15, 65°C, 18 MPa, 40,000 ppm salinity.",
                ),
            ],
        ),
        cl.StarterCategory(
            label="Full CO2 storage workflow",
            starters=[
                cl.Starter(
                    label="Geochemistry → seismic (chained)",
                    message="Run a full workflow: start from mineralogy (calcite 0.80, quartz 0.10, dolomite 0.10 weight fractions, porosity 0.22) and brine (Na+ 1 mol/kg, Cl- 1 mol/kg) at 60°C, 15 MPa. Compute pre- and post-CO2 injection mineral equilibrium, then calculate the seismic velocity change (Vp, Vs, Ip) for the post-injection state with CO2 saturation 0.4.",
                ),
                cl.Starter(
                    label="Seismic nonuniqueness: saturation vs. pressure",
                    message="Illustrate the nonuniqueness problem: compare the Vp drop caused by 5% free CO2 saturation vs. a 3 MPa pore-pressure increase in a carbonate with 80% calcite, 15% quartz, 5% dolomite, porosity 0.20, AR 0.15, 65°C, 20 MPa baseline, 35,000 ppm salinity.",
                ),
            ],
        ),
    ]


@cl.on_message
async def on_message(message: cl.Message) -> None:
    response = await _client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=message.content,
        config=_config,
    )
    for turn in response.automatic_function_calling_history:
        for part in turn.parts:
            if part.function_call:
                print(f"[CALL] {part.function_call.name}({dict(part.function_call.args)})")
    await cl.Message(content=response.text).send()
