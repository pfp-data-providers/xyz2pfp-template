# xyz2pfp
repo to serialize xyz-entity data to pfp-cidoc

This repo fetches data from the [xyz-entities repo](https://github.com/xyz-project/xyz-entities) and converts it into a CIDOC CRM RDF Graph validating against the famous [PFP-Shacl](https://pfp-schema.acdh.oeaw.ac.at/shacl/shacl.ttl).

## PFP
[PFP](https://www.oeaw.ac.at/acdh/research/dh-research-infrastructure/activities/modelling-humanities-data/pfp-prosopographical-research-platform-austria) stands for **Prosopographical Research Platform Austria** or **Prosopographische Forschungsplattform Österreich** in German.


### Usage

* clone this repo
* run `./inits.sh` to replace the placeholder `xyz` with your project's slug, e.g. 

```shell
./init_setup.sh akademie
```