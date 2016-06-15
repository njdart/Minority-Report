export PYTHONPATH=..
python3 -m cProfile -o minRep.cprof minority_report.py
pyprof2calltree -k -i minRep.cprof
