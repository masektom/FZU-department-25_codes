# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:01:27 2026

@author: tmase
"""

# -*- coding: utf-8 -*-
# Výpočet XRD spekter - Miller indices, d-spacing, and 2θ angles
# Supports multiple crystal lattice systems

import numpy as np
import math as mt
import os

CuKa = 1.54184  # Å - Cu Kα X-ray wavelength


def _write_results(planes: list[tuple], directory: str, filename: str) -> None:
    """Write computed planes to a .txt file in the given directory."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("rovina, d_space [Å], 2theta [°]\n")
        for label, d, two_theta in planes:
            line = f"{label}, {d}, {two_theta}"
            print(line)
            f.write(line + "\n")
    print(f"\nSoubor uložen: {filepath}")


def _theta_from_d(d: float) -> float | None:
    """Calculate 2θ (degrees) from d-spacing using Bragg's law. Returns None if unphysical."""
    arg = CuKa / (2 * d)
    if abs(arg) > 1:
        return None
    return round(mt.degrees(2 * mt.asin(arg)), 2)


# ---------------------------------------------------------------------------
# Tetragonal  (a = b ≠ c, α = β = γ = 90°)
# Formula: 1/d² = (h²+k²)/a² + l²/c²
# ---------------------------------------------------------------------------

def Tetragonal(a: float, c: float, directory: str, number: int, filename: str = "Tetragonal_XRD.txt") -> None:
    """
    Calculate XRD planes for a tetragonal lattice.

    Parameters
    ----------
    a         : lattice parameter a (= b) in Å
    c         : lattice parameter c in Å
    directory : output directory path
    number    : maximum Miller index (h, k, l each run 0 … number)
    filename  : output filename (default: Tetragonal_XRD.txt)
    """
    planes = []
    for h in range(number + 1):
        for k in range(h + 1):          # k ≤ h avoids duplicate planes
            for l in range(number + 1):
                if h == k == l == 0:
                    continue
                d = round(1 / np.sqrt((h**2 + k**2) / a**2 + l**2 / c**2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


# ---------------------------------------------------------------------------
# Cubic  (a = b = c, α = β = γ = 90°)
# Formula: 1/d² = (h²+k²+l²)/a²
# ---------------------------------------------------------------------------

def Cubic(a: float, directory: str, number: int, filename: str = "Cubic_XRD.txt") -> None:
    """
    Calculate XRD planes for a cubic lattice.

    Parameters
    ----------
    a         : lattice parameter a in Å
    directory : output directory path
    number    : maximum Miller index
    filename  : output filename (default: Cubic_XRD.txt)
    """
    planes = []
    for h in range(number + 1):
        for k in range(h + 1):
            for l in range(k + 1):      # l ≤ k ≤ h avoids duplicates
                if h == k == l == 0:
                    continue
                d = round(a / np.sqrt(h**2 + k**2 + l**2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


# ---------------------------------------------------------------------------
# Orthorhombic  (a ≠ b ≠ c, α = β = γ = 90°)
# Formula: 1/d² = h²/a² + k²/b² + l²/c²
# ---------------------------------------------------------------------------

def Orthorhombic(a: float, b: float, c: float, directory: str, number: int, filename: str = "Orthorhombic_XRD.txt") -> None:
    """
    Calculate XRD planes for an orthorhombic lattice.

    Parameters
    ----------
    a, b, c   : lattice parameters in Å
    directory : output directory path
    number    : maximum Miller index
    filename  : output filename (default: Orthorhombic_XRD.txt)
    """
    planes = []
    for h in range(number + 1):
        for k in range(number + 1):
            for l in range(number + 1):
                if h == k == l == 0:
                    continue
                d = round(1 / np.sqrt(h**2 / a**2 + k**2 / b**2 + l**2 / c**2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


# ---------------------------------------------------------------------------
# Hexagonal  (a = b ≠ c, α = β = 90°, γ = 120°)
# Formula: 1/d² = (4/3)(h²+hk+k²)/a² + l²/c²
# ---------------------------------------------------------------------------

def Hexagonal(a: float, c: float, directory: str, number: int, filename: str = "Hexagonal_XRD.txt") -> None:
    """
    Calculate XRD planes for a hexagonal lattice.

    Parameters
    ----------
    a         : lattice parameter a (= b) in Å
    c         : lattice parameter c in Å
    directory : output directory path
    number    : maximum Miller index
    filename  : output filename (default: Hexagonal_XRD.txt)
    """
    planes = []
    for h in range(number + 1):
        for k in range(number + 1):
            for l in range(number + 1):
                if h == k == l == 0:
                    continue
                d = round(1 / np.sqrt((4 / 3) * (h**2 + h*k + k**2) / a**2 + l**2 / c**2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


# ---------------------------------------------------------------------------
# Monoclinic  (a ≠ b ≠ c, α = γ = 90°, β ≠ 90°)
# Formula: 1/d² = (1/sin²β)(h²/a² + k²sin²β/b² + l²/c² - 2hl·cosβ/(ac))
# ---------------------------------------------------------------------------

def Monoclinic(a: float, b: float, c: float, beta_deg: float, directory: str, number: int, filename: str = "Monoclinic_XRD.txt") -> None:
    """
    Calculate XRD planes for a monoclinic lattice.

    Parameters
    ----------
    a, b, c   : lattice parameters in Å
    beta_deg  : monoclinic angle β in degrees
    directory : output directory path
    number    : maximum Miller index
    filename  : output filename (default: Monoclinic_XRD.txt)
    """
    beta = mt.radians(beta_deg)
    sin_b = mt.sin(beta)
    cos_b = mt.cos(beta)
    planes = []
    for h in range(number + 1):
        for k in range(number + 1):
            for l in range(number + 1):
                if h == k == l == 0:
                    continue
                inv_d2 = (1 / sin_b**2) * (
                    h**2 / a**2
                    + k**2 * sin_b**2 / b**2
                    + l**2 / c**2
                    - 2 * h * l * cos_b / (a * c)
                )
                if inv_d2 <= 0:
                    continue
                d = round(1 / np.sqrt(inv_d2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


def Rhombohedral(a: float, alpha_deg: float, directory: str, number: int, filename: str = "Rhombohedral_XRD.txt") -> None:
    """
    Calculate XRD planes for a Rhombohedral lattice.

    Parameters
    ----------
    a   : lattice parameters in Å
    alpha_deg  : Rhombohedral angle α in degrees
    directory : output directory path
    number    : maximum Miller index
    filename  : output filename (default: Rhombohedral_XRD.txt)
    """
    alpha = mt.radians(alpha_deg)
    sin_a = mt.sin(alpha)
    cos_a = mt.cos(alpha)
    planes = []
    for h in range(number + 1):
        for k in range(h + 1):
            for l in range(h + 1):
                if h == k == l == 0:
                    continue
                inv_d2 = (1/(a**2 * (1 - 3*cos_a**2 + 2*cos_a**3))) * ((h**2 + k**2 + l**2)*sin_a**2 + 2*(h*k + k*l + h*l)*(cos_a**2 - cos_a))
                if inv_d2 <= 0:
                    continue
                d = round(1 / np.sqrt(inv_d2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


# ---------------------------------------------------------------------------
# Triclinic  (a ≠ b ≠ c, α ≠ β ≠ γ ≠ 90°)
# General formula via the reciprocal metric tensor
# ---------------------------------------------------------------------------

def Triclinic(a: float, b: float, c: float,
              alpha_deg: float, beta_deg: float, gamma_deg: float,
              directory: str, number: int, filename: str = "Triclinic_XRD.txt") -> None:
    """
    Calculate XRD planes for a triclinic lattice.

    Parameters
    ----------
    a, b, c         : lattice parameters in Å
    alpha_deg       : angle α (between b and c) in degrees
    beta_deg        : angle β (between a and c) in degrees
    gamma_deg       : angle γ (between a and b) in degrees
    directory       : output directory path
    number          : maximum Miller index
    filename        : output filename (default: Triclinic_XRD.txt)
    """
    al = mt.radians(alpha_deg)
    be = mt.radians(beta_deg)
    ga = mt.radians(gamma_deg)

    # Unit-cell volume
    V = a * b * c * mt.sqrt(
        1 - mt.cos(al)**2 - mt.cos(be)**2 - mt.cos(ga)**2
        + 2 * mt.cos(al) * mt.cos(be) * mt.cos(ga)
    )

    # Reciprocal metric tensor components G*_ij
    S11 = (b * c * mt.sin(al))**2
    S22 = (a * c * mt.sin(be))**2
    S33 = (a * b * mt.sin(ga))**2
    S12 = a * b * c**2 * (mt.cos(al) * mt.cos(be) - mt.cos(ga))
    S13 = a * b**2 * c * (mt.cos(al) * mt.cos(ga) - mt.cos(be))
    S23 = a**2 * b * c * (mt.cos(be) * mt.cos(ga) - mt.cos(al))

    planes = []
    for h in range(number + 1):
        for k in range(number + 1):
            for l in range(number + 1):
                if h == k == l == 0:
                    continue
                inv_d2 = (S11 * h**2 + S22 * k**2 + S33 * l**2
                          + 2 * S12 * h * k + 2 * S13 * h * l + 2 * S23 * k * l) / V**2
                if inv_d2 <= 0:
                    continue
                d = round(1 / np.sqrt(inv_d2), 5)
                two_theta = _theta_from_d(d)
                if two_theta is None:
                    continue
                planes.append((f"({h}{k}{l})", d, two_theta))
    _write_results(planes, directory, filename)


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output_dir = r"C:\Škola\Škola_CVUT\Diplomová práce\Výsledky\XRD\test"

    # SnO - tetragonal
    Tetragonal(a=3.803, c=4.838, directory=output_dir, number=3, filename="SnO_XRD_test.txt")

    # SnO2 - tetragonal (uncomment to use)
    # Tetragonal(a=4.738, c=3.186, directory=output_dir, number=3, filename="SnO2_XRD.txt")

    # Other lattice examples:
    # Cubic(a=4.065, directory=output_dir, number=3, filename="Al_XRD.txt")
    # Hexagonal(a=3.21, c=5.21, directory=output_dir, number=3, filename="Ti_XRD.txt")
    # Orthorhombic(a=5.43, b=6.21, c=7.05, directory=output_dir, number=3, filename="Ortho_XRD.txt")
    # Monoclinic(a=5.43, b=6.21, c=7.05, beta_deg=110.5, directory=output_dir, number=3, filename="Mono_XRD.txt")
    # Triclinic(a=5.0, b=6.0, c=7.0, alpha_deg=80, beta_deg=85, gamma_deg=95, directory=output_dir, number=2, filename="Tri_XRD.txt")