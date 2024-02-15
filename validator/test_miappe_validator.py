import sys
from miappe_validator import Miappe_validator as mv
input_file=sys.argv[1]
mv(input_file).run_miappe_validator()
