import csv
import logging

from collections import defaultdict

from .constants import (
    CREATION_DELEGATED_POLE, CREATION_NOT_DELEGATED_POLE, END_DATE,
    END_DATETIME, START_DATE, START_DATETIME
)
from .models import Record, Town, Towns
from .utils import (
    compute_id, convert_date, convert_datetime, convert_name_with_article,
    iter_over_insee_csv_file
)

log = logging.getLogger(__name__)


def load_towns(filename='sources/France2018.txt'):
    """
    Load all towns from `filename` into an OrderedDict of `Town`s namedtuples.

    Warning: default file contains outdated towns but NOT renamed ones.
    """
    log.info('Loading towns')
    towns = Towns()
    for i, line in iter_over_insee_csv_file(filename):
        actual = int(line['ACTUAL'])
        if actual == 9:  # Cantonal fraction.
            continue  # Skip for the moment.
        town = Town(
            id=compute_id(line['DEP'] + line['COM'], START_DATE),
            depcom=line['DEP'] + line['COM'],
            actual=actual,
            modification=0,
            ancestors='',
            successors='',
            start_date=START_DATE,
            end_date=END_DATE,
            start_datetime=START_DATETIME,
            end_datetime=END_DATETIME,
            dep=line['DEP'],
            com=line['COM'],
            nccenr=convert_name_with_article(line),
            population='NULL',
            parents=''
        )
        towns[town.id] = town
    return towns


def load_history(filename='sources/historiq2018.txt'):
    """Load all towns from `filename` into a list of `Record`s."""
    log.info('Loading history')
    history = []
    last_log = defaultdict(int)
    for i, line in iter_over_insee_csv_file(filename):
        effdate = convert_date(line['EFF'])
        depcom = line['DEP'] + line['COM']
        mod = int(line['MOD'])
        last = None
        # We need to know which one of the record is the last in case
        # of `CREATION_*_POLE` to perform clean up only on the last one.
        if mod in (CREATION_DELEGATED_POLE, CREATION_NOT_DELEGATED_POLE):
            id_ = depcom + effdate.isoformat()
            last_log[id_] += 1
            last = id_ in last_log and last_log[id_] == int(line['NBCOM'])
        record = Record(
            depcom=depcom,
            mod=mod,
            eff=convert_datetime(line['EFF']),
            effdate=effdate,
            nccoff=convert_name_with_article(line, 'NCCOFF', 'TNCCOFF'),
            nccanc=convert_name_with_article(line, 'NCCANC', 'TNCCANC'),
            comech=line['COMECH'],
            dep=line['DEP'],
            com=line['COM'],
            depanc=line['DEPANC'],
            last=last,
        )
        history.append(record)
    return history


def load_population_from(filename):
    """
    Load populations from `filename` into a dict.

    We use the name `DEPCOM` + `LIBMIN` as key because we cannot rely on
    `DEPCOM` only, it is not unique (recycled on towns' merges).
    """
    populations = {}
    with open(filename) as population:
        for item in csv.DictReader(population, delimiter=';'):
            populations[item['DEPCOM'] + item['LIBMIN']] = item['PMUN13']
    return populations


def load_populations():
    """Load all populations into a dedicated dict."""
    log.info('Loading populations')
    return {
        'metropole': load_population_from('sources/population_metropole.csv'),
        'arrondissements': load_population_from(
            'sources/population_arrondissements.csv'),
        'dom': load_population_from('sources/population_dom.csv'),
        'mortes': load_population_from('sources/population_mortes.csv')
    }


def load_counties(filename='exports/departements/departements.csv'):
    """Load counties from `filename` into a dict."""
    log.info('Loading counties')
    counties = defaultdict(list)
    with open(filename) as counties_csv:
        for line in csv.DictReader(counties_csv):
            counties[line['insee_code']].append(line)
    return counties
