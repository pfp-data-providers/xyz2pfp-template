#!/bin/bash

echo "##############"
DATA_DIR=datasets
RDF_FILE=${DATA_DIR}/xyz.nt
export NO_LIMIT=1
start_time=$(date +%s)

python scripts/orgs.py
python scripts/places.py
python scripts/persons.py
python scripts/finalize.py

end_time=$(date +%s)
duration=$((end_time - start_time))
formatted_duration=$(printf '%02dh:%02dm:%02ds\n' $(($duration/3600)) $(($duration%3600/60)) $(($duration%60)))

file_size=$(du -h "${RDF_FILE}" | cut -f1)
numberoflines=$(wc -l < ${RDF_FILE})
formatted_number=$(printf "%'d" $numberoflines)

echo "Created Dataset with ${formatted_number} triples in ${formatted_duration}"
echo "######################"