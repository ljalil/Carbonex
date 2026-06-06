"""
CLI / programmatic entry point (non-chainlit usage).

For the Chainlit UI, run:  chainlit run main.py -w
"""

import asyncio
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

TOOLS = [
    co2_brine_solubility_fixed,
    co2_brine_solubility_vs_pressure,
    co2_brine_solubility_vs_temperature,
    co2_brine_solution_properties,
    co2_brine_rock_fixed,
    co2_brine_rock_vs_pressure,
    co2_brine_rock_vs_temperature,
    compute_equilibrium_mineralogy_and_porosity,
    carbonate_rock_seismic_state,
    carbonate_rock_saturation_sweep,
    carbonate_rock_4d_contrast,
    phreeqc_moles_to_rock_physics_inputs,
]

_client = genai.Client(http_options={"api_version": "v1alpha"})

_SYSTEM_INSTRUCTION = (
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

_config = types.GenerateContentConfig(
    tools=TOOLS,
    system_instruction=_SYSTEM_INSTRUCTION,
    temperature=0.0,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        maximum_remote_calls=20
    ),
)


def run_agent(prompt: str, model: str = "gemini-2.5-flash") -> str:

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

    elements = [
        cl.Pyplot(name="plot", figure=fig, display="inline"),
    ]
    await cl.Message(
        content="Here is a simple plot",
        elements=elements,
    ).send()

    async def _run() -> str:
        response = await _client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=_config,
        )
        for turn in response.automatic_function_calling_history:
            for part in turn.parts:
                if part.function_call:
                    print(f"[CALL] {part.function_call.name}({dict(part.function_call.args)})")
        return response.text

    return asyncio.run(_run())
