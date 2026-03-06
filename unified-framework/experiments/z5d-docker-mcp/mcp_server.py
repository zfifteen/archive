import asyncio
import os
import subprocess
import sys
import math
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import mcp.server.stdio

server = Server("z5d-mcp-server")

@server.tool()
async def read_file(filepath: str) -> str:
    """Read and return the contents of a file from the local filesystem"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"

@server.tool()
async def write_file(filepath: str, content: str) -> str:
    """Write content to a file on the local filesystem, overwriting if exists"""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"File '{filepath}' written successfully."
    except Exception as e:
        return f"Error writing file '{filepath}': {str(e)}"

@server.tool()
async def list_dir(dirpath: str) -> str:
    """List contents of a directory with file/directory type and sizes"""
    try:
        entries = os.listdir(dirpath)
        result = []
        for entry in entries:
            full_path = os.path.join(dirpath, entry)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else 0
            result.append(f"{'[DIR]' if is_dir else '[FILE]'} {entry} ({size} bytes)")
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory '{dirpath}': {str(e)}"

@server.tool()
async def bash(command: str) -> str:
    """Execute a bash command and return stdout, stderr, and exit code"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return f"stdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@server.tool()
async def git(args: str) -> str:
    """Execute git commands for version control operations"""
    try:
        result = subprocess.run(f"git {args}", shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return f"stdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing git command: {str(e)}"

@server.tool()
async def brew(args: str) -> str:
    """Execute Homebrew commands for macOS package management"""
    try:
        result = subprocess.run(f"brew {args}", shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return f"stdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing brew command: {str(e)}"

@server.tool()
async def gh(args: str) -> str:
    """Execute GitHub CLI commands"""
    try:
        result = subprocess.run(f"gh {args}", shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return f"stdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing gh command: {str(e)}"

@server.tool()
async def python(args: str) -> str:
    """Execute Python scripts or modules"""
    try:
        result = subprocess.run(f"python {args}", shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return f"stdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing python command: {str(e)}"

@server.tool()
async def pip(args: str) -> str:
    """Execute pip commands for Python package management"""
    try:
        result = subprocess.run(f"pip {args}", shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return f"stdout: {result.stdout}\nstderr: {result.stderr}\nExit code: {result.returncode}"
    except Exception as e:
        return f"Error executing pip command: {str(e)}"

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio

@server.tool()
async def geometric_resolution(n: int, k: float = 0.3) -> str:
    """Compute geometric resolution θ'(n,k) = φ * ((n mod φ) / φ)^k for prime-density mapping. Default k=0.3."""
    try:
        if n < 0:
            return "Error: n must be non-negative."
        mod_phi = n % PHI
        result = PHI * (mod_phi / PHI) ** k
        return f"θ'({n}, {k}) = {result}"
    except Exception as e:
        return f"Error computing geometric resolution: {str(e)}"

@server.tool()
async def universal_z(A: float, B: float, c: float) -> str:
    """Compute universal invariant Z = A * (B / c), with guards for c != 0."""
    try:
        if c == 0:
            return "Error: c cannot be zero (universal invariant)."
        result = A * (B / c)
        return f"Z = {A} * ({B} / {c}) = {result}"
    except Exception as e:
        return f"Error computing Z: {str(e)}"

@server.tool()
async def curvature_kappa(n: int) -> str:
    """Compute curvature κ(n) = d(n) * ln(n+1) / e², where d(n) is the divisor function. Assumes d(n) ≈ ln(n) approximation."""
    try:
        if n <= 0:
            return "Error: n must be positive."
        import math
        d_n = math.log(n)  # Approximation for divisor function
        kappa = d_n * math.log(n + 1) / (math.e ** 2)
        return f"κ({n}) ≈ {kappa} (using d(n) ≈ ln(n))"
    except Exception as e:
        return f"Error computing κ: {str(e)}"

def sieve_of_eratosthenes(n: int) -> int:
    """Return the number of primes <= n using Sieve of Eratosthenes."""
    if n < 2:
        return 0
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.sqrt(n)) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return sum(is_prime)

@server.tool()
async def prime_count(n: int) -> str:
    """Compute the number of primes <= n using sieve. Empirical validation for prime density."""
    try:
        if n < 0:
            return "Error: n must be non-negative."
        count = sieve_of_eratosthenes(n)
        return f"Number of primes <= {n}: {count}"
    except Exception as e:
        return f"Error computing prime count: {str(e)}"

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())