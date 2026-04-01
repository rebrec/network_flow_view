import re

def parse_nvql(query_string: str) -> dict:
    """
    Parser simple pour le NetVis Query Language (NVQL) V1.
    Traduit une chaîne "key:value" en un dictionnaire de filtres.
    Exemples:
    "src:10.1.1.1 and port:443" -> {"ip_src": "10.1.1.1", "port_dst": 443}
    "not proto:UDP" -> {"exclude_protocol": "UDP"}
    """
    filters = {}

    # Séparation par "and" (on gère seulement le AND pour la V1 simple)
    tokens = [t.strip() for t in query_string.split("and")]

    for token in tokens:
        is_negated = False
        if token.lower().startswith("not "):
            is_negated = True
            token = token[4:]

        # Recherche de motifs "key:value"
        match = re.match(r"(\w+[\.\w]*):(\S+)", token)
        if match:
            key, value = match.groups()

            # Mapping des clés NVQL vers les colonnes DB
            mapping = {
                "src": "ip_src",
                "dst": "ip_dst",
                "port": "port_dst",
                "proto": "protocol",
                "src.zone": "src_zone",
                "dst.zone": "dst_zone",
                "tag": "tag"
            }

            db_key = mapping.get(key, key)
            if is_negated:
                db_key = f"exclude_{db_key}"

            # Cast type pour les ports
            if "port" in db_key:
                value = int(value)

            filters[db_key] = value

    return filters
