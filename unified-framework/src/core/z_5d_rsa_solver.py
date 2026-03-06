# Import Z5D components
try:
    from .z_5d_enhanced import z5d_predictor
    from ..experiments.z5d_semiprime_prediction.z5d_semiprime_predictor import baseline_semiprime_enhanced
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from z_5d_enhanced import z5d_predictor
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'experiments', 'z5d_semiprime_prediction'))
    from z5d_semiprime_predictor import baseline_semiprime_enhanced