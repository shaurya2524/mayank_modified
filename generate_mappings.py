import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nyaya_sahayak.legal_extractor import main

main()