import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.pdf_parser import main

main()