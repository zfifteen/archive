## 3. The Joukowski Connection

### 3.1 The Joukowski Transform

The Joukowski (Zhukovsky) transformation is the conformal map[^4][^43]:

\[
w = z + \frac{1}{z} \quad (4)
\]

For \(z = Re^{i\theta}\) on a circle of radius \(R > 1\):

\[
w = Re^{i\theta} + \frac{1}{R}e^{-i\theta} \quad (5)
\]

This is structurally identical to Equation (1) with \(R_+ = R\) and \(R_- = 1/R\). The image is an ellipse with semi-axes \(a = R + 1/R\) and \(b = R - 1/R\)[^105]. The unit circle (\(R = 1\)) maps to the degenerate line segment \([-2, 2]\), and circles with \(R > 1\) map to progressively rounder ellipses.

### 3.2 The Joukowski Radius of a Semiprime

For the factoring ellipse with \(R_+ = n\) and \(R_- = m\), we can write:

\[
z(\theta) = \sqrt{nm}\left[\sqrt{\frac{n}{m}}\,e^{i\theta} + \sqrt{\frac{m}{n}}\,e^{-i\theta}\right] = \sqrt{nm}\left[\mathcal{R}\,e^{i\theta} + \frac{1}{\mathcal{R}}\,e^{-i\theta}\right] \quad (6)
\]

where \(\mathcal{R} = \sqrt{n/m}\) is the *Joukowski radius* of the semiprime. The scale factor is \(\sqrt{nm}\). This means the factoring ellipse is a scaled Joukowski image of the circle \(|z| = \mathcal{R}\).

The Joukowski radius encodes the factor ratio through:

\[
\frac{\mathcal{R}^2 + 1}{\mathcal{R}^2 - 1} = \frac{n/m + 1}{n/m - 1} = \frac{n+m}{n-m} = \frac{q}{p} \quad (7)
\]

### 3.3 Hyperbolic Parametrization

Defining \(u = \ln(\mathcal{R})\), we obtain:

\[
\tanh(u) = \frac{\mathcal{R}^2 - 1}{\mathcal{R}^2 + 1} = \frac{p}{q}, \quad \coth(u) = \frac{q}{p} \quad (8)
\]

Factor recovery is immediate:

\[
p = \sqrt{N \cdot \tanh(u)}, \quad q = \sqrt{N / \tanh(u)} \quad (9)
\]

The factoring problem reduces to determining \(u\) (or equivalently \(\mathcal{R}\)) such that both expressions yield prime integers.