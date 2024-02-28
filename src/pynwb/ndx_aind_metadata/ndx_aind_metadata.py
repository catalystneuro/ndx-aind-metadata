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


def get_surgery(procedures):
    """Summarizes surgery information from procedure class"""

    text_list = []
    for sub_proc in len(procedures["subject_procedures"]):
        if sub_proc["procedure_type"] == "Surgery":
            procedure_date = sub_proc["start_date"]
            procedure_list = []
            for proc in sub_proc["procedures"]:
                procedure_list.append(proc["procedure_type"])
            procedure_list.append("performed","on",procedure_date)
            procedure_text = ' '.join(i) for i in procedure_list
            text_list.append(procedure_text)
    complete_surgery_text = '. 'join(i) for i in text_list
    return complete_surgery_text


def get_virus(procedures):
    """Extracts viruses that were injected from procedure class"""

    virus_list = []
    for sub_proc in len(procedures["subject_procedures"]):
        if sub_proc["procedure_type"] == "Surgery":
            for proc in sub_proc["procedures"]:
                try:
                    if proc["injection_materials"]["material_type"] == "Virus":
                        virus_list.append(proc["injection_materials"]["name"])
                except:
                    pass
    return virus_list


def extract_nwbfile_kwargs(self, aind_datadescription_json: str, aind_procedures_json: str, aind_session_json: str):
    """Extracts key metadata for the NWBFile"""

    datadescription = json.load(aind_datadescription_json)
    procedures = json.load(aind_procedures_json)
    session = json.load(aind_session_json)
    self._validate_aind_metadata(datadescription, aind_DataDescription)
    self._validate_aind_metadata(procedures, aind_Procedures)
    self._validate_aind_metadata(session, aind_Session)

    kwargs = dict(
        identifier = datadescription["name"], #Is this what we want? Also for session_id below
        session_start_time = session["session_start_time"],
        timestamps_reference_time  = session["session_start_time"], #I assume this is true
        experimenter = session["experimenter_full_name"],
        session_id = datadescription["name"],
        institution = datadescription["institution"],
        keywords = datadescription["modality"], #we can probably add some other things here
        protocol = session["protocol_id"] + "and IACUC protocol " + session["iacuc_protocol"],
        lab = datadescription["group"],
        surgery = get_surgery(procedures),
        virus = get_virus(procedures),
    )

    return kwargs


def new_subject_init(self, aind_subject_json: str, aind_session_json: str):

    aind_metadata = json.loads(aind_subject_json)
    self._validate_aind_metadata(aind_metadata, aind_Subject)
    aind_session = json.load(aind_session_json)
    self._validate_aind_metadata(aind_session, aind_Session)

    sex_value_map = {"Male": "M", "Female": "F"}

    date_of_birth = datetime.strptime(subject["date_of_birth"], "%Y-%m-%d")
    date_of_acquisition = datetime.fromisoformat(session['session_start_time']).date()
    age = (date_of_acquisition-date_of_birth).days

    kwargs = dict(
        subject_id=aind_metadata["subject_id"],
        sex=sex_value_map[aind_metadata["sex"]],
        date_of_birth=datetime.strptime(aind_metadata["date_of_birth"], "%Y-%m-%d"),
        genotype=aind_metadata["genotype"],
        species=aind_metadata["species"]["name"],
        age = "P"+str(age),
    )

    Subject.__init__(self, **kwargs)
    self.aind_subject_json = aind_subject_json


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




