from subprocess import check_output
from pathlib import Path

PROGRAM_PATH = str(Path('PaLaser-C_API_V1.0/PaLaser.exe'))

result = check_output(PROGRAM_PATH + ' -s').decode()

print(result)
