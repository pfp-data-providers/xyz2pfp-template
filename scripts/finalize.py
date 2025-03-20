import glob
import os
from rdflib import Graph

prefix = "xyz"

files = glob.glob(f"./datasets/{prefix}_*.nt")
out_file = os.path.join("datasets", f"{prefix}.nt")
g = Graph()
for x in files:
    g.parse(x)
    os.unlink(x)
print(f"serializing graph to {out_file}")
g.serialize(out_file, format="nt", encoding="utf-8")
