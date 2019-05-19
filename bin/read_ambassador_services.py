#!/usr/local/bin/python3
import json
import os
import subprocess
import sys
import yaml

def ambassador_services_from(docs):
    """Return the services from a set of K8s Manifests."""
    services = []
    for doc in docs:
        if doc is not None:
            for k,v in doc.items():
                if k == "kind" and v == "Service":
                    services.append(doc)
    return services

def metadata_from_ambassador_service(service):
    """Return the metadata from object or None if it does not exist."""
    if "metadata" in service:
        metadata=service["metadata"]
        return metadata
    else:
        return None

def name_from_metadata(metadata):
    """Return the name from object or None if it does not exist."""
    if "name" in metadata:
        return metadata["name"]
    else:
        return None

def annotation_from_metadata(metadata):
    """Return the Ambassador annotation string from a document."""
    if "annotations" in metadata and metadata["annotations"]:
        annotations = metadata["annotations"]
        if "getambassador.io/config" in annotations:
            return annotations["getambassador.io/config"]
        else:
            return None
    else:
        return None

def yaml_docs_from_metadata_string(metadata):
    """Return a list of YAML objects from a YAML string."""
    annotation_string = annotation_from_metadata(metadata)
    if annotation_string is None:
        return None
    docs = list()
    for raw_doc in annotation_string.split('\n---'):
        try:
            docs.append(yaml.full_load(raw_doc))
        except SyntaxError:
            docs.append(raw_doc)
    return docs

def ambassador_services_from_directory(input_dir):
    helm = subprocess.Popen(['helm', 'template', input_dir], stdout=subprocess.PIPE)
    docs = yaml.load_all(helm.stdout, Loader=yaml.FullLoader)
    return ambassador_services_from(docs)

def ambassador_mappings_from_directory(directory):
    mappings = list()
    for service in ambassador_services_from_directory(directory):
        ambassador_metadata = metadata_from_ambassador_service(service)
        if ambassador_metadata:
            docs = yaml_docs_from_metadata_string(ambassador_metadata)
            if docs is not None:
                for doc in docs:
                    if "kind" in doc and "Mapping" == doc["kind"]:
                        mappings.append(doc)
    return mappings

def main():
    chartsdir="/Users/derrickburns/go/src/github.com/tidepool-org/development/charts/"
    mappings = ambassador_mappings_from_directory(chartsdir + 'tidepool/0.1.0')
    print(yaml.dump(mappings,Dumper=yaml.Dumper))

if __name__ == "__main__":
    main()

