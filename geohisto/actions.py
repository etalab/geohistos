"""
Perform actions on towns given the modifications' types.

The modifications come from the history of changes.
"""
import logging

from .constants import (
    CHANGE_COUNTY, CHANGE_COUNTY_CREATION, CHANGE_NAME, CHANGE_NAME_CREATION,
    CHANGE_NAME_FUSION, CHANGE_NAME_REINSTATEMENT, CREATION,
    CREATION_DELEGATED, CREATION_DELEGATED_POLE, CREATION_NOT_DELEGATED,
    CREATION_NOT_DELEGATED_POLE, DELETION_FUSION, DELETION_PARTITION, DELTA,
    END_DATETIME, FUSION_ASSOCIATION_ASSOCIATED, OBSOLETE, REINSTATEMENT,
    SPLITING, START_DATE, START_DATETIME
)
from .utils import ACTIONS, compute_id, in_case_of

log = logging.getLogger(__name__)


@in_case_of(CHANGE_NAME, CHANGE_NAME_FUSION)
def change_name(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    successors = ''
    end_datetime = END_DATETIME
    # In case the change name is referenced in historiq after the split.
    if (current_town.end_datetime != END_DATETIME and
            current_town.end_datetime > record.eff):
        end_datetime = current_town.end_datetime
        # Check for already existing successors.
        successors = ';'.join(
            successor.id
            for successor in towns.valid_at(end_datetime + DELTA,
                                            depcom=record.depcom))

    new_town = current_town.generate(
        id=compute_id(current_town.depcom, record.effdate),
        start_datetime=record.eff,
        end_datetime=end_datetime,
        # `nccenr` changes on fusions.
        nccenr=record.nccoff or current_town.nccenr,
        successors=successors
    )
    towns.upsert(new_town)

    old_town = current_town.generate(
        nccenr=record.nccanc,
        end_datetime=record.eff - DELTA,
        modification=record.mod
    )
    old_town = old_town.add_successor(new_town.id)
    towns.upsert(old_town)
    towns.update_successors(old_town, to_town=new_town)


@in_case_of(CHANGE_NAME_CREATION, CREATION)
def creation(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    new_town = current_town.generate(
        id=compute_id(current_town.depcom, record.effdate),
        start_datetime=record.eff,
        end_datetime=END_DATETIME,
        # `nccenr` changes on fusions.
        nccenr=record.nccoff or current_town.nccenr,
        modification=record.mod,
        successors=''
    )
    towns.upsert(new_town)

    has_different_ids = new_town.id != current_town.id
    if has_different_ids:
        towns.update_successors(new_town, from_town=current_town)
        towns.delete(current_town)
        towns.update_successors(current_town, to_town=new_town)


@in_case_of(CREATION_DELEGATED_POLE)
def creation_delegated(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)
    is_already_created = current_town.modification == CREATION_DELEGATED_POLE
    has_the_same_name = record.nccoff == current_town.nccenr
    if is_already_created and has_the_same_name:
        new_town = current_town
    else:
        new_town = current_town.generate(
            id=compute_id(current_town.depcom, record.effdate),
            start_datetime=record.eff,
            end_datetime=END_DATETIME,
            # `nccenr` changes on fusions.
            nccenr=record.nccoff or current_town.nccenr,
            modification=record.mod,
            successors=''
        )
    # It happens with `Pont-d'Ouilly` for instance.
    is_already_registered = new_town.id in towns
    if not is_already_registered:
        towns.upsert(new_town)
    if record.last:
        towns.update_successors(new_town, from_town=current_town)

    # Update ancestors, useful for town that were created since then.
    for ancestor in towns.valid_at(current_town.start_datetime - DELTA,
                                   depcom=record.depcom):
        towns.update_successors(ancestor, to_town=new_town)

    # Do not delete the initial town if all creations are not performed.
    if not record.last:
        return

    has_different_ids = new_town.id != current_town.id
    has_the_same_name = new_town.nccenr == current_town.nccenr
    if has_different_ids and has_the_same_name:
        towns.delete(current_town)


@in_case_of(REINSTATEMENT)
def reinstatement(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    id_ = compute_id(current_town.depcom, record.effdate)
    # It happens with `Nonsard-Lamarche`, `Pretz-en-Argonne` and
    # `Les Avanchers-Valmorel` where a change name is performed
    # at the same date. Handled in special cases.
    is_already_registered = id_ in towns
    if is_already_registered:
        return

    new_town = current_town.generate(
        id=id_,
        start_datetime=record.eff,
        end_datetime=END_DATETIME,
        nccenr=record.nccoff,
        successors='',
        modification=0
    )
    towns.upsert(new_town)

    old_town = current_town.generate(
        nccenr=record.nccoff,
        end_datetime=min(current_town.end_datetime, record.eff - DELTA),
        modification=record.mod
    )
    if new_town.valid_at(old_town.end_datetime + DELTA):
        old_town = old_town.add_successor(new_town.id)
    towns.upsert(old_town)
    towns.replace_successor(old_town, new_town,
                            valid_datetime=new_town.start_datetime - DELTA)


@in_case_of(CHANGE_NAME_REINSTATEMENT)
def change_name_reinstatement(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)
    new_town = current_town.generate(
        id=compute_id(current_town.depcom, record.effdate),
        start_datetime=record.eff,
        end_datetime=END_DATETIME,
        nccenr=record.nccoff,
        successors='',
        modification=0
    )
    towns.upsert(new_town)

    old_town = current_town.generate(
        nccenr=record.nccanc or record.nccoff,
        end_datetime=min(current_town.end_datetime, record.eff - DELTA),
        modification=record.mod
    )
    old_town = old_town.add_successor(new_town.id)
    for ancestor in old_town.get_ancestors(towns):
        for guessed_successor in towns.valid_at(
                old_town.end_datetime + DELTA, depcom=ancestor.depcom):
            if (guessed_successor and guessed_successor.id != old_town.id and
                    guessed_successor.id != new_town.id):
                old_town = old_town.add_successor(guessed_successor.id)
    towns.upsert(old_town)


@in_case_of(SPLITING)
def spliting(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    current_town = current_town.generate(
        modification=record.mod
    )
    towns.upsert(current_town)


@in_case_of(DELETION_PARTITION, DELETION_FUSION, CREATION_DELEGATED)
def deletion(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)
    old_town = current_town.generate(
        nccenr=record.nccoff,
        end_datetime=record.eff - DELTA,
        modification=record.mod
    )
    successor = towns.get_current(record.comech, record.eff)
    old_town = old_town.add_successor(successor.id)
    towns.upsert(old_town)


@in_case_of(FUSION_ASSOCIATION_ASSOCIATED)
def fusion_association_associated(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    end_datetime = record.eff - DELTA

    # It happens only with `Lamarche-en-Woëvre` because
    # the reinstatement is at the same date of the (re)fusion,
    # so we set the end_date just after the start_date exceptionnally.
    # Cannot be moved to specials because of model enforcement.
    has_temporary_existence = current_town.start_datetime == record.eff
    if has_temporary_existence:
        end_datetime = record.eff + DELTA

    old_town = current_town.generate(
        nccenr=record.nccoff,
        end_datetime=end_datetime,
        modification=record.mod
    )
    successor = towns.get_current(record.comech, record.eff)
    old_town = old_town.add_successor(successor.id)
    if successor.modification == CHANGE_NAME_REINSTATEMENT:
        # Deal with fusions then splits declared in the wrong order.
        if old_town.depcom not in successor.successors:
            new_town = towns.get_current(
                old_town.depcom, successor.end_datetime + DELTA)
            successor = successor.add_successor(new_town.id)
            towns.upsert(successor)
    towns.upsert(old_town)


@in_case_of(CREATION_NOT_DELEGATED)
def creation_not_delegated(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    # Create new town only if it doesn't exist yet
    # (same depcom, different name).
    has_same_depcom = record.depcom == record.comech
    has_different_name = current_town.nccenr != record.nccoff
    if has_same_depcom and has_different_name:
        new_town = current_town.generate(
            id=compute_id(current_town.depcom, record.effdate),
            start_datetime=record.eff,
            modification=CREATION_NOT_DELEGATED_POLE
        )
        old_town = new_town.add_successor(current_town.id)
        towns.upsert(new_town)
        towns.update_successors(new_town, from_town=current_town)

        old_town = current_town.generate(
            nccenr=record.nccoff,
            end_datetime=record.eff - DELTA,
            modification=record.mod
        )
        old_town = old_town.add_successor(new_town.id)
        towns.upsert(old_town)
    else:
        successor = towns.get_current(record.comech, record.eff)
        old_town = current_town.generate(
            end_datetime=record.eff - DELTA,
            modification=record.mod
        )
        old_town = old_town.add_successor(successor.id)
        towns.upsert(old_town)


@in_case_of(CREATION_NOT_DELEGATED_POLE)
def creation_not_delegated_pole(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)
    end_datetime = END_DATETIME
    if current_town.start_datetime < record.eff:
        end_datetime = record.eff - DELTA
    old_town = current_town.generate(
        end_datetime=end_datetime,
        modification=record.mod,
        successors=''
    )
    towns.upsert(old_town)

    if not record.last:
        return

    new_town = current_town.generate(
        id=compute_id(current_town.depcom, record.effdate),
        start_datetime=record.eff,
        end_datetime=END_DATETIME,
        nccenr=record.nccoff,
        modification=CREATION_NOT_DELEGATED_POLE
    )
    old_town = old_town.add_successor(new_town.id)
    towns.upsert(old_town)
    new_town.add_successor(current_town.id)
    towns.upsert(new_town)
    towns.update_successors(new_town, from_town=current_town)


@in_case_of(CHANGE_COUNTY)
def change_county(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)
    # We set the `end_datetime` explicitely for the particular case
    # of Blamécourt where the town as fusioned before changing county.
    new_town = current_town.generate(
        id=compute_id(current_town.depcom, record.effdate),
        start_datetime=record.eff,
        end_datetime=max(current_town.end_datetime, record.eff + DELTA)
    )
    towns.upsert(new_town)
    towns.delete(current_town)
    towns.update_successors(current_town, to_town=new_town)

    ancient_town = towns.get_current(record.depanc, record.eff)
    ancient_town_is_valid = ancient_town.valid_at(record.eff)
    if ancient_town_is_valid:
        id_ = compute_id(ancient_town.depcom, current_town.start_date)
        is_new_entry = id_ not in towns
        old_town = ancient_town.generate(
            id=id_,
            start_datetime=current_town.start_datetime,
            end_datetime=record.eff - DELTA,
            modification=record.mod
        )
        towns.update_successors(old_town, from_town=current_town)
        towns.delete(ancient_town)
        towns.update_successors(ancient_town, to_town=old_town)
        if is_new_entry:
            # In that particular case we would like to update the initial
            # entry that has been created with the wrong county code.
            initial_town = towns.get_current(record.depcom, START_DATETIME)
            initial_updated_town = initial_town.generate(
                id=compute_id(record.depanc, START_DATE),
                dep=record.depanc[:2],
                com=record.depanc[2:],
                depcom=record.depanc
            )
            towns.upsert(initial_updated_town)
            towns.delete(initial_town)
    else:
        # This particular case happens when there are multiple county
        # changes, for instance with Châteaufort.
        old_town = ancient_town.generate(
            id=compute_id(ancient_town.depcom, START_DATE),
            start_datetime=START_DATETIME,
            end_datetime=record.eff - DELTA,
            modification=record.mod
        )
    old_town = old_town.add_successor(new_town.id)
    towns.upsert(old_town)


@in_case_of(CHANGE_COUNTY_CREATION)
def change_county_creation(towns, record):
    """Only for Gernicourt and Fresne-sur-Loire.

    In both cases the change is coupled with a fusion, hence the 1ms lifetime.
    """
    current_town = towns.get_current(record.depcom, record.eff)
    old_town = towns.get_current(record.depanc, record.eff)
    new_town = current_town.generate(
        id=compute_id(record.depcom, record.effdate),
        depcom=record.depcom,
        dep=record.depcom[:2],
        com=record.depcom[2:],
        start_datetime=record.eff,
        end_datetime=record.eff + DELTA  # Only 1ms lifetime to keep track.
    )
    towns.upsert(new_town)
    towns.delete(current_town)
    old_town_new = old_town.generate(
        end_datetime=record.eff - DELTA,
        successors=new_town.id,
        modification=record.mod
    )
    towns.upsert(old_town_new)
    towns.update_successors(new_town, from_town=old_town_new)


@in_case_of(OBSOLETE)
def obsolete(towns, record):
    current_town = towns.get_current(record.depcom, record.eff)

    old_town = current_town.generate(
        end_datetime=record.eff - DELTA,
        modification=record.mod
    )
    towns.upsert(old_town)


def compute(towns, history):
    log.info('Computing history from actions')
    for record in history:
        try:
            ACTIONS.get(record.mod, lambda a, b: a)(towns, record)
        except Exception as e:
            print(record)
            raise e

    # Sort towns by id at the end of all computations, useful for tests.
    towns.sort_by_id()
