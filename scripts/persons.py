import os
import requests
from tqdm import tqdm
from acdh_cidoc_pyutils import (
    make_e42_identifiers,
    make_appellations,
    make_birth_death_entities,
    make_affiliations,
    make_entity_label,
    make_occupations,
)
from acdh_xml_pyutils.xml import NSMAP
from acdh_cidoc_pyutils.namespaces import CIDOC
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import get_xmlid
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF


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

index_file = "./xyz-listperson.xml"
entity_type = "person"

print("check if source file exists")
BASE_URL = "https://raw.githubusercontent.com/xyz-project/xyz-entities/refs/heads/main/indices/"  # noqa
if os.path.exists(index_file):
    pass
else:
    url = f"{BASE_URL}listperson.xml"
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
    item_label = make_entity_label(x.xpath(".//tei:persName[1]", namespaces=NSMAP)[0])[
        0
    ]
    item_id = f"{PU}{xml_id}"
    subj = URIRef(item_id)
    g.add((subj, RDF.type, CIDOC["E21_Person"]))
    affilliations = make_affiliations(
        subj,
        x,
        f"{PU}org__",
        item_label,
        org_id_xpath="./tei:orgName/@key",
        org_label_xpath="./tei:orgName/text()",
    )
    g += affilliations

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

    # birth
    try:
        x.xpath(".//tei:birth[./tei:date or ./tei:settlement]", namespaces=NSMAP)[0]
        event_graph, birth_uri, birth_timestxyz = make_birth_death_entities(
            subj,
            x,
            f"{PU}",
            event_type="birth",
            default_prefix="Geburt von",
            date_node_xpath="/tei:date[1]",
            place_id_xpath="//tei:settlement[1]/@key",
        )
        g.add((subj, CIDOC["P98i_was_born"], birth_uri))
        g += event_graph
    except IndexError:
        pass

    # death
    try:
        x.xpath(".//tei:death[./tei:date or ./tei:settlement]", namespaces=NSMAP)[0]
        event_graph, death_uri, birth_timestxyz = make_birth_death_entities(
            subj,
            x,
            f"{PU}",
            event_type="death",
            default_prefix="Tod von",
            date_node_xpath="/tei:date[1]",
            place_id_xpath="//tei:settlement[1]/@key",
        )
        g.add((subj, CIDOC["P100i_died_in"], death_uri))
        g += event_graph
    except IndexError:
        pass

    # occupations
    g += make_occupations(subj, x, id_xpath="./@key")[0]

save_path = os.path.join(rdf_dir, f"xyz_{entity_type}.nt")
print(f"saving graph as {save_path}")
g.serialize(save_path, format="nt", encoding="utf-8")
