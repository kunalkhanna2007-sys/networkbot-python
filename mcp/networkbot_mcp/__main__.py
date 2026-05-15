"""Entry point for `python -m networkbot_mcp`."""
import sys
import os

# Allow running as: python -m networkbot_mcp
# Picks up NETWORKBOT_API_KEY from env or .env file
from .server import mcp

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
