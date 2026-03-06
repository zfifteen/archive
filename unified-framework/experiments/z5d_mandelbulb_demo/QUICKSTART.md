# Quick Start Guide

Get the Z5D Mandelbulb demo running in 60 seconds.

## Option 1: Browser Demo (Fastest)

1. **Open the demo directly:**
   ```bash
   cd experiments/z5d_mandelbulb_demo
   python serve_demo.py
   ```

2. **Your browser opens automatically to:**
   ```
   http://localhost:8000/mandelbulb_demo.html
   ```

3. **Controls:**
   - **Left mouse drag:** Rotate camera
   - **Mouse wheel:** Zoom in/out
   - **Right mouse drag:** Pan camera
   - **P key:** Cycle Mandelbulb power (8 → 12 → 16 → 20)
   - **G key:** Toggle Z5D curvature on/off
   - **F key:** Toggle FPS counter
   - **H key:** Hide UI

4. **What to look for:**
   - FPS counter (top right) should show 60+ fps
   - Toggle Z5D off/on to see performance difference
   - Higher powers (16, 20) still run smoothly with Z5D

## Option 2: Run Python Benchmarks

1. **Quick test:**
   ```bash
   cd experiments/z5d_mandelbulb_demo
   python z5d_curvature.py test
   ```
   
   Output shows speedup: "Z5D: 44 iterations, Standard: 61 iterations, Speedup: 1.39×"

2. **Full benchmark (1000 rays):**
   ```bash
   python z5d_curvature.py benchmark 1000
   ```
   
   Generates `benchmark_results.json` with detailed statistics

3. **Comprehensive suite:**
   ```bash
   cd benchmarks
   python performance_benchmark.py 500
   ```
   
   Tests power scaling, resolution scaling, geodesic multiplier tuning, and curvature distribution

## Option 3: Generate Visualizations

```bash
cd experiments/z5d_mandelbulb_demo/benchmarks
python visualize_curvature.py
```

Creates three PNG images in `../screenshots/`:
- `curvature_slice.png` - 2D slice of curvature field
- `curvature_comparison.png` - Multi-slice comparison
- `step_size_analysis.png` - Performance analysis charts

## Option 4: Integration Example

```bash
cd experiments/z5d_mandelbulb_demo
python integration_example.py
```

Runs four examples showing:
1. Basic ray-marching usage
2. Z5D vs standard comparison
3. Adaptive level-of-detail
4. Batch rendering with statistics

## Verify Installation

**Required:**
- Python 3.8+
- numpy
- matplotlib (for visualizations)
- scipy (for benchmarks)

**Install missing dependencies:**
```bash
pip install numpy matplotlib scipy
```

**Browser requirements:**
- Chrome 113+ (recommended)
- Safari 17+
- Firefox 122+ (enable WebGPU in about:config)

## Expected Results

### Browser Demo
- Smooth 60+ fps rendering at 1080p
- Interactive rotation and zoom
- Real-time power adjustment
- Visible FPS improvement when Z5D is enabled

### Python Benchmarks
- 1.4-1.6× speedup across all powers
- 100% hit rate maintained
- Consistent performance

### Visualizations
- Clear curvature field patterns
- Step size distribution showing geodesic leaps
- Multi-slice view of spatial complexity

## Troubleshooting

**Browser demo not loading?**
- Check console for WebGL errors
- Try a different browser
- Ensure JavaScript is enabled

**Python errors?**
- Install missing packages: `pip install numpy scipy matplotlib`
- Check Python version: `python --version` (need 3.8+)

**Slow performance in browser?**
- Lower internal resolution in demo
- Reduce geodesic multiplier to 5
- Try a different browser (Chrome performs best)

**Visualizations not generating?**
- Install matplotlib: `pip install matplotlib`
- Check write permissions in screenshots/ directory

## Next Steps

1. **Explore the code:** Start with `z5d_curvature.py` for the core algorithm
2. **Read the docs:** `README.md` has comprehensive technical details
3. **Modify parameters:** Try different geodesic multipliers (5-20)
4. **Integrate:** Use `integration_example.py` as a template
5. **Share results:** Take screenshots and compare with standard ray-marching

## File Overview

```
experiments/z5d_mandelbulb_demo/
├── QUICKSTART.md              ← You are here
├── README.md                  ← Full documentation
├── IMPLEMENTATION_SUMMARY.md  ← Technical details
├── mandelbulb_demo.html       ← Browser demo
├── z5d_curvature.py           ← Core Python API
├── integration_example.py     ← Usage examples
└── benchmarks/                ← Validation tools
```

## One-Line Demo

```bash
cd experiments/z5d_mandelbulb_demo && python serve_demo.py
```

That's it! The demo opens in your browser automatically. Drag to rotate, scroll to zoom, press P to change power.

---

**Questions?** See [README.md](README.md) for detailed documentation.

**Issues?** Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details.
