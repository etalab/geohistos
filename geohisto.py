#!/usr/bin/env python
"""
Most of the cryptic keys in that script are documented here:
http://www.insee.fr/fr/methodes/nomenclatures/cog/documentation.asp↩
?page=telechargement/2016/doc/doc_variables.htm
"""
import csv
import subprocess
import unittest
from collections import defaultdict
from itertools import islice

from constants import START_DATE, END_DATE
from utils import (
    convert_date, convert_leg, compute_name, compute_population,
    has_been_hard_renamed, add_same_ancestor, has_been_renamed,
    add_ancestor, has_ancestor, has_changed_county, add_neighbor,
    has_been_restablished, has_been_deleted, restablish_town, delete_town
)


def load_towns_from(filename):
    """
    Load all towns from `filename` into a dict of lists.

    Warning: that file contains outdated towns but NOT renamed ones.
    """
    towns = defaultdict(list)
    with open(filename, encoding='cp1252') as file:
        for town in csv.DictReader(file, delimiter='\t'):
            actual = int(town['ACTUAL'])
            town['ANCESTORS'] = []
            town['NEIGHBORS'] = []
            town['START_DATE'] = START_DATE
            town['END_DATE'] = END_DATE
            town['DELETED'] = False
            if actual == 9:  # Cantonal fraction.
                continue  # Skip for the moment.
            # Beware that the `DEP` + `COM` combination is not unique,
            # hence the defaultdict list.
            towns[town['DEP'] + town['COM']].append(town)
    return towns


def compute_history_from(filename, towns):
    """
    Compute ancestors for each `towns` for renamed and merged towns.

    We are looping over the `filename` to detect renaming and merging
    actions within the past, enriching the given town with dates
    of these events and keys of ascendants.
    """
    with open(filename, encoding='cp1252') as file:
        for history in csv.DictReader(file, delimiter='\t'):
            town = towns[history['DEP'] + history['COM']]
            history['DTR'] = convert_date(history['DTR'])
            history['EFF'] = convert_date(history['EFF'])
            history['JO'] = convert_date(history['JO'])
            history['LEG'] = convert_leg(history['LEG'])
            if has_been_hard_renamed(town, history):
                add_same_ancestor(town, history)
            elif has_been_renamed(town, history):
                add_same_ancestor(town, history)
            elif has_ancestor(town, towns, history):
                add_ancestor(town, towns, history)
            elif has_changed_county(town, towns, history):
                add_neighbor(town, towns, history)
            elif has_been_restablished(town, history):
                restablish_town(town, towns, history)
            elif has_been_deleted(town, history):
                delete_town(town, history)
    return towns


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


