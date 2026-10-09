"""Real custom MCP stdio server: run with the same virtual-environment Python."""
from mcp.server.fastmcp import FastMCP
from src.catalog import drug_info as lookup, check_interaction as check, find_generic as generic
mcp = FastMCP('MediGuide Medicines')

@mcp.tool()
def drug_info(medicine: str) -> dict:
    """Retrieve educational uses, common side effects and warnings for a medicine."""
    return lookup(medicine)

@mcp.tool()
def check_interaction(medicines: list[str]) -> dict:
    """Check all pairs against a limited dataset; unknown NEVER means safe."""
    return check(medicines)

@mcp.tool()
def find_generic(brand: str) -> dict:
    """Find an exact brand-variant ingredient example, requiring pharmacist confirmation."""
    return generic(brand)

if __name__ == '__main__':
    mcp.run(transport='stdio')
