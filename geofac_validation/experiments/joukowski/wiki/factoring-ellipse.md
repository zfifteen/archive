## 2. The Factoring Ellipse

### 2.1 Complex Exponential Decomposition

The standard parametric ellipse centered at the origin with semi-major axis \(a\) and semi-minor axis \(b\) is given by \(x = a\cos\theta\), \(y = b\sin\theta\). Using Euler's formula[^4]:

\[
\cos\theta = \frac{e^{i\theta} + e^{-i\theta}}{2}, \quad \sin\theta = \frac{e^{i\theta} - e^{-i\theta}}{2i}
\]

the complex representation \(z = x + iy\) becomes:

\[
z(\theta) = \frac{a+b}{2}\,e^{i\theta} + \frac{a-b}{2}\,e^{-i\theta} \quad (1)
\]

This expresses the ellipse as the vector sum of two circular motions: a counterclockwise (CCW) phasor with radius \(R_+ = (a+b)/2\) and a clockwise (CW) phasor with radius \(R_- = (a-b)/2\)[^185].

![](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/6491db48b0a9707d184efabb02ee441f/2d7befbb-9a9a-4412-93d8-6d60649bd568/80c44e59.png?AWSAccessKeyId=ASIA2F3EMEYEXZNGBIW7&Signature=64tlT1MAlggyvNbPCj55jp1H%2B3w%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEL3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQDqcjCnvTbXg3zfE1lgVnFYPqcMsIOO%2FspxNrECqYa8bAIhAIwftuqprtvgtRhBE3%2Bpmut%2FZBGYPGZ7tMO%2B%2BSX4Z%2BrOKvwECIb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMNjk5NzUzMzA5NzA1IgyjzNC3J3op40fgkr4q0AS3bMD%2FCcknQzDerFaYG88OBsix0wraDsHVzLb0FNSxyWtqH8R%2FBXZmOTgNF3G3zEajtffM3l6%2FMwKKP9q8wM75gaNBcspgKJVip9QEtEM9VbrX4XvPgbRgO1kh2IkT79BUEtCDK5exaMxZGstzEC0Ypawj7l%2FmLllwz%2FEGNtb4CTOLV79L0w%2FUCvsxwXe0cUXP8D3MYcoAJ7pga%2Be2THuL083AMnI%2Fc%2FJ%2F%2FdOH4jgPx9WuaJCXABjJSp%2FEjuxFIpPwme0jJPuW8upELnNSlXbYRZSXkNBsfnsUYf2gJ%2B4Apyo43%2BxmYjkLiMHNpJ5UsRZyraadBXgAacmgaKky96G8%2BK65RR%2FG0ZzhN7sgZ9mLGyAZiPTURr%2BP9mr6CIxx9my0t0lKEhqdMWvabY23M2%2FYj1VSS9Jgbj59EAXEBhkYj17LTYZCZSWvSQtcG43HS1uTPF6fL1LBsh9G0Ro%2BvLFHAnhV5C5524Y%2FEsRL%2FRjK7ITd0zh1%2BLNpwiVvFHqxu6JG8I1epXNsA9j641cYRbA0Th8PooG9tQCMEy4n5sjTA3A4O1A7OgQdEbKJ0af5qIX1ur3gYcoYQFB%2B%2FkjlKatK3VkZwJrR5A%2BT%2BHpZ8VohVKNoZP9PDHftldniQuUFkJTFEOZkWxDhgPf5kjRCrX9OLZEWUlf7P7hQBdGpF6EiCAunoUsVoAMzcb%2FFBOi3UFRoUJrFkFkFx%2B69y42Aj8pY58oxL20SC3I9ri5ZmQJvhqs7SjvuDGECVYcmVcyr3t%2BPBCjrWi9v%2BuYoZMv9RDI9MN3OpcwGOpcBGLQtMa09h7Z670H%2F6TEc8GKafA%2FSL4sXCKmGT1w5vc3OnYYApJLZ4puMBlmtBHQMuQ4rwKqisAo%2F0hg%2BVBo%2Fs58n2b1jkYwnDOzgT4nJbF7ApcfPIjsK1SgX%2FpEcQsoiNbcGqe69Un9%2BNZTZBQHXq%2BJCu69tOX1HBziFcfU0%2FLDECjzg7Kfy2nqcl6GEs1kWcERcD75Fag%3D%3D&Expires=1770618238)

### 2.2 Setting Semi-Axes to Prime Factors

For a semiprime \(N = pq\) with \(p \leq q\), we define the *factoring ellipse* as the ellipse with semi-major axis \(a = q\) and semi-minor axis \(b = p\). Then:

\[
R_+ = \frac{q+p}{2} = n, \quad R_- = \frac{q-p}{2} = m \quad (2)
\]

These are precisely the Fermat variables. The fundamental identity of Fermat factorization emerges as a conservation law[^89]:

\[
R_+^2 - R_-^2 = n^2 - m^2 = \frac{(p+q)^2 - (q-p)^2}{4} = \frac{4pq}{4} = N \quad (3)
\]

The area of the factoring ellipse is \(\pi ab = \pi pq = \pi N\), encoding the semiprime geometrically.

### 2.3 Boundary Cases

The factoring ellipse interpolates between two degenerate limits:

| Condition | \(R_+\) | \(R_-\) | Geometry | Factoring meaning |
|---|---|---|---|---|
| \(p = q\) | \(p\) | \(0\) | Circle | Perfect square, trivial |
| \(p = 1\) | \((q+1)/2\) | \((q-1)/2\) | Near-degenerate line | Trivially factorable |
| \(1 < p < q\) | \(n\) | \(m\) | Proper ellipse | Nontrivial semiprime |

Every semiprime lives on the spectrum between circle and line segment, parametrized continuously by the factor balance.