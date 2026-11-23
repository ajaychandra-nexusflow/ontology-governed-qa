#!/usr/bin/env python3
"""Offline governance gates for an ontology extension (gates 1-4, optional 7).

Usage:
  python check_extension.py extension.ttl --core core.ttl [--shapes shapes.ttl]
                            [--namespace https://example.com/odp#]

Exit code 0 when every gate that ran passes, 1 otherwise, 2 on usage error.
Gates 5, 6 and 8 need live data / a reasoner; see references/governance-gates.md.
"""
import argparse
import sys

try:
    from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
    from rdflib.namespace import SKOS, XSD
except ImportError:
    sys.exit("rdflib is required: pip install rdflib")

ALLOWED_EXTERNAL = {str(RDF), str(RDFS), str(OWL), str(SKOS), str(XSD)}


def gate(n, name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] Gate {n}: {name}" + (f" - {detail}" if detail else ""))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("extension")
    ap.add_argument("--core", help="core ontology Turtle (enables gate 3)")
    ap.add_argument("--shapes", help="SHACL shapes Turtle (enables gate 7, needs pyshacl)")
    ap.add_argument("--namespace", default="https://example.com/odp#", help="ontology namespace (default: %(default)s)")
    a = ap.parse_args()

    ODP = Namespace(a.namespace)
    results = []

    # Gate 1: parses
    ext = Graph()
    try:
        ext.parse(a.extension, format="turtle")
        results.append(gate(1, "Turtle parses", True, f"{len(ext)} triples"))
    except Exception as e:  # noqa: BLE001
        gate(1, "Turtle parses", False, str(e))
        return 1

    # Gate 2: vocabulary
    allowed = ALLOWED_EXTERNAL | {a.namespace}
    bad = set()
    for s, p, o in ext:
        terms = [p] + ([o] if p == RDF.type and isinstance(o, URIRef) else [])
        for t in terms:
            if isinstance(t, URIRef) and not any(str(t).startswith(ns) for ns in allowed):
                bad.add(str(t))
    results.append(gate(2, "Only approved vocabulary", not bad, ", ".join(sorted(bad))))

    # Gate 3: no core redefinition
    if a.core:
        core = Graph()
        core.parse(a.core, format="turtle")
        core_subjects = {s for s in core.subjects() if isinstance(s, URIRef)}
        clash = sorted(str(s) for s in set(ext.subjects()) if s in core_subjects)
        results.append(gate(3, "No core IRI redefined", not clash, ", ".join(clash)))
    else:
        print("[SKIP] Gate 3: pass --core to enable")

    # Gate 4: every concept has a binding
    concepts = set(ext.subjects(RDF.type, ODP.Concept))
    bound = set(ext.objects(None, ODP.bindsConcept))
    missing = sorted(str(c) for c in concepts - bound)
    results.append(gate(4, "Every new concept has a binding", not missing,
                        ", ".join(missing) if missing else f"{len(concepts)} concept(s) checked"))

    # Gate 7: SHACL (optional)
    if a.shapes:
        try:
            from pyshacl import validate
            merged = Graph()
            if a.core:
                merged += core
            merged += ext
            shapes = Graph().parse(a.shapes, format="turtle")
            conforms, _, text = validate(merged, shacl_graph=shapes, inference="rdfs")
            results.append(gate(7, "SHACL conforms", conforms, "" if conforms else text.strip().splitlines()[0]))
        except ImportError:
            print("[SKIP] Gate 7: pip install pyshacl")
    else:
        print("[SKIP] Gate 7: pass --shapes to enable")

    print("\nGates 5, 6 and 8 need live data and a reasoner; run them in your runtime.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
