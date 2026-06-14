"""`python -m musicbox` runs the interactive CLI simulator.

On the device you instead run the full service (panel + web):
`python -m musicbox.service`.
"""

from .cli import run

run()
