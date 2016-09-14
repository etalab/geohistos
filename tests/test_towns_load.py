import datetime

import pytest

from geohisto.loaders import load_towns


@pytest.fixture
def towns():
    return load_towns()


def test_initial_load(towns):
    assert len(towns) == 39166


def test_contains_arles(towns):
    arles = towns.filter(depcom='13004')[0]
    assert arles.dep == '13'
    assert arles.com == '004'
    assert arles.start_date == datetime.date(1942, 1, 1)
    assert arles.end_date == datetime.date(9999, 1, 1)
    assert arles.successors == ''
    assert arles.actual == 1
    assert arles.nccenr == 'Arles'


def test_convert_name(towns):
    la_breole = towns.filter(depcom='04033')[0]
    assert la_breole.nccenr == 'La Bréole'
    lescale = towns.filter(depcom='04079')[0]
    assert lescale.nccenr == "L'Escale"
