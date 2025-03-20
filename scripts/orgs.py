import os
import requests
from tqdm import tqdm
from acdh_cidoc_pyutils import (
    make_e42_identifiers,
    make_appellations,
    p95i_was_formed_by,
)
from acdh_cidoc_pyutils.namespaces import CIDOC
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import get_xmlid, make_entity_label
from acdh_xml_pyutils.xml import NSMAP
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF


entity_type = "org"
g = Graph()
domain = "https://xyz.acdh.oeaw.ac.at/"
PU = Namespace(domain)

rdf_dir = "./datasets"
os.makedirs(rdf_dir, exist_ok=True)

index_file = f"./xyz-list{entity_type}.xml"


print("check if source file exists")
if os.path.exists(index_file):
    pass
else:
    url = "https://raw.githubusercontent.com/xyz-project/xyz-entities/refs/heads/main/indices/listorg.xml"  # noqa: E501
    print(f"fetching {index_file} from {url}")
    response = requests.get(url)
    with open(index_file, "wb") as file:
        file.write(response.content)


doc = TeiReader(index_file)
items = doc.any_xpath(f".//tei:{entity_type}[@xml:id]")
for x in tqdm(items, total=len(items)):
    label = make_entity_label(x.xpath(".//*[1]")[0], default_lang="de")
    if "no label" in label[0]:
        print(label)
        continue
    xml_id = get_xmlid(x)
    item_id = f"{PU}{xml_id}"
    subj = URIRef(item_id)
    g.add((subj, RDF.type, CIDOC["E74_Group"]))

    # ids
    g += make_e42_identifiers(
        subj,
        x,
        type_domain="https://pfp-custom-types",
        default_lang="de",
    )

    # names
    g += make_appellations(
        subj, x, type_domain="https://pfp-custom-types", default_lang="de"
    )

    # located
    for y in x.xpath(
        ".//tei:location[@type='located_in_place']/tei:placeName/@key", namespaces=NSMAP
    ):
        g.add((subj, CIDOC["P74_has_current_or_former_residence"], URIRef(f"{PU}{y}")))

    # founded
    for y in x.xpath(".//tei:desc/tei:date/@from-iso", namespaces=NSMAP):
        g += p95i_was_formed_by(
            subj, start_date=y, label=f"{label[0]} wurde gegründet", label_lang=label[1]
        )

save_path = os.path.join(rdf_dir, f"xyz_{entity_type}.nt")
print(f"saving graph as {save_path}")
g.serialize(save_path, format="nt", encoding="utf-8")
