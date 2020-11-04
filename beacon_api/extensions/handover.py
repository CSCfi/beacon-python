"""Prepare Handover."""

from typing import Dict, List
from .. import __handover_drs__, __handover_datasets__, __handover_base__


def add_handover(response: Dict) -> Dict:
    """Add handover to a dataset response."""
    response["datasetHandover"] = make_handover(
        __handover_datasets__,
        [response["datasetId"]],
        response["referenceName"],
        response["start"],
        response["end"],
        response["referenceBases"],
        response["alternateBases"],
        response["variantType"],
    )
    return response


def make_handover(
    paths: List[List[str]], datasetIds: List[str], chr: str = "", start: int = 0, end: int = 0, ref: str = "", alt: str = "", variant: str = ""
) -> List[Dict]:
    """Create one handover for each path (specified in config)."""
    alt = alt if alt else variant
    handovers = []
    start = start + __handover_base__
    end = end + __handover_base__
    for label, desc, path in paths:
        for dataset in set(datasetIds):
            handovers.append(
                {
                    "handoverType": {"id": "CUSTOM", "label": label},
                    "description": desc,
                    "url": __handover_drs__ + "/" + path.format(dataset=dataset, chr=chr, start=start, end=end, ref=ref, alt=alt),
                }
            )

    return handovers
