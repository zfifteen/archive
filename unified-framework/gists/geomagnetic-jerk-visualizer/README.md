# Geomagnetic Jerk Visualizer

**What is a Geomagnetic Jerk? Visualized through Derivatives.**

This script demonstrates the concept of geomagnetic jerks - sudden changes in Earth's magnetic field dynamics - using a 3-panel visualization that shows how derivatives reveal hidden patterns.

## Output

![Geomagnetic Jerk Visualization](geomagnetic_jerk_visualization.png)

## The Concept

A **geomagnetic jerk** is a sudden change in the secular variation (rate of change) of Earth's magnetic field. These events:

- Occur on annual to decadal timescales
- Provide insights into fluid motion in Earth's outer core
- Are becoming more frequent (2019-2020, 2021, 2022-2023)

### Why Derivatives Matter

| Panel | What it Shows | Visibility of Jerk |
|-------|--------------|--------------------|
| (a) Magnetic Field B(t) | Raw field values | Barely visible |
| (b) Secular Variation dB/dt | First derivative | **V-SHAPE reveals it!** |
| (c) Secular Acceleration d2B/dt2 | Second derivative | Step/spike signal |

## Usage

```bash
python geomagnetic_jerk_visualizer.py
```

## Requirements

```
numpy>=1.21.0
matplotlib>=3.4.0
scipy>=1.7.0
```

## Inspired By

- **S0 News** (Feb 1, 2026): "Solar Flares Surge to Life, Unstable Earth"
- **Khanyile et al. (2026)**: Modelling earth's magnetic field over southern Africa (Physics of the Earth and Planetary Interiors)
- **Khanyile & Nahayo (2024)**: Geomagnetic jerks observed in southern Africa between 2017-2023

## Key Finding

Earth appears to be entering a "constant state of jerkiness" - with multiple rapid secular variation events detected between 2018 and 2023, suggesting increasingly turbulent core dynamics.

## License

MIT License - Free to use, modify, and distribute with attribution.
