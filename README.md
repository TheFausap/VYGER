# 🛰️ VYGER — Deep Space Probe Mission Simulator

> *JPL Deep Space Network — Probe Mission Simulator*
> *Jet Propulsion Laboratory / California Inst. of Technology — 1977*

A retro-styled, terminal-aesthetic space probe simulator written in Python. Pilot a Voyager-inspired spacecraft through the solar system and beyond — scanning, analyzing, and cataloguing celestial objects as you navigate ever deeper into interstellar space. Features real NASA exoplanet data, physics-based procedural generation, and gravity-assist slingshot maneuvers.

---

## ✨ Features

### 🌌 Core Gameplay

- **Sector-by-sector deep space navigation** with realistic transit times and AU distances
- **Multi-step object investigation**: Detect → Scan → Analyze → Catalogue
- **Gravity-assist slingshot maneuvers** based on simplified Oberth effect physics
- **Resource management**: RTG power, RCS fuel, and DSN signal strength degrade over time
- **Data burst transmissions** back to JPL with realistic light-delay calculations

### 🔬 Physics & Science

- **Physics-based procedural generation** of celestial objects (planets, asteroids, comets, moons, KBOs)
  - Equilibrium temperature follows Stefan–Boltzmann scaling: `T ∝ d^(-0.5)`
  - Composition transitions at the snow line (~4 AU)
  - Mass–radius relations for each body class
  - Region-dependent type probability distributions
- **Real NASA exoplanet data** fetched live from the [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) TAP service
  - ~50 embedded confirmed exoplanets as instant fallback
  - Background thread silently upgrades the pool once the live database loads
  - ~25% chance of encountering a real confirmed exoplanet during navigation
- **Slingshot delta-v formula**: `Δv = 1.3 · √(M/r) · mag_bonus` — calibrated so Jupiter (318 M⊕) at 5 AU gives ≈12 km/s, consistent with Voyager 1's actual Jupiter flyby gain

### 🖥️ Interface

- **Retro green phosphor CRT aesthetic** (Tkinter GUI)
- **ASCII spacecraft & celestial body artwork** rendered on a starfield canvas with nebulae
- **Real-time telemetry panel** showing probe status, resources, and mission statistics
- **Scrollable terminal** with color-coded output (amber headers, green data, red errors, orange warnings)
- **Command history** with up/down arrow key navigation
- **Animated boot sequence** mimicking vintage JPL mission control diagnostics

---

## 📋 Requirements

- **Python 3.6+**
- **Tkinter** (included with most Python installations)
- No external dependencies — uses only the Python standard library (`tkinter`, `urllib`, `json`, `math`, `random`, `threading`)

### Installing Tkinter (if not already available)

```bash
# Debian / Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk

# macOS (via Homebrew)
brew install python-tk
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/TheFausap/VYGER.git
cd VYGER
python3 voyager_sim.py
```

The simulator will boot up with a diagnostic sequence, then you're ready to explore. Type `N` or `NAVIGATE` to begin your mission.

---

## 🎮 Commands

| Command | Shortcut | Description |
| ------- | -------- | ----------- |
| `NAVIGATE` | `NAV`, `N` | Advance probe to the next sector |
| `SCAN` | `SC` | Wide-field sensor sweep of detected object |
| `ANALYZE` | `AN` | Deep spectral and composition analysis |
| `SLINGSHOT` | `SL` | Gravity-assist maneuver (requires analysis, mass ≥ 0.5 M⊕) |
| `CATALOGUE` | `CAT` | Log analyzed object to mission record |
| `STATUS` | `ST` | Full probe telemetry report |
| `LOG` | `L` | View mission object catalogue |
| `TRANSMIT` | `TX` | Send data burst to Earth via DSN |
| `CLEAR` | `CLS` | Clear terminal display |
| `QUIT` | `Q`, `EXIT` | Terminate mission |
| `HELP` | `H` | Show command list |

### Typical Mission Workflow

