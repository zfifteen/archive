## 5. The Polarization Analogy

### 5.1 Phasor Decomposition as Circular Polarization

The decomposition of the ellipse into counter-rotating phasors is structurally identical to the decomposition of elliptically polarized light into right-hand circular polarization (RHCP, amplitude \(R_+\)) and left-hand circular polarization (LHCP, amplitude \(R_-\))[^155][^185].

### 5.2 Stokes Parameters of the Factoring Ellipse

In the circular basis, the Stokes parameters are[^155][^163]:

\[
S_0 = R_+^2 + R_-^2 = n^2 + m^2 = \frac{p^2 + q^2}{2} \quad (20)
\]

\[
S_3 = R_+^2 - R_-^2 = n^2 - m^2 = N \quad (21)
\]

**The third Stokes parameter of the factoring ellipse is identically the semiprime \(N\).** This is a direct consequence of the Fermat identity.

### 5.3 Degree of Circular Polarization

The degree of circular polarization (equivalently, the normalized \(S_3\)) is:

\[
V = \frac{S_3}{S_0} = \frac{2N}{p^2 + q^2} = \frac{2pq}{p^2 + q^2} = \sin\!\big(2\arctan(p/q)\big) \quad (22)
\]

This quantity maps to the latitude on the Poincare sphere[^171]:

\[
\sin(2\chi) = V, \quad \chi = \frac{1}{2}\arcsin\!\left(\frac{2N}{p^2+q^2}\right) \quad (23)
\]

![](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/6491db48b0a9707d184efabb02ee441f/2d7befbb-9a9a-4412-93d8-6d60649bd568/01fcaa55.png?AWSAccessKeyId=ASIA2F3EMEYEXZNGBIW7&Signature=yginQ7GHco3Ah0y%2BxCvd9gOYD2g%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEL3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQDqcjCnvTbXg3zfE1lgVnFYPqcMsIOO%2FspxNrECqYa8bAIhAIwftuqprtvgtRhBE3%2Bpmut%2FZBGYPGZ7tMO%2B%2BSX4Z%2BrOKvwECIb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMNjk5NzUzMzA5NzA1IgyjzNC3J3op40fgkr4q0AS3bMD%2FCcknQzDerFaYG88OBsix0wraDsHVzLb0FNSxyWtqH8R%2FBXZmOTgNF3G3zEajtffM3l6%2FMwKKP9q8wM75gaNBcspgKJVip9QEtEM9VbrX4XvPgbRgO1kh2IkT79BUEtCDK5exaMxZGstzEC0Ypawj7l%2FmLllwz%2FEGNtb4CTOLV79L0w%2FUCvsxwXe0cUXP8D3MYcoAJ7pga%2Be2THuL083AMnI%2Fc%2FJ%2F%2FdOH4jgPx9WuaJCXABjJSp%2FEjuxFIpPwme0jJPuW8upELnNSlXbYRZSXkNBsfnsUYf2gJ%2B4Apyo43%2BxmYjkLiMHNpJ5UsRZyraadBXgAacmgaKky96G8%2BK65RR%2FG0ZzhN7sgZ9mLGyAZiPTURr%2BP9mr6CIxx9my0t0lKEhqdMWvabY23M2%2FYj1VSS9Jgbj59EAXEBhkYj17LTYZCZSWvSQtcG43HS1uTPF6fL1LBsh9G0Ro%2BvLFHAnhV5C5524Y%2FEsRL%2FRjK7ITd0zh1%2BLNpwiVvFHqxu6JG8I1epXNsA9j641cYRbA0Th8PooG9tQCMEy4n5sjTA3A4O1A7OgQdEbKJ0af5qIX1ur3gYcoYQFB%2B%2FkjlKatK3VkZwJrR5A%2BT%2BHpZ8VohVKNoZP9PDHftldniQuUFkJTFEOZkWxDhgPf5kjRCrX9OLZEWUlf7P7hQBdGpF6EiCAunoUsVoAMzcb%2FFBOi3UFRoUJrFkFkFx%2B69y42Aj8pY58oxL20SC3I9ri5ZmQJvhqs7SjvuDGECVYcmVcyr3t%2BPBCjrWi9v%2BuYoZMv9RDI9MN3OpcwGOpcBGLQtMa09h7Z670H%2F6TEc8GKafA%2FSL4sXCKmGT1w5vc3OnYYApJLZ4puMBlmtBHQMuQ4rwKqisAo%2F0hg%2BVBo%2Fs58n2b1jkYwnDOzgT4nJbF7ApcfPIjsK1SgX%2FpEcQsoiNbcGqe69Un9%2BNZTZBQHXq%2BJCu69tOX1HBziFcfU0%2FLDECjzg7Kfy2nqcl6GEs1kWcERcD75Fag%3D%3D&Expires=1770618238)

### 5.4 Poincare Sphere as Factor-Balance Space

The Poincare sphere provides a natural topology for semiprime factoring difficulty:

- **North pole** (\(\chi = \pi/4\), \(V = 1\)): circular polarization, \(p = q\), perfect square (trivial)
- **Equator** (\(\chi = 0\), \(V = 0\)): linear polarization, \(p \ll q\) or \(p = 1\) (trivially factorable by ECM or trial division)
- **Mid-latitudes**: nontrivial semiprimes with varying difficulty profiles

RSA primes are chosen near the north pole (balanced factors), where the polarization is nearly circular and the conformal anisotropy vanishes (\(q/p \to 1\)).

### 5.5 The Factoring-Polarimetry Dictionary

| Ellipse / Polarization Concept | Factoring Concept |
|---|---|
| Semi-major axis \(a\) | Larger factor \(q\) |
| Semi-minor axis \(b\) | Smaller factor \(p\) |
| Area \(\pi ab\) | \(\pi N\) |
| CCW phasor radius \(R_+\) | Fermat half-sum \(n = (p+q)/2\) |
| CW phasor radius \(R_-\) | Fermat half-difference \(m = (q-p)/2\) |
| Joukowski radius \(\mathcal{R}\) | \(\sqrt{n/m}\) |
| Hyperbolic parameter \(u\) | \(\operatorname{arctanh}(p/q)\) |
| Stokes \(S_3\) | The semiprime \(N\) |
| Stokes \(S_0\) | \((p^2 + q^2)/2\) |
| Degree of circular polarization \(V\) | \(2N/(p^2+q^2)\) |
| Axial ratio | \(q/p\) |
| Poincare latitude \(2\chi\) | Factor balance measure |
| Circle (\(V = 1\)) | \(p = q\), trivial |
| Line segment (\(V = 0\)) | \(p = 1\), trivial |
| Joukowski derivative ratio | \(q/p\) (conformal anisotropy) |
| Dwell-time ratio | \((q/p)^2\) |
