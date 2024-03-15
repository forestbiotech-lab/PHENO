#!/usr/bin/env python3
import sys
import time
t1 = time.perf_counter(), time.process_time()
from miappe_validator import Miappe_validator as mv
input_file=sys.argv[1]
mv(input_file).run_miappe_validator()

t2 = time.perf_counter(), time.process_time()
#print(f"{function.__name__}()")
print(f" Real time: {t2[0] - t1[0]:.2f} seconds")
print(f" CPU time: {t2[1] - t1[1]:.2f} seconds")
print()