```text
N → SC → AN → CAT → TX
(navigate, investigate, catalogue, transmit)

N → SC → AN → SL
(navigate, investigate, slingshot for speed boost)
```

---

## 🌍 Space Regions

As the probe travels farther from the Sun, it passes through distinct regions:

| Distance (AU) | Region |
| --- | --- |
| 0 – 2 | Inner Solar System |
| 2 – 5 | Asteroid Belt Region |
| 5 – 10 | Outer Solar System |
| 10 – 20 | Gas Giant Region |
| 20 – 50 | Kuiper Belt Region |
| 50 – 100 | Heliosphere Boundary |
| 100+ | Interstellar Space |

Object types and compositions shift realistically as you travel through these regions — expect more rocky planets and asteroids near the inner system, gas and ice giants in the outer system, and trans-Neptunian objects beyond the Kuiper Belt.

---

## 🏗️ Architecture

```text
VYGER/
├── voyager_sim.py      # v2.0 — current version (physics engine + NASA exoplanet data)
├── voyager_sim_v1.py   # v1.0 — original version (random generation, no live data)
├── LICENSE             # GNU GPL v3
└── README.md
```

### Key Classes (v2.0)

| Class | Purpose |
| ----- | ------- |
| `PhysicsGen` | Physics-based procedural object generation (temperature, composition, mass–radius scaling) |
| `ExoplanetDB` | Loads real exoplanet data from the NASA Exoplanet Archive TAP API with embedded fallback |
| `ProbeState` | Probe telemetry, resource tracking, navigation, encounter spawning, slingshot physics |
| `VoyagerApp` | Tkinter GUI — canvas rendering, terminal I/O, command dispatch, boot sequence |

### v1.0 → v2.0 Changelog

| Feature | v1.0 | v2.0 |
| ------- | ----- | ---- |
| Object generation | Random | Physics-based (Stefan–Boltzmann, mass–radius, region weighting) |
| Celestial data | Static name pools | NASA Exoplanet Archive live + embedded fallback |
| Slingshot maneuver | — | ✅ Gravity-assist with Oberth-effect Δv |
| Radiation damage | — | ✅ Close flyby risk during slingshots |
| Quit command | — | ✅ |
| Exoplanet DB panel | — | ✅ Real-time status display |

---

## 📡 NASA Exoplanet Archive Integration

The simulator queries the [NASA Exoplanet Archive TAP service](https://exoplanetarchive.ipac.caltech.edu/) for confirmed exoplanet parameters:

- **Planet name**, **mass** (Earth masses), **radius** (Earth radii), **equilibrium temperature** (K), **orbital semi-major axis** (AU)

This happens in a background thread at startup. If the network is unavailable, the simulator instantly falls back to a curated embedded catalogue of ~50 confirmed exoplanets (51 Pegasi b, TRAPPIST-1 system, Proxima Centauri b, Kepler-452b, etc.).

The telemetry panel shows the current database status:

- `EMBEDDED (N)` — using built-in catalogue
- `NASA (N)` — live data loaded successfully
- `OFFLINE — EMBEDDED ACTIVE` — network fetch failed, using fallback

---

## ⚙️ Slingshot Physics

The gravity-assist mechanic is modeled on simplified Oberth-effect dynamics:

```text
Δv = 1.3 · √(M / r) · mag_bonus

where:
  M         = object mass in Earth masses (M⊕)
  r         = periapsis distance (AU)
  mag_bonus = 1.15 if magnetic field detected, else 1.0
  Δv capped at 28 km/s
```

- **Fuel cost**: `1.5% + M/400%` for precision periapsis correction burns
- **Minimum mass**: 0.5 M⊕ required for viable trajectory assist
- **Radiation risk**: Objects with >400 rads/hr may damage RTG power output during close flyby
- **Calibration**: Jupiter-class (318 M⊕) at 5 AU yields ≈12 km/s, matching Voyager 1's real Jupiter flyby

---

## 📜 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

---

*Ad astra per aspera* 🌟
