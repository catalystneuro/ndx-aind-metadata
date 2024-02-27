import json
from datetime import datetime
from functools import partialmethod

import jsonschema
from aind_data_schema.core.subject import Subject as aind_Subject
from aind_data_schema.core.session import Session as aind_Session
from aind_data_schema.core.rig import Rig as aind_Rig
from aind_data_schema.core.data_description import DataDescription as aind_DataDescription
from aind_data_schema.core.procedures import Procedures as aind_Procedures
from aind_data_schema.core.processing import Processing as aind_Processing
from pynwb import get_class
from pynwb.file import Subject, LabMetaData


def validate_aind_metadata(self, metadata: dict, model):

    schema = model.model_json_schema()

    try:
        jsonschema.validate(metadata, schema)
    except jsonschema.exceptions.ValidationError as e:
        self._error_on_new_warn_on_construct(
            error_msg='Invalid AIND metadata: %s' % e.message
        )


def new_subject_init(self, aind_schema_json: str):

    aind_metadata = json.loads(aind_schema_json)
    self._validate_aind_metadata(aind_metadata, aind_Subject)

    sex_value_map = {"Male": "M", "Female": "F"}

    kwargs = dict(
        subject_id=aind_metadata["subject_id"],
        sex=sex_value_map[aind_metadata["sex"]],
        date_of_birth=datetime.strptime(aind_metadata["date_of_birth"], "%Y-%m-%d"),
        genotype=aind_metadata["genotype"],
        species=aind_metadata["species"]["name"],
    )

    Subject.__init__(self, **kwargs)
    self.aind_schema_json = aind_schema_json


AindSubject = get_class('AindSubject', 'ndx-aind-metadata')
AindSubject.__init__ = new_subject_init
AindSubject._validate_aind_metadata = validate_aind_metadata


def new_labmetadata_init(self, name: str, aind_schema_json: str, model):
    aind_metadata = json.loads(aind_schema_json)
    self._validate_aind_metadata(aind_metadata, model)

    LabMetaData.__init__(self, name=name)
    self.aind_schema_json = aind_schema_json


new_classes = []
for name, model in (
    ("DataDescription", aind_DataDescription),
    ("Procedures", aind_Procedures),
    ("Processing", aind_Processing),
    ("Rig", aind_Rig),
    ("Session", aind_Session),
):
    NewClass = get_class(f'Aind{name}', 'ndx-aind-metadata')
    NewClass.__init__ = partialmethod(new_labmetadata_init, name=f'Aind{name}', model=model)
    NewClass._validate_aind_metadata = validate_aind_metadata
    new_classes.append(NewClass)

AindDataDescription, AindProcedures, AindProcessing, AindRig, AindSession = new_classes




