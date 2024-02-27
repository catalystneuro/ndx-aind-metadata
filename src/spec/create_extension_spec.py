# -*- coding: utf-8 -*-
import os.path

from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBDatasetSpec


def main():
    # these arguments were auto-generated from your cookiecutter inputs
    ns_builder = NWBNamespaceBuilder(
        name="""ndx-aind-metadata""",
        version="""0.1.0""",
        doc="""Extension for Allen Institute Neural Dynamics""",
        author=[
            "Saskia", 
        ],
        contact=[
            "my_email@example.com", 
        ],
    )
    ns_builder.include_namespace("core")

    # see https://pynwb.readthedocs.io/en/stable/tutorials/general/extensions.html
    # for more information
    aind_subject = NWBGroupSpec(
        neurodata_type_def="AindSubject",
        neurodata_type_inc="Subject",
        doc="Subject with AIND metadata",
        datasets=[
            NWBDatasetSpec(
                name="aind_schema_json",
                doc="json of subject metadata",
                dtype="text",
                shape=None,
                quantity=1,
            )
        ],
    )

    lab_metadata_classes = [
        NWBGroupSpec(
            neurodata_type_def=f"Aind{x}",
            neurodata_type_inc="LabMetaData",
            doc=f"{x} with AIND metadata",
            datasets=[
                NWBDatasetSpec(
                    name="aind_schema_json",
                    doc="json of session metadata",
                    dtype="text",
                    shape=None,
                    quantity=1,
                )
            ],
        ) for x in (
            "Acquisition",
            "DataDescription",
            "Procedures",
            "Processing",
            "Rig",
            "Session",
        )
    ]

    new_data_types = [aind_subject] + lab_metadata_classes

    # export the spec to yaml files in the spec folder
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, new_data_types, output_dir)


if __name__ == "__main__":
    # usage: python create_extension_spec.py
    main()
