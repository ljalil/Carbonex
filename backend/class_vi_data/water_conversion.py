# Density estimate from mineral composition using partial molar volumes
# Method: mass balance + partial molar volume approximation

# Typical partial molar volumes at 25 °C in cm^3/mol (literature averages)
partial_molar_volumes = {
    "Na+": 16.6,
    "K+": 25.0,
    "Ca2+": -24.4,
    "Mg2+": -19.6,
    "Cl-": 16.6,
    "SO4^2-": -20.1,
    "HCO3-": 28.5,
    "CO3^2-": 41.5,
}

# Molar masses in g/mol
molar_masses = {
    "Na+": 22.99,
    "K+": 39.10,
    "Ca2+": 40.08,
    "Mg2+": 24.31,
    "Cl-": 35.45,
    "SO4^2-": 96.06,
    "HCO3-": 61.02,
    "CO3^2-": 60.01,
}

def solution_density(concentrations_mgL, T_C=25.0):
    """
    Estimate solution density from ion concentrations.
    Returns density in g/cm^3
    """
    rho_w = 0.99987 + 6.69e-5 * T_C - 8.0e-6 * T_C**2
    m_w = rho_w * 1000.0
    n_w = m_w / 18.015
    V_w = n_w * 18.015

    m_s = 0.0
    V_s = 0.0
    for ion, conc_mgL in concentrations_mgL.items():
        if ion not in molar_masses or ion not in partial_molar_volumes:
            raise ValueError(f"Missing data for ion {ion}")
        M = molar_masses[ion]
        Vm = partial_molar_volumes[ion]
        n_i = (conc_mgL / 1000.0) / M  # mol/L
        m_i = n_i * M
        V_i = n_i * Vm
        m_s += m_i
        V_s += V_i

    m_total = m_w + m_s
    V_total = V_w + V_s
    rho = m_total / V_total
    return rho

def mgL_to_molarity(concentrations_mgL):
    """mg/L -> mol/L"""
    molarities = {}
    for ion, conc_mgL in concentrations_mgL.items():
        M = molar_masses[ion]
        molarities[ion] = (conc_mgL / 1000.0) / M
    return molarities

def molarity_to_mgL(concentrations_molL):
    """mol/L -> mg/L"""
    mgL = {}
    for ion, conc_molL in concentrations_molL.items():
        M = molar_masses[ion]
        mgL[ion] = conc_molL * M * 1000.0
    return mgL

def mgL_to_molality(concentrations_mgL, T_C=25.0):
    """
    mg/L -> mol/kg water
    """
    rho = solution_density(concentrations_mgL, T_C)
    rho_gL = rho * 1000.0
    m_solutes = sum(conc_mgL / 1000.0 for conc_mgL in concentrations_mgL.values())
    m_water = rho_gL - m_solutes
    kg_water = m_water / 1000.0

    molalities = {}
    for ion, conc_mgL in concentrations_mgL.items():
        M = molar_masses[ion]
        n_i = (conc_mgL / 1000.0) / M
        b_i = n_i / kg_water
        molalities[ion] = b_i
    return molalities

def molality_to_molarity(concentrations_molkg, T_C=25.0):
    """
    mol/kg water -> mol/L solution
    Approximate using density estimate reconstructed from mg/L.
    """
    # First get mg/L equivalent from molality by assuming 1 kg water
    concentrations_mgL = {}
    for ion, b in concentrations_molkg.items():
        M = molar_masses[ion]
        # assume 1 kg water → 1000 g → 1000 mL ~ 1 L
        n_i = b * 1.0  # mol
        mass_i = n_i * M  # g
        conc_mgL = mass_i * 1000.0 / 1.0  # mg/L approx
        concentrations_mgL[ion] = conc_mgL
    return mgL_to_molarity(concentrations_mgL)

def molarity_to_molality(concentrations_molL, T_C=25.0):
    """
    mol/L -> mol/kg water
    """
    # Convert mol/L to mg/L first
    concentrations_mgL = molarity_to_mgL(concentrations_molL)
    return mgL_to_molality(concentrations_mgL, T_C)

# Example usage
if __name__ == "__main__":
    concentrations = {
        "Na+": 500.0,
        "Cl-": 800.0,
        "Ca2+": 200.0,
        "Mg2+": 100.0,
        "SO4^2-": 300.0,
        "HCO3-": 150.0,
    }
    rho = solution_density(concentrations, T_C=25)
    print(f"Estimated density: {rho:.5f} g/cm^3")

    molarities = mgL_to_molarity(concentrations)
    print("\nMolarity (mol/L):")
    for ion, c in molarities.items():
        print(f"{ion}: {c:.6f}")

    molalities = mgL_to_molality(concentrations, T_C=25)
    print("\nMolality (mol/kg water):")
    for ion, b in molalities.items():
        print(f"{ion}: {b:.6f}")
