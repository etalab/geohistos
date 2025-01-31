"""Tests related to output validity (duplicity, missing ancestors, etc)."""
from itertools import groupby

from geohisto.constants import DELTA


def test_unicity_per_boundaries(towns):
    """Ensure unicity for a given insee code at its start/end dates."""
    for depcom, siblings in groupby(towns.values(), lambda town: town.depcom):
        for sibling1 in siblings:
            for sibling2 in siblings:
                if sibling1.id != sibling2.id:
                    assert sibling1.valid_at(sibling2.start_datetime) is False
                    assert sibling1.valid_at(sibling2.end_datetime) is False


def test_successors_are_valid(towns):
    """Ensure all successors are valid at the end date."""
    for town in towns.values():
        for successor_id in town.successors.split(';'):
            successor = successor_id and towns.retrieve(successor_id) or None
            if successor:
                try:
                    assert successor.valid_at(town.end_datetime + DELTA)
                except OverflowError:
                    # Happens when end_datetime is already EN_DATETIME.
                    assert successor.valid_at(town.end_datetime)
