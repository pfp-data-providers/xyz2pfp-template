import os
import requests
from lxml.etree import Element
from tqdm import tqdm
from acdh_cidoc_pyutils import (
    make_e42_identifiers,
    make_appellations,
    coordinates_to_p168,
)
from acdh_cidoc_pyutils.namespaces import CIDOC
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import get_xmlid
from acdh_xml_pyutils.xml import NSMAP
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF


BASE_URL = "https://raw.githubusercontent.com/xyz-project/xyz-entities/refs/heads/main/indices/"  # noqa


def p89_falls_within(
    subj: URIRef,
    node: Element,
    domain: URIRef,
    location_id_xpath="./tei:location[@type='located_in_place']/tei:placeName/@key",
) -> Graph:
    g = Graph()
    try:
        range_id = node.xpath(location_id_xpath, namespaces=NSMAP)[0]
    except IndexError:
        return g
    range_uri = URIRef(f"{domain}{range_id}")
    g.add((subj, CIDOC["P89_falls_within"], range_uri))
    return g


g = Graph()
domain = "https://kaiserin-eleonora.oeaw.ac.at/"
PU = Namespace(domain)

if os.environ.get("NO_LIMIT"):
    LIMIT = False
    print("no limit")
else:
    LIMIT = False

rdf_dir = "./datasets"
os.makedirs(rdf_dir, exist_ok=True)
entity_type = "place"
index_file = f"./xyz-list{entity_type}.xml"


print("check if source file exists")
if os.path.exists(index_file):
    pass
else:
    url = f"{BASE_URL}listplace.xml"
    print(f"fetching {index_file} from {url}")
    response = requests.get(url)
    with open(index_file, "wb") as file:
        file.write(response.content)


doc = TeiReader(index_file)
items = doc.any_xpath(f".//tei:{entity_type}[@xml:id]")
if LIMIT:
    items = items[:LIMIT]

for x in tqdm(items, total=len(items)):
    xml_id = get_xmlid(x)
    item_id = f"{PU}{xml_id}"
    subj = URIRef(item_id)
    g.add((subj, RDF.type, CIDOC["E53_Place"]))

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

    # coordinates
    g += coordinates_to_p168(subj, x)

    # falls within
    g += p89_falls_within(subj, x, f"{PU}")


save_path = os.path.join(rdf_dir, f"xyz_{entity_type}.nt")
print(f"saving graph as {save_path}")
g.serialize(save_path, format="nt", encoding="utf-8")