def write_results_on(filename, towns, populations):
    """
    Write the `filename` with CSV formatted informations.

    With the generated file, you will be able to retrace the history of
    a given INSEE code with renames and merges.

    Each town has an associated population, sometimes computed from
    population of ancestors.
    """
    with open(filename, 'w') as csvfile:
        fieldnames = [
            'DIRECTION', 'INSEE_CODE', 'NAME', 'START_DATE', 'END_DATE',
            'POPULATION'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        write = writer.writerow

        for id, town in sorted(towns.items()):
            current = town[0]
            # Root elements are the one still in use, skip others.
            if not current['DELETED'] and current['END_DATE'] != END_DATE:
                # if current['ACTUAL'] != '1':
                #     print(current)
                continue
            name = compute_name(current)
            population_id = id + name
            population = compute_population(
                populations, population_id, towns, town)
            # Main entry.
            write({
                'DIRECTION': '--',
                'INSEE_CODE': id,
                'NAME': name,
                'START_DATE': current['START_DATE'],
                'END_DATE': current['END_DATE'],
                'POPULATION': population
            })
            # Add an entry for each rename (same id).
            for t in town[1:]:
                name = compute_name(t)
                population_id = id + name
                population = compute_population(
                    populations, population_id, towns)
                write({
                    'DIRECTION': '<-',
                    'INSEE_CODE': id,
                    'NAME': name,
                    'START_DATE': t['START_DATE'],
                    'END_DATE': t['END_DATE'],
                    'POPULATION': population
                })

            # Add an entry for each neighbor (different id).
            for neighbor in current['NEIGHBORS']:
                id = neighbor['DEP'] + neighbor['COM']
                name = compute_name(neighbor)
                population_id = id + name
                population = compute_population(
                    populations, population_id, towns)
                write({
                    'DIRECTION': '<<',
                    'INSEE_CODE': id,
                    'NAME': name,
                    'START_DATE': neighbor['START_DATE'],
                    'END_DATE': neighbor['END_DATE'],
                    'POPULATION': population
                })

            # Add an entry for each ancestor (different id).
            for ancestor in current['ANCESTORS']:
                ancestor = towns[ancestor][0]
                id = ancestor['DEP'] + ancestor['COM']
                name = compute_name(ancestor)
                population_id = id + name
                population = compute_population(
                    populations, population_id, towns)
                write({
                    'DIRECTION': '->',
                    'INSEE_CODE': id,
                    'NAME': name,
                    'START_DATE': ancestor['START_DATE'],
                    'END_DATE': ancestor['END_DATE'],
                    'POPULATION': population
                })


def generate_head_results_from(filename, nb_of_lines=100):
    """
    Equivalent of `head` using Python.

    The passed `filename` will have a `_head` suffix added for the
    newly generated extract.
    """
    filepath, extension = filename.split('.')
    filename_out = filepath + '_head.' + extension
    with open(filename) as csvfile, \
            open(filename_out, 'w') as csvfileout:
        head = islice(csvfile, nb_of_lines)
        csvfileout.write(''.join(head))


def check_generated_results_from(filename):
    test_case = unittest.TestCase()
    base_command = 'cat {filename} | grep -e "{{term}}" | wc -l'.format(
        filename=filename)
    extra_args = {'executable': '/bin/bash', 'shell': True}

    # Check the number of lines with current towns.
    output = subprocess.check_output(
        base_command.format(term='--'), **extra_args)
    test_case.assertEqual(int(output.strip()), 35962)  # Should be 35930.

    # Check the number of lines with arrondissements.
    output = subprocess.check_output(
        base_command.format(term='Arrondissement'), **extra_args)
    test_case.assertEqual(int(output.strip()), 20 + 9 + 16)

    # Check a new town from 2016 is present.
    new_2016_town = '--,01015,Arboys en Bugey,2016-01-01,2020-01-01,631'
    output = subprocess.check_output(
        base_command.format(term=new_2016_town), **extra_args)
    test_case.assertEqual(int(output.strip()), 1)

    # Check it's a rename from a previous INSEE code.
    rename_2016_town = '<-,01015,Arbignieu,1942-01-01,2016-01-01,495'
    output = subprocess.check_output(
        base_command.format(term=rename_2016_town), **extra_args)
    test_case.assertEqual(int(output.strip()), 1)

    # Check it's a merge too from a previous INSEE code.
    merge_2016_town = '->,01340,Saint-Bois,1942-01-01,2016-01-01,136'
    output = subprocess.check_output(
        base_command.format(term=merge_2016_town), **extra_args)
    test_case.assertEqual(int(output.strip()), 1)

if __name__ == '__main__':
    towns = load_towns_from('sources/france2016.txt')
    towns = compute_history_from('sources/historiq2016.txt', towns)
    populations = {}
    populations['metropole'] = load_population_from(
        'sources/population_metropole.csv')
    populations['arrondissements'] = load_population_from(
        'sources/population_arrondissements.csv')
    populations['dom'] = load_population_from(
        'sources/population_dom.csv')
    populations['mortes'] = load_population_from(
        'sources/population_mortes.csv')
    write_results_on('exports/towns/towns.csv', towns, populations)
    generate_head_results_from('exports/towns/towns.csv')
    check_generated_results_from('exports/towns/towns.csv')
