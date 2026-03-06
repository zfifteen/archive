## 4. Conformal Anisotropy (Main Result)

### 4.1 Theorem 1: Joukowski Derivative Ratio

**Theorem.** *The ratio of the Joukowski derivative magnitudes at the minor-axis and major-axis endpoints of the factoring ellipse equals exactly \(q/p\).*  

**Proof.** The derivative of the Joukowski transform is:

\[
\frac{dw}{dz} = 1 - \frac{1}{z^2} \quad (10)
\]

On the circle \(z = \mathcal{R}e^{i\theta}\):

\[
\left|\frac{dw}{dz}\right|^2 = \left|1 - \frac{e^{-2i\theta}}{\mathcal{R}^2}\right|^2 = 1 - \frac{2\cos(2\theta)}{\mathcal{R}^2} + \frac{1}{\mathcal{R}^4} \quad (11)
\]

At \(\theta = 0\) (mapping to the major-axis endpoint \(w = q\)):

\[
\left|\frac{dw}{dz}\right|_{\theta=0} = \left|1 - \frac{1}{\mathcal{R}^2}\right| = \frac{\mathcal{R}^2 - 1}{\mathcal{R}^2} \quad (12)
\]

At \(\theta = \pi/2\) (mapping to the minor-axis endpoint \(w = ip\)):

\[
\left|\frac{dw}{dz}\right|_{\theta=\pi/2} = 1 + \frac{1}{\mathcal{R}^2} = \frac{\mathcal{R}^2 + 1}{\mathcal{R}^2} \quad (13)
\]

Their ratio:

\[
\frac{\left|\frac{dw}{dz}\right|_{\pi/2}}{\left|\frac{dw}{dz}\right|_0} = \frac{\mathcal{R}^2 + 1}{\mathcal{R}^2 - 1} = \frac{q}{p} \quad \blacksquare \quad (14)
\]

![](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/6491db48b0a9707d184efabb02ee441f/2d7befbb-9a9a-4412-93d8-6d60649bd568/644afcf8.png?AWSAccessKeyId=ASIA2F3EMEYEXZNGBIW7&Signature=rCsat8uPd8m72zcLUS1ug8MqGq8%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEL3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQDqcjCnvTbXg3zfE1lgVnFYPqcMsIOO%2FspxNrECqYa8bAIhAIwftuqprtvgtRhBE3%2Bpmut%2FZBGYPGZ7tMO%2B%2BSX4Z%2BrOKvwECIb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMNjk5NzUzMzA5NzA1IgyjzNC3J3op40fgkr4q0AS3bMD%2FCcknQzDerFaYG88OBsix0wraDsHVzLb0FNSxyWtqH8R%2FBXZmOTgNF3G3zEajtffM3l6%2FMwKKP9q8wM75gaNBcspgKJVip9QEtEM9VbrX4XvPgbRgO1kh2IkT79BUEtCDK5exaMxZGstzEC0Ypawj7l%2FmLllwz%2FEGNtb4CTOLV79L0w%2FUCvsxwXe0cUXP8D3MYcoAJ7pga%2Be2THuL083AMnI%2Fc%2FJ%2F%2FdOH4jgPx9WuaJCXABjJSp%2FEjuxFIpPwme0jJPuW8upELnNSlXbYRZSXkNBsfnsUYf2gJ%2B4Apyo43%2BxmYjkLiMHNpJ5UsRZyraadBXgAacmgaKky96G8%2BK65RR%2FG0ZzhN7sgZ9mLGyAZiPTURr%2BP9mr6CIxx9my0t0lKEhqdMWvabY23M2%2FYj1VSS9Jgbj59EAXEBhkYj17LTYZCZSWvSQtcG43HS1uTPF6fL1LBsh9G0Ro%2BvLFHAnhV5C5524Y%2FEsRL%2FRjK7ITd0zh1%2BLNpwiVvFHqxu6JG8I1epXNsA9j641cYRbA0Th8PooG9tQCMEy4n5sjTA3A4O1A7OgQdEbKJ0af5qIX1ur3gYcoYQFB%2B%2FkjlKatK3VkZwJrR5A%2BT%2BHpZ8VohVKNoZP9PDHftldniQuUFkJTFEOZkWxDhgPf5kjRCrX9OLZEWUlf7P7hQBdGpF6EiCAunoUsVoAMzcb%2FFBOi3UFRoUJrFkFkFx%2B69y42Aj8pY58oxL20SC3I9ri5ZmQJvhqs7SjvuDGECVYcmVcyr3t%2BPBCjrWi9v%2BuYoZMv9RDI9MN3OpcwGOpcBGLQtMa09h7Z670H%2F6TEc8GKafA%2FSL4sXCKmGT1w5vc3OnYYApJLZ4puMBlmtBHQMuQ4rwKqisAo%2F0hg%2BVBo%2Fs58n2b1jkYwnDOzgT4nJbF7ApcfPIjsK1SgX%2FpEcQsoiNbcGqe69Un9%2BNZTZBQHXq%2BJCu69tOX1HBziFcfU0%2FLDECjzg7Kfy2nqcl6GEs1kWcERcD75Fag%3D%3D&Expires=1770618238)

### 4.2 Geometric Interpretation

The conformal map *compresses* the pre-image circle most strongly at \(\theta = 0\), near the major-axis endpoint \((q, 0)\), and *stretches* most strongly at \(\theta = \pi/2\), near the minor-axis endpoint \((0, p)\). This means integer lattice points in the Joukowski image are packed \(q/p\) times more densely per unit arc length near the larger factor than near the smaller factor.

### 4.3 Arc Speed Anisotropy

An equivalent statement in terms of arc speed: for the parametric ellipse \(z(\theta) = (q\cos\theta, p\sin\theta)\):

\[
\left|\frac{dz}{d\theta}\right|_{\theta=0} = p, \quad \left|\frac{dz}{d\theta}\right|_{\theta=\pi/2} = q \quad (15)
\]

Uniform-\(\theta\) sampling covers less arc per increment near the major axis (speed \(= p\)) and more arc near the minor axis (speed \(= q\)). The sampling density per unit arc is therefore:

\[
\rho_{\text{arc}}(\theta=0) : \rho_{\text{arc}}(\theta=\pi/2) = \frac{1}{p} : \frac{1}{q} = q : p \quad (16)
\]

This is the same \(q/p\) ratio from Theorem 1, confirming that conformal compression and parametric sampling anisotropy are dual descriptions of the same phenomenon.

### 4.4 Kepler's Law for the Factoring Ellipse

The areal velocity (angular momentum per unit mass) for the parametric ellipse is:

\[
L = \operatorname{Im}(\bar{z} \cdot \dot{z}) = n^2 - m^2 = N \quad (17)
\]

This is constant for all \(\theta\), analogous to Kepler's second law. The effective angular velocity varies as:

\[
\omega_{\text{eff}}(\theta) = \frac{N}{|z(\theta)|^2} \quad (18)
\]

with maximum \(N/p^2\) at the minor axis and minimum \(N/q^2\) at the major axis. The dwell-time ratio is:

\[
\frac{\omega_{\text{eff}}(\pi/2)}{\omega_{\text{eff}}(0)} = \frac{q^2}{p^2} = \left(\frac{q}{p}\right)^2 \quad (19)
\]

A process that integrates signal over time (rather than arc length) accumulates \((q/p)^2\) more signal near the major axis.