#!/usr/bin/env python
"""
Utils in use to convert/compute historical data.

Most of the cryptic keys in that script are documented here:
http://www.insee.fr/fr/methodes/nomenclatures/cog/documentation.asp↩
?page=telechargement/2016/doc/doc_variables.htm
"""
from datetime import date

from constants import START_DATE, END_DATE


def chunks(string, num):
    """Split a given `string` by `num` characters and return a list."""
    return [string[start:start+num] for start in range(0, len(string), num)]


def convert_date(string):
    """
    Convert '01-01-2016' to a Python `datetime.date` object.

    For the particular case where there are multiple dates within the
    same key, we return a list of `datetime.date` object.
    """
    if not string or string == '         .':  # Yes, it happens once!
        return ''

    if len(string) > 10:
        return [convert_date(chunk) for chunk in chunks(string, 10)]

    return date(*reversed([int(i) for i in string.split('-')]))


def convert_leg(string):
    """
    Convert 'L01-01-2016' to a Python tuple ('L', `datetime.date`).

    For the particular case where there are multiple dates within the
    same key, we return a list of tuples.
    """
    if not string:
        return ''

    if len(string) > 11:
        return [convert_leg(chunk) for chunk in chunks(string, 11)]

    return string[0], convert_date(string[1:])


def has_been_hard_renamed(town, history):
    """Return `True` in case of a rename without any other operation."""
    return int(history['MOD']) in (100, 110)


def has_been_restablished(town, history):
    """Return `True` in case of a restablishement."""
    return int(history['MOD']) in (210, 230)


def has_been_renamed(town, history):
    """Return `True` in case of a rename with the same INSEE code."""
    return (int(history['MOD']) in (120, 331)
            and history['NCCOFF'] != town[0]['NCCENR'])

def has_been_deleted(town, history):
    """Return `True` in case of a deletion."""
    return (int(history['MOD']) == 300)


def has_ancestor(town, towns, history):
    """Return `True` in case of a merge with a different name."""
    return (int(history['MOD']) in (320, 340, 341)
            and town[0]['NCCENR'] != towns[history['COMECH']][0]['NCCENR'])


def has_changed_county(town, towns, history):
    """Return `True` in case of a move to another county."""
    return int(history['MOD']) in (410, 411)


def add_same_ancestor(town, history):
    """
    Enrich the `town` with a copy of itself.

    Keeping the old name and updating dates.
    """
    current = town[0]
    same_ancestor = current.copy()
    same_ancestor['ANCESTORS'] = []
    same_ancestor['END_DATE'] = history['EFF']
    # Take the `OFF`icial name if different from actual,
    # otherwise fallback on the `ANC`ient one.
    if same_ancestor['NCCENR'] != history['NCCOFF']:
        same_ancestor['NCCENR'] = history['NCCOFF']
    else:
        same_ancestor['NCCENR'] = history['NCCANC']
    current['START_DATE'] = history['EFF']
    town.append(same_ancestor)


def add_ancestor(town, towns, history):
    """Add an ancestor to a given `town`, updating dates."""
    current = town[0]
    ancestor = towns[history['COMECH']][0]
    # Only update consistent ranges.
    if ancestor['START_DATE'] < history['EFF']:
        ancestor['END_DATE'] = history['EFF']
    current['START_DATE'] = history['EFF']
    current['ANCESTORS'].append(history['COMECH'])


def add_neighbor(town, towns, history):
    """
    Add a neighbor to a given `town`, updating dates.

    By neighbor, we mean an adjacent county.
    """
    current = town[0]
    neighbor = current.copy()
    neighbor['END_DATE'] = history['EFF']
    neighbor['DEP'] = history['DEPANC'][:2]
    neighbor['COM'] = history['DEPANC'][2:]
    current['START_DATE'] = history['EFF']
    current['NEIGHBORS'].append(neighbor)
    # Handle special cases of `Châteaufort` and `Toussus-le-Noble`,
    # these towns have switched twice from one county to another.
    if history['DEPANC'] not in ('78143', '78620'):
        # Finally change the end date of the reference town
        # for clean removal when the result is written.
        towns[history['DEPANC']][0]['END_DATE'] = history['EFF']


def restablish_town(town, towns, history):
    """Restablish a previously merged town."""
    current = town[0]
    current['END_DATE'] = END_DATE
    current['START_DATE'] = history['EFF']
    # Avoid duplicates.
    if history['COMECH'] not in current['ANCESTORS']:
        current['ANCESTORS'].append(history['COMECH'])

def delete_town(town, history):
    """Delete a town."""
    current = town[0]
    current['END_DATE'] = history['EFF']
    current['DELETED'] = True

def compute_name(town):
    """Return the `town` name with optional article."""
    if town['ARTMIN']:
        # Special `L'` case, all other article require a space.
        extra_space = int(town['TNCC']) != 5
        return '{article}{extra_space}{name}'.format(
            article=town['ARTMIN'][1:-1],
            extra_space=' ' if extra_space else '',
            name=town['NCCENR']
        )
    else:
        return town['NCCENR']


def compute_population(populations, population_id,
                       towns, town=None, key='metropole'):
    """
    Retrieve the population from `populations` dict cast as an integer.

    Fallback on `arrondissements` and `dom` if no population is found.
    Finally, a population of `0` is added for listed dead towns.
    In case of unknown population the value `NULL` is returned.

    If the `population_id` is missing and `town` is available, we try
    to compute the population based on ancestors (renames + merges).
    The `key` is useful for the recursivity of the function in order to
    explore different `populations` sub-dictionnaries.
    """
    # If the population is already available, return it.
    population = int(populations[key].get(population_id, 0))
    if population:
        return population
    elif town is None:
        return 'NULL'

    # Otherwise sum populations from renamed + ancestors towns.
    population = 0
    for t in town[1:]:
        population_id = t['DEP'] + t['COM'] + t['NCCENR']
        try:
            population += compute_population(populations, population_id, towns)
        except TypeError:  # Returned population equals 'NULL'
            pass
    for ancestor in town[0]['ANCESTORS']:
        # TODO: restrict to direct ancestors only?
        ancestor = towns[ancestor][0]
        population_id = ancestor['DEP'] + ancestor['COM'] + ancestor['NCCENR']
        try:
            population += compute_population(populations, population_id, towns)
        except TypeError:  # Returned population equals 'NULL'
            pass
    if not population:
        try:
            population += compute_population(
                populations, population_id, towns, key='arrondissements')
        except TypeError:  # Returned population equals 'NULL'
            pass
    if not population:
        try:
            population += compute_population(
                populations, population_id, towns, key='dom')
        except TypeError:  # Returned population equals 'NULL'
            pass
    if not population and population_id not in populations['mortes']:
        population = 'NULL'

    return population
