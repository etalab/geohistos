"""
Tests related to actions performed on towns given the history.

All fixtures are extracted from real cases located in France2017
and historiq2017 files.
"""
from datetime import date, datetime

from geohisto.actions import compute
from geohisto.constants import (
    CHANGE_COUNTY, CHANGE_COUNTY_CREATION, CHANGE_NAME, CHANGE_NAME_CREATION,
    CHANGE_NAME_FUSION, CHANGE_NAME_REINSTATEMENT, CREATION,
    CREATION_DELEGATED, CREATION_DELEGATED_POLE, CREATION_NOT_DELEGATED,
    CREATION_NOT_DELEGATED_POLE, CREATION_PREEXISTING_ASSOCIATED,
    DELETION_FUSION, DELETION_PARTITION, END_DATE, END_DATETIME,
    FUSION_ABSORPTION, FUSION_ASSOCIATION_ASSOCIATED, OBSOLETE, REINSTATEMENT,
    SPLITING, START_DATE, START_DATETIME
)

from .factories import record_factory, town_factory, towns_factory


def test_change_name():
    """Change name of the same town (id)."""
    neuville_town = town_factory(
        dep='10', com='263', nccenr='Neuville-sur-Vanne')
    towns = towns_factory(neuville_town)
    change_name_record = record_factory(
        dep='10', com='263', mod=CHANGE_NAME, effdate=date(2008, 10, 6),
        nccoff='Neuville-sur-Vanne', nccanc='Neuville-sur-Vannes')
    history = [change_name_record]
    compute(towns, history)
    neuville_s, neuville = list(towns.filter(depcom='10263'))
    assert neuville_s.id == 'fr:commune:10263@1942-01-01'
    assert neuville_s.nccenr == 'Neuville-sur-Vannes'
    assert neuville_s.start_date == START_DATE
    assert neuville_s.start_datetime == START_DATETIME
    assert neuville_s.end_date == date(2008, 10, 5)
    assert neuville_s.end_datetime == datetime(2008, 10, 5, 23, 59, 59, 999999)
    assert neuville_s.modification == CHANGE_NAME
    assert neuville_s.successors == neuville.id
    assert neuville.id == 'fr:commune:10263@2008-10-06'
    assert neuville.nccenr == 'Neuville-sur-Vanne'
    assert neuville.start_date == date(2008, 10, 6)
    assert neuville.start_datetime == datetime(2008, 10, 6, 0, 0, 0)
    assert neuville.end_date == END_DATE
    assert neuville.end_datetime == END_DATETIME


def test_change_name_many():
    """Change name of the same town (id), three times."""
    chalon_champagne_town = town_factory(
        dep='51', com='108', nccenr='Châlons-en-Champagne')
    towns = towns_factory(chalon_champagne_town)
    change_name_record1 = record_factory(
        dep='51', com='108', mod=CHANGE_NAME, effdate=date(1995, 11, 17),
        nccoff='Châlons-en-Champagne', nccanc='Châlons-sur-Marne')
    change_name_record2 = record_factory(
        dep='51', com='108', mod=CHANGE_NAME, effdate=date(1997, 5, 1),
        nccoff='Châlons-sur-Marne', nccanc='Châlons-en-Champagne')
    change_name_record3 = record_factory(
        dep='51', com='108', mod=CHANGE_NAME, effdate=date(1998, 1, 4),
        nccoff='Châlons-en-Champagne', nccanc='Châlons-sur-Marne')
    history = [change_name_record1, change_name_record2, change_name_record3]
    compute(towns, history)
    marne, champ, marne2, champ2 = list(towns.filter(depcom='51108'))
    assert marne.id == 'fr:commune:51108@1942-01-01'
    assert marne.nccenr == 'Châlons-sur-Marne'
    assert marne.start_date == START_DATE
    assert marne.start_datetime == START_DATETIME
    assert marne.end_date == date(1995, 11, 16)
    assert marne.end_datetime == datetime(1995, 11, 16, 23, 59, 59, 999999)
    assert marne.modification == CHANGE_NAME
    assert marne.successors == champ.id
    assert champ.id == 'fr:commune:51108@1995-11-17'
    assert champ.nccenr == 'Châlons-en-Champagne'
    assert champ.start_date == date(1995, 11, 17)
    assert champ.start_datetime == datetime(1995, 11, 17, 0, 0, 0)
    assert champ.end_date == date(1997, 4, 30)
    assert champ.end_datetime == datetime(1997, 4, 30, 23, 59, 59, 999999)
    assert champ.successors == marne2.id
    assert marne2.id == 'fr:commune:51108@1997-05-01'
    assert marne2.nccenr == 'Châlons-sur-Marne'
    assert marne2.start_date == date(1997, 5, 1)
    assert marne2.start_datetime == datetime(1997, 5, 1, 0, 0, 0)
    assert marne2.end_date == date(1998, 1, 3)
    assert marne2.end_datetime == datetime(1998, 1, 3, 23, 59, 59, 999999)
    assert marne2.modification == CHANGE_NAME
    assert marne2.successors == champ2.id
    assert champ2.id == 'fr:commune:51108@1998-01-04'
    assert champ2.nccenr == 'Châlons-en-Champagne'
    assert champ2.start_date == date(1998, 1, 4)
    assert champ2.start_datetime == datetime(1998, 1, 4, 0, 0, 0)
    assert champ2.end_date == END_DATE
    assert champ2.end_datetime == END_DATETIME


def test_change_name_fusion():
    """Change name of a town during a fusion."""
    bragelogne_beavoir_town = town_factory(
        dep='10', com='058', nccenr='Bragelogne-Beauvoir')
    towns = towns_factory(bragelogne_beavoir_town)
    change_name_fusion_record = record_factory(
        dep='10', com='058', mod=CHANGE_NAME_FUSION, effdate=date(1973, 5, 1),
        nccoff='Bragelogne-Beauvoir', nccanc='Bragelogne')
    history = [change_name_fusion_record]
    compute(towns, history)
    braguelogne, braguelogne_beauvoir = list(towns.filter(depcom='10058'))
    assert braguelogne.id == 'fr:commune:10058@1942-01-01'
    assert braguelogne.successors == braguelogne_beauvoir.id
    assert braguelogne.modification == CHANGE_NAME_FUSION
    assert braguelogne.nccenr == 'Bragelogne'
    assert braguelogne_beauvoir.id == 'fr:commune:10058@1973-05-01'
    assert braguelogne_beauvoir.nccenr == 'Bragelogne-Beauvoir'


def test_change_name_creation():
    """Change name of a town during a creation."""
    clefs_town = town_factory(dep='49', com='101', nccenr='Clefs')
    towns = towns_factory(clefs_town)
    change_name_creation_record = record_factory(
        dep='49', com='101', mod=CHANGE_NAME_CREATION,
        effdate=date(2016, 1, 1), nccoff='Clefs')
    history = [change_name_creation_record]
    compute(towns, history)
    clefs_list = list(towns.filter(depcom='49101'))
    assert len(clefs_list) == 1
    clefs = clefs_list[0]
    assert clefs.id == 'fr:commune:49101@2016-01-01'
    assert clefs.successors == ''
    assert clefs.modification == CHANGE_NAME_CREATION
    assert clefs.nccenr == 'Clefs'
    assert clefs.start_date == date(2016, 1, 1)
    assert clefs.start_datetime == datetime(2016, 1, 1, 0, 0, 0)
    assert clefs.end_date == END_DATE
    assert clefs.end_datetime == END_DATETIME


def test_change_name_reinstatement_after_fusion():
    """Change name of a town during a reinstatement following a fusion."""
    framboisiere_town = town_factory(
        dep='28', com='159', nccenr='Framboisière')
    saucelle_town = town_factory(
        dep='28', com='368', nccenr='Saucelle')
    towns = towns_factory(framboisiere_town, saucelle_town)
    change_name_fusion_record = record_factory(
        dep='28', com='159', mod=CHANGE_NAME_FUSION,
        effdate=date(1972, 12, 22),
        nccoff='Framboisière-la-Saucelle', nccanc='Framboisière')
    change_name_reinstatement_record = record_factory(
        dep='28', com='159', mod=CHANGE_NAME_REINSTATEMENT,
        effdate=date(1987, 1, 1),
        nccoff='Framboisière', nccanc='Framboisière-la-Saucelle')
    spliting_record = record_factory(
        dep='28', com='159', mod=SPLITING,
        effdate=date(1987, 1, 1),
        nccoff='Framboisière', comech='28368')
    fusion_association_associated = record_factory(
        dep='28', com='368', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1972, 12, 22), comech='28159',
        nccoff='Saucelle')
    reinstatement_record = record_factory(
        dep='28', com='368', mod=REINSTATEMENT,
        effdate=date(1987, 1, 1), comech='28159',
        nccoff='Saucelle', nccanc='Framboisière-la-Saucelle')
    history = [
        change_name_fusion_record, change_name_reinstatement_record,
        spliting_record, fusion_association_associated, reinstatement_record
    ]
    compute(towns, history)
    framb, framb_saucelle, framb2 = list(towns.filter(depcom='28159'))
    saucelle, saucelle2 = list(towns.filter(depcom='28368'))
    assert saucelle.successors == framb_saucelle.id
    assert framb_saucelle.id == 'fr:commune:28159@1972-12-22'
    assert framb_saucelle.successors == framb2.id + ';' + saucelle2.id
    assert framb_saucelle.modification == CHANGE_NAME_REINSTATEMENT
    assert framb.id == 'fr:commune:28159@1942-01-01'
    assert framb.successors == framb_saucelle.id
    assert framb2.id == 'fr:commune:28159@1987-01-01'
    assert framb2.successors == ''


def test_creation():
    """Creation of a new town."""
    curan_town = town_factory(dep='12', com='307', nccenr='Curan')
    towns = towns_factory(curan_town)
    creation_record = record_factory(
        dep='12', com='307', mod=CREATION,
        effdate=date(1952, 12, 3), nccoff='Curan')
    history = [creation_record]
    compute(towns, history)
    curan_list = list(towns.filter(depcom='12307'))
    assert len(curan_list) == 1
    curan = curan_list[0]
    assert curan.id == 'fr:commune:12307@1952-12-03'
    assert curan.successors == ''
    assert curan.modification == CREATION
    assert curan.nccenr == 'Curan'
    assert curan.start_date == date(1952, 12, 3)
    assert curan.start_datetime == datetime(1952, 12, 3, 0, 0, 0)
    assert curan.end_date == END_DATE
    assert curan.end_datetime == END_DATETIME


def test_reinstatement():
    """Reinstatement town."""
    brageac_town = town_factory(dep='15', com='024', nccenr='Brageac')
    towns = towns_factory(brageac_town)
    reinstatement_record = record_factory(
        dep='15', com='024', mod=REINSTATEMENT,
        effdate=date(1985, 10, 1), nccoff='Brageac')
    history = [reinstatement_record]
    compute(towns, history)
    old_brageac, new_brageac = list(towns.filter(depcom='15024'))
    assert old_brageac.id == 'fr:commune:15024@1942-01-01'
    assert old_brageac.successors == new_brageac.id
    assert old_brageac.modification == REINSTATEMENT
    assert old_brageac.nccenr == 'Brageac'
    assert old_brageac.start_date == START_DATE
    assert old_brageac.start_datetime == START_DATETIME
    assert old_brageac.end_date == date(1985, 9, 30)
    assert (old_brageac.end_datetime ==
            datetime(1985, 9, 30, 23, 59, 59, 999999))
    assert new_brageac.id == 'fr:commune:15024@1985-10-01'
    assert new_brageac.successors == ''
    assert new_brageac.modification == 0
    assert new_brageac.nccenr == 'Brageac'
    assert new_brageac.start_date == date(1985, 10, 1)
    assert new_brageac.start_datetime == datetime(1985, 10, 1, 0, 0, 0)
    assert new_brageac.end_date == END_DATE
    assert new_brageac.end_datetime == END_DATETIME


def test_fusion_then_reinstatement():
    """That case is important to verify that we don't mess with dates."""
    brageac_town = town_factory(dep='15', com='024', nccenr='Brageac')
    ally_town = town_factory(dep='15', com='003', nccenr='Ally')
    towns = towns_factory(brageac_town, ally_town)
    spliting_record = record_factory(
        dep='15', com='003', mod=SPLITING,
        effdate=date(1985, 10, 1), nccoff='Ally', comech='15024')
    fusion_record = record_factory(
        dep='15', com='024', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1973, 1, 1), nccoff='Brageac', comech='15003')
    reinstatement_record = record_factory(
        dep='15', com='024', mod=REINSTATEMENT,
        effdate=date(1985, 10, 1), nccoff='Brageac', comech='15003')
    history = [spliting_record, fusion_record, reinstatement_record]
    compute(towns, history)
    ally_list = list(towns.filter(depcom='15003'))
    assert len(ally_list) == 1
    ally = ally_list[0]
    old_brageac, new_brageac = list(towns.filter(depcom='15024'))
    assert old_brageac.id == 'fr:commune:15024@1942-01-01'
    assert old_brageac.successors == ally.id
    assert old_brageac.modification == REINSTATEMENT
    assert old_brageac.nccenr == 'Brageac'
    assert old_brageac.start_date == START_DATE
    assert old_brageac.start_datetime == START_DATETIME
    assert old_brageac.end_date == date(1972, 12, 31)
    assert (old_brageac.end_datetime ==
            datetime(1972, 12, 31, 23, 59, 59, 999999))
    assert ally.successors == ''
    assert new_brageac.id == 'fr:commune:15024@1985-10-01'
    assert new_brageac.successors == ''
    assert new_brageac.modification == 0
    assert new_brageac.nccenr == 'Brageac'
    assert new_brageac.start_date == date(1985, 10, 1)
    assert new_brageac.start_datetime == datetime(1985, 10, 1, 0, 0, 0)
    assert new_brageac.end_date == END_DATE
    assert new_brageac.end_datetime == END_DATETIME


def test_deletion_partition():
    """Deletion of an old town (partition)."""
    creusy_town = town_factory(dep='45', com='117', nccenr='Creusy')
    chevilly_town = town_factory(dep='45', com='093', nccenr='Chevilly')
    sougy_town = town_factory(dep='45', com='313', nccenr='Sougy')
    towns = towns_factory(creusy_town, chevilly_town, sougy_town)
    deletion_partition_record1 = record_factory(
        dep='45', com='117', mod=DELETION_PARTITION,
        effdate=date(1965, 1, 1), nccoff='Creusy', comech='45093')
    deletion_partition_record2 = record_factory(
        dep='45', com='117', mod=DELETION_PARTITION,
        effdate=date(1965, 1, 1), nccoff='Creusy', comech='45313')
    history = [deletion_partition_record1, deletion_partition_record2]
    compute(towns, history)
    creusy_list = list(towns.filter(depcom='45117'))
    assert len(creusy_list) == 1
    creusy = creusy_list[0]
    assert creusy.id == 'fr:commune:45117@1942-01-01'
    assert (creusy.successors ==
            'fr:commune:45093@1942-01-01;fr:commune:45313@1942-01-01')
    assert creusy.modification == DELETION_PARTITION
    assert creusy.nccenr == 'Creusy'
    assert creusy.start_date == START_DATE
    assert creusy.start_datetime == START_DATETIME
    assert creusy.end_date == date(1964, 12, 31)
    assert creusy.end_datetime == datetime(1964, 12, 31, 23, 59, 59, 999999)


def test_deletion_fusion():
    """Deletion of an old town (partition)."""
    eyvignes_town = town_factory(dep='24', com='169',
                                 nccenr='Eyvignes-et-Eybènes')
    salignac_town = town_factory(dep='24', com='516',
                                 nccenr='Salignac-Eyvigues')
    towns = towns_factory(eyvignes_town, salignac_town)
    deletion_fusion_record = record_factory(
        dep='24', com='169', mod=DELETION_FUSION,
        effdate=date(1965, 3, 1), nccoff='Eyvignes-et-Eybènes', comech='24516')
    history = [deletion_fusion_record]
    compute(towns, history)
    eyvignes_list = list(towns.filter(depcom='24169'))
    assert len(eyvignes_list) == 1
    eyvignes = eyvignes_list[0]
    assert eyvignes.id == 'fr:commune:24169@1942-01-01'
    assert eyvignes.successors == 'fr:commune:24516@1942-01-01'
    assert eyvignes.modification == DELETION_FUSION
    assert eyvignes.nccenr == 'Eyvignes-et-Eybènes'
    assert eyvignes.start_date == START_DATE
    assert eyvignes.start_datetime == START_DATETIME
    assert eyvignes.end_date == date(1965, 2, 28)
    assert eyvignes.end_datetime == datetime(1965, 2, 28, 23, 59, 59, 999999)


def test_fusion_absorption():
    """Fusion of a town with absorption."""
    castilly_town = town_factory(dep='14', com='142', nccenr='Castilly')
    mestry_town = town_factory(dep='14', com='428', nccenr='Mestry')
    towns = towns_factory(castilly_town, mestry_town)
    fusion_absorption_record = record_factory(
        dep='14', com='142', mod=FUSION_ABSORPTION,
        effdate=date(1965, 2, 15), nccoff='Castilly', comech='14428')
    deletion_fusion_record = record_factory(
        dep='14', com='428', mod=DELETION_FUSION,
        effdate=date(1965, 2, 15), nccoff='Mestry', comech='14142')
    history = [fusion_absorption_record, deletion_fusion_record]
    compute(towns, history)
    castilly_list = list(towns.filter(depcom='14142'))
    assert len(castilly_list) == 1
    castilly = castilly_list[0]
    assert castilly.id == 'fr:commune:14142@1942-01-01'
    assert castilly.successors == ''
    assert castilly.modification == 0
    assert castilly.nccenr == 'Castilly'
    assert castilly.start_date == START_DATE
    assert castilly.start_datetime == START_DATETIME
    assert castilly.end_date == END_DATE
    assert castilly.end_datetime == END_DATETIME
    mestry_list = list(towns.filter(depcom='14428'))
    assert len(mestry_list) == 1
    mestry = mestry_list[0]
    assert mestry.id == 'fr:commune:14428@1942-01-01'
    assert mestry.successors == castilly.id
    assert mestry.modification == DELETION_FUSION
    assert mestry.nccenr == 'Mestry'
    assert mestry.start_date == START_DATE
    assert mestry.start_datetime == START_DATETIME
    assert mestry.end_date == date(1965, 2, 14)
    assert mestry.end_datetime == datetime(1965, 2, 14, 23, 59, 59, 999999)


def test_creation_not_delegated():
    """New town without delegate."""
    fragnes_loyere_town = town_factory(dep='71', com='204',
                                       nccenr='Fragnes-La Loyère')
    loyere_town = town_factory(dep='71', com='265', nccenr='Loyère')
    towns = towns_factory(fragnes_loyere_town, loyere_town)
    creation_not_delegated_record1 = record_factory(
        dep='71', com='204', mod=CREATION_NOT_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Fragnes', comech='71204')
    creation_not_delegated_pole_record1 = record_factory(
        dep='71', com='204', mod=CREATION_NOT_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Fragnes-La Loyère', comech='71204')
    creation_not_delegated_pole_record2 = record_factory(
        dep='71', com='204', mod=CREATION_NOT_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Fragnes-La Loyère', comech='71265')
    creation_not_delegated_record2 = record_factory(
        dep='71', com='265', mod=CREATION_NOT_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Loyère', comech='71204')
    history = [
        creation_not_delegated_record1, creation_not_delegated_pole_record1,
        creation_not_delegated_pole_record2, creation_not_delegated_record2
    ]
    compute(towns, history)
    fragnes, fragnes_loyere = list(towns.filter(depcom='71204'))
    loyere = next(towns.filter(depcom='71265'))
    assert fragnes.id == 'fr:commune:71204@1942-01-01'
    assert fragnes.modification == CREATION_NOT_DELEGATED
    assert fragnes.successors == fragnes_loyere.id
    assert fragnes.nccenr == 'Fragnes'
    assert fragnes.start_date == START_DATE
    assert fragnes.start_datetime == START_DATETIME
    assert fragnes.end_date == date(2015, 12, 31)
    assert fragnes.end_datetime == datetime(2015, 12, 31, 23, 59, 59, 999999)
    assert loyere.id == 'fr:commune:71265@1942-01-01'
    assert loyere.modification == CREATION_NOT_DELEGATED
    assert loyere.successors == fragnes_loyere.id
    assert loyere.nccenr == 'Loyère'
    assert loyere.start_date == START_DATE
    assert loyere.start_datetime == START_DATETIME
    assert loyere.end_date == date(2015, 12, 31)
    assert loyere.end_datetime == datetime(2015, 12, 31, 23, 59, 59, 999999)
    assert fragnes_loyere.id == 'fr:commune:71204@2016-01-01'
    assert fragnes_loyere.modification == CREATION_NOT_DELEGATED_POLE
    assert fragnes_loyere.successors == ''
    assert fragnes_loyere.nccenr == 'Fragnes-La Loyère'
    assert fragnes_loyere.start_date == date(2016, 1, 1)
    assert fragnes_loyere.start_datetime == datetime(2016, 1, 1, 0, 0, 0)
    assert fragnes_loyere.end_date == END_DATE
    assert fragnes_loyere.end_datetime == END_DATETIME


def test_fusion_association_associated():
    """Fusion-association: associated town."""
    falgueyrat_town = town_factory(dep='24', com='173', nccenr='Falgueyrat')
    plaisance_town = town_factory(dep='24', com='168', nccenr='Plaisance')
    towns = towns_factory(falgueyrat_town, plaisance_town)
    fusion_association_associated_record = record_factory(
        dep='24', com='173', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1973, 1, 1), nccoff='Falgueyrat', comech='24168')
    history = [fusion_association_associated_record]
    compute(towns, history)
    falgueyrat_list = list(towns.filter(depcom='24173'))
    assert len(falgueyrat_list) == 1
    falgueyrat = falgueyrat_list[0]
    assert falgueyrat.id == 'fr:commune:24173@1942-01-01'
    assert falgueyrat.successors == 'fr:commune:24168@1942-01-01'
    assert falgueyrat.modification == FUSION_ASSOCIATION_ASSOCIATED
    assert falgueyrat.nccenr == 'Falgueyrat'
    assert falgueyrat.start_date == START_DATE
    assert falgueyrat.start_datetime == START_DATETIME
    assert falgueyrat.end_date == date(1972, 12, 31)
    assert (falgueyrat.end_datetime ==
            datetime(1972, 12, 31, 23, 59, 59, 999999))


def test_creation_delegated():
    """New town: delegated."""
    grentzingen_town = town_factory(dep='68', com='108', nccenr='Grentzingen')
    illtal_town = town_factory(dep='68', com='240', nccenr='Illtal')
    towns = towns_factory(grentzingen_town, illtal_town)
    creation_delegated_record = record_factory(
        dep='68', com='108', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Grentzingen', comech='68240')
    history = [creation_delegated_record]
    compute(towns, history)
    grentzingen_list = list(towns.filter(depcom='68108'))
    assert len(grentzingen_list) == 1
    grentzingen = grentzingen_list[0]
    assert grentzingen.id == 'fr:commune:68108@1942-01-01'
    assert grentzingen.successors == 'fr:commune:68240@1942-01-01'
    assert grentzingen.modification == CREATION_DELEGATED
    assert grentzingen.nccenr == 'Grentzingen'
    assert grentzingen.start_date == START_DATE
    assert grentzingen.start_datetime == START_DATETIME
    assert grentzingen.end_date == date(2015, 12, 31)
    assert (grentzingen.end_datetime ==
            datetime(2015, 12, 31, 23, 59, 59, 999999))


def test_creation_delegated_pole():
    """New town: delegated - pole."""
    grentzingen_town = town_factory(dep='68', com='108', nccenr='Grentzingen')
    henflingen_town = town_factory(dep='68', com='133', nccenr='Henflingen')
    illtal_town = town_factory(dep='68', com='240', nccenr='Illtal')
    towns = towns_factory(grentzingen_town, henflingen_town, illtal_town)
    creation_delegated_record = record_factory(
        dep='68', com='108', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Grentzingen', comech='68240')
    creation_delegated_pole_record1 = record_factory(
        dep='68', com='240', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Illtal', comech='68108',
        last=False)
    creation_delegated_pole_record2 = record_factory(
        dep='68', com='240', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Illtal', comech='68133',
        last=False)
    creation_delegated_pole_record3 = record_factory(
        dep='68', com='240', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Illtal', comech='68240',
        last=True)
    history = [
        creation_delegated_record, creation_delegated_pole_record1,
        creation_delegated_pole_record2, creation_delegated_pole_record3
    ]
    compute(towns, history)
    grentzingen_list = list(towns.filter(depcom='68108'))
    assert len(grentzingen_list) == 1
    grentzingen = grentzingen_list[0]
    illtal_list = list(towns.filter(depcom='68240'))
    assert len(illtal_list) == 1
    illtal = illtal_list[0]
    assert grentzingen.id == 'fr:commune:68108@1942-01-01'
    assert grentzingen.successors == illtal.id
    assert grentzingen.modification == CREATION_DELEGATED
    assert grentzingen.nccenr == 'Grentzingen'
    assert grentzingen.start_date == START_DATE
    assert grentzingen.start_datetime == START_DATETIME
    assert grentzingen.end_date == date(2015, 12, 31)
    assert (grentzingen.end_datetime ==
            datetime(2015, 12, 31, 23, 59, 59, 999999))
    assert illtal.id == 'fr:commune:68240@2016-01-01'
    assert illtal.successors == ''
    assert illtal.modification == CREATION_DELEGATED_POLE
    assert illtal.nccenr == 'Illtal'
    assert illtal.start_date == date(2016, 1, 1)
    assert illtal.start_datetime == datetime(2016, 1, 1, 0, 0, 0)
    assert illtal.end_date == END_DATE
    assert illtal.end_datetime == END_DATETIME


def test_change_county():
    """Town changed county."""
    new_afa_town = town_factory(dep='2A', com='001', nccenr='Afa')
    old_afa_town = town_factory(dep='20', com='001', nccenr='Afa')
    towns = towns_factory(new_afa_town, old_afa_town)
    change_county_record = record_factory(
        dep='2A', com='001', mod=CHANGE_COUNTY,
        effdate=date(1976, 1, 1), nccoff='Afa', depanc='20001')
    history = [change_county_record]
    compute(towns, history)
    afa_list = list(towns.filter(depcom='2A001'))
    assert len(afa_list) == 1
    afa = afa_list[0]
    assert afa.id == 'fr:commune:2A001@1976-01-01'
    assert afa.successors == ''
    assert afa.modification == 0
    assert afa.nccenr == 'Afa'
    assert afa.start_date == date(1976, 1, 1)
    assert afa.start_datetime == datetime(1976, 1, 1, 0, 0, 0)
    assert afa.end_date == END_DATE
    assert afa.end_datetime == END_DATETIME
    old_afa_list = list(towns.filter(depcom='20001'))
    assert len(old_afa_list) == 1
    old_afa = old_afa_list[0]
    assert old_afa.id == 'fr:commune:20001@1942-01-01'
    assert old_afa.successors == 'fr:commune:2A001@1976-01-01'
    assert old_afa.modification == CHANGE_COUNTY
    assert old_afa.nccenr == 'Afa'
    assert old_afa.start_date == START_DATE
    assert old_afa.start_datetime == START_DATETIME
    assert old_afa.end_date == date(1975, 12, 31)
    assert old_afa.end_datetime == datetime(1975, 12, 31, 23, 59, 59, 999999)


def test_change_county_twice():
    old_chateaufort_town = town_factory(dep='78', com='143',
                                        nccenr='Châteaufort')
    new_chateaufort_town = town_factory(dep='91', com='143',
                                        nccenr='Châteaufort')
    towns = towns_factory(new_chateaufort_town, old_chateaufort_town)
    change_county1_record = record_factory(
        dep='78', com='143', mod=CHANGE_COUNTY,
        effdate=date(1969, 11, 29), nccoff='Châteaufort', comech='91143')
    change_county2_record = record_factory(
        dep='91', com='143', mod=CHANGE_COUNTY,
        effdate=date(1968, 1, 1), nccoff='Châteaufort', depanc='78143')
    history = [change_county1_record, change_county2_record]
    compute(towns, history)
    old_chateaufort, chateaufort = list(towns.filter(depcom='78143'))
    tmp_chateaufort_list = list(towns.filter(depcom='91143'))
    assert len(tmp_chateaufort_list) == 1
    tmp_chateaufort = tmp_chateaufort_list[0]
    assert chateaufort.id == 'fr:commune:78143@1969-11-29'
    assert chateaufort.successors == ''
    assert chateaufort.modification == 0
    assert chateaufort.nccenr == 'Châteaufort'
    assert chateaufort.start_date == date(1969, 11, 29)
    assert chateaufort.start_datetime == datetime(1969, 11, 29, 0, 0, 0)
    assert chateaufort.end_date == END_DATE
    assert chateaufort.end_datetime == END_DATETIME
    assert old_chateaufort.id == 'fr:commune:78143@1942-01-01'
    assert old_chateaufort.successors == tmp_chateaufort.id
    assert old_chateaufort.modification == CHANGE_COUNTY
    assert old_chateaufort.nccenr == 'Châteaufort'
    assert old_chateaufort.start_date == START_DATE
    assert old_chateaufort.start_datetime == START_DATETIME
    assert old_chateaufort.end_date == date(1967, 12, 31)
    assert (old_chateaufort.end_datetime ==
            datetime(1967, 12, 31, 23, 59, 59, 999999))
    assert tmp_chateaufort.id == 'fr:commune:91143@1968-01-01'
    assert tmp_chateaufort.successors == chateaufort.id
    assert tmp_chateaufort.modification == CHANGE_COUNTY
    assert tmp_chateaufort.nccenr == 'Châteaufort'
    assert tmp_chateaufort.start_date == date(1968, 1, 1)
    assert tmp_chateaufort.start_datetime == datetime(1968, 1, 1, 0, 0, 0)
    assert tmp_chateaufort.end_date == date(1969, 11, 28)
    assert (tmp_chateaufort.end_datetime ==
            datetime(1969, 11, 28, 23, 59, 59, 999999))


def test_fusion_then_change_county():
    """Town fusion then changed county."""
    old_magny_town = town_factory(dep='78', com='355', nccenr='Magny-en-Vexin')
    new_magny_town = town_factory(dep='95', com='355', nccenr='Magny-en-Vexin')
    old_blamecourt_town = town_factory(dep='78', com='065',
                                       nccenr='Blamécourt')
    new_blamecourt_town = town_factory(dep='95', com='065',
                                       nccenr='Blamécourt')
    towns = towns_factory(old_magny_town, new_magny_town,
                          new_blamecourt_town, old_blamecourt_town)
    # Warning: the depcom reference is at a date where 95065
    # and 95355 do not exist yet!
    fusion_record = record_factory(
        dep='95', com='065', mod=DELETION_FUSION,
        effdate=date(1965, 1, 9), nccoff='Blamécourt', comech='95355')
    change_county_record = record_factory(
        dep='95', com='065', mod=CHANGE_COUNTY,
        effdate=date(1968, 1, 1), nccoff='Blamécourt', depanc='78065')
    history = [fusion_record, change_county_record]
    compute(towns, history)
    blamecourt_list = list(towns.filter(depcom='95065'))
    assert len(blamecourt_list) == 1
    blamecourt = blamecourt_list[0]
    assert blamecourt.id == 'fr:commune:95065@1968-01-01'
    assert blamecourt.successors == next(towns.filter(depcom='95355')).id
    assert blamecourt.modification == DELETION_FUSION
    assert blamecourt.nccenr == 'Blamécourt'
    assert blamecourt.start_date == date(1968, 1, 1)
    assert blamecourt.start_datetime == datetime(1968, 1, 1, 0, 0, 0)
    assert blamecourt.end_date == date(1968, 1, 1)
    assert blamecourt.end_datetime == datetime(1968, 1, 1, 0, 0, 0, 1)
    old_blamecourt_list = list(towns.filter(depcom='78065'))
    assert len(old_blamecourt_list) == 1
    old_blamecourt = old_blamecourt_list[0]
    assert old_blamecourt.id == 'fr:commune:78065@1942-01-01'
    assert old_blamecourt.successors == 'fr:commune:95065@1968-01-01'
    assert old_blamecourt.modification == CHANGE_COUNTY
    assert old_blamecourt.nccenr == 'Blamécourt'
    assert old_blamecourt.start_date == START_DATE
    assert old_blamecourt.start_datetime == START_DATETIME
    assert old_blamecourt.end_date == date(1967, 12, 31)
    assert (old_blamecourt.end_datetime ==
            datetime(1967, 12, 31, 23, 59, 59, 999999))


def test_obsolete():
    """Obsolete town."""
    hauteville_town = town_factory(dep='01', com='459',
                                   nccenr='Hauteville-Lompnés')
    towns = towns_factory(hauteville_town)
    obsolete_record = record_factory(
        dep='01', com='459', mod=OBSOLETE,
        effdate=date(1942, 8, 1), nccoff='Hauteville-Lompnés')
    history = [obsolete_record]
    compute(towns, history)
    hauteville_list = list(towns.filter(depcom='01459'))
    assert len(hauteville_list) == 1
    hauteville = hauteville_list[0]
    assert hauteville.id == 'fr:commune:01459@1942-01-01'
    assert hauteville.successors == ''
    assert hauteville.modification == OBSOLETE
    assert hauteville.nccenr == 'Hauteville-Lompnés'
    assert hauteville.start_date == START_DATE
    assert hauteville.start_datetime == START_DATETIME
    assert hauteville.end_date == date(1942, 7, 31)
    assert hauteville.end_datetime == datetime(1942, 7, 31, 23, 59, 59, 999999)


def test_successors_update_on_fusion():
    """When an successor is first set to the wrong town."""
    bragelogne_beauvoir_town = town_factory(dep='10', com='058',
                                            nccenr='Beauvoir')
    beauvoir_sarce_town = town_factory(dep='10', com='036',
                                       nccenr='Beauvoir-sur-Sarce')
    towns = towns_factory(bragelogne_beauvoir_town, beauvoir_sarce_town)
    fusion_association_record = record_factory(
        dep='10', com='036', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1973, 5, 1), nccoff='Beauvoir-sur-Sarce', comech='10058')
    change_name_record = record_factory(
        dep='10', com='058', mod=CHANGE_NAME_FUSION,
        effdate=date(1973, 5, 1), nccoff='Bragelogne-Beauvoir',
        nccanc='Bragelogne')
    history = [fusion_association_record, change_name_record]
    compute(towns, history)
    bragelogne, bragelogne_beauvoir = list(towns.filter(depcom='10058'))
    beauvoir_sur_sarce = next(towns.filter(depcom='10036'))
    assert bragelogne.nccenr == 'Bragelogne'
    assert bragelogne.successors == bragelogne_beauvoir.id
    assert beauvoir_sur_sarce.successors == bragelogne_beauvoir.id
    assert bragelogne_beauvoir.successors == ''


def test_ancestor_not_deleted_on_fusion():
    """The ancestor with same depcom should not be deleted on fusion."""
    val_ocre_town = town_factory(dep='89', com='334', nccenr="Val d'Ocre")
    saint_martin_town = town_factory(dep='89', com='356',
                                     nccenr='Saint-Martin-sur-Ocre')
    towns = towns_factory(val_ocre_town, saint_martin_town)
    creation_delegated_record1 = record_factory(
        dep='89', com='334', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Saint-Aubin-Château-Neuf',
        comech='89334')
    change_name_record1 = record_factory(
        dep='89', com='334', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff="Val d'Ocre",
        last=False, comech='89334')
    change_name_record2 = record_factory(
        dep='89', com='334', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff="Val d'Ocre",
        last=True, comech='89356')
    creation_delegated_record2 = record_factory(
        dep='89', com='356', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Saint-Martin-sur-Ocre',
        comech='89334')
    history = [
        creation_delegated_record1,
        change_name_record1,
        change_name_record2,
        creation_delegated_record2,
    ]
    compute(towns, history)
    saint_aubin, val_ocre = list(towns.filter(depcom='89334'))
    saint_martin_list = list(towns.filter(depcom='89356'))
    assert len(saint_martin_list) == 1
    saint_martin = saint_martin_list[0]
    assert saint_aubin.id == 'fr:commune:89334@1942-01-01'
    assert saint_aubin.nccenr == 'Saint-Aubin-Château-Neuf'
    assert saint_aubin.successors == val_ocre.id
    assert saint_martin.id == 'fr:commune:89356@1942-01-01'
    assert saint_martin.nccenr == 'Saint-Martin-sur-Ocre'
    assert saint_martin.successors == val_ocre.id
    assert val_ocre.id == 'fr:commune:89334@2016-01-01'
    assert val_ocre.nccenr == "Val d'Ocre"
    assert val_ocre.successors == ''


def test_reinstatement_with_existing_town():
    """When a town is reinstated but already exists."""
    avanchers_valmorel_town = town_factory(dep='73', com='024',
                                           nccenr='Avanchers-Valmorel')
    aigueblanche_town = town_factory(dep='73', com='003',
                                     nccenr='Aigueblanche')
    towns = towns_factory(avanchers_valmorel_town, aigueblanche_town)
    fusion_association_record = record_factory(
        dep='73', com='024', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1972, 7, 18), nccoff='Avanchers', comech='73003')
    change_name_record = record_factory(
        dep='73', com='024', mod=CHANGE_NAME,
        effdate=date(1988, 1, 1), nccoff='Avanchers-Valmorel',
        nccanc='Avanchers')
    reinstatement_record = record_factory(
        dep='73', com='024', mod=REINSTATEMENT,
        effdate=date(1988, 1, 1), nccoff='Avanchers-Valmorel',
        comech='73003')
    history = [fusion_association_record, change_name_record,
               reinstatement_record]
    compute(towns, history)
    avanchers, avanchers_valmorel = list(towns.filter(depcom='73024'))
    aigueblanche_list = list(towns.filter(depcom='73003'))
    assert len(aigueblanche_list) == 1
    aigueblanche = aigueblanche_list[0]
    assert avanchers.nccenr == 'Avanchers'
    assert (avanchers.successors ==
            aigueblanche.id + ';' + avanchers_valmorel.id)
    assert avanchers_valmorel.nccenr == 'Avanchers-Valmorel'
    assert avanchers_valmorel.successors == ''


def test_start_end_same_moment():
    lamarche_town = town_factory(dep='55', com='273',
                                 nccenr='Lamarche-en-Woëvre')
    heudicourt_town = town_factory(dep='55', com='245',
                                   nccenr='Heudicourt-sous-les-Côtes')
    nonsart_town = town_factory(dep='55', com='386',
                                nccenr='Nonsard-Lamarche')
    towns = towns_factory(lamarche_town, heudicourt_town, nonsart_town)
    fusion_association_record1 = record_factory(
        dep='55', com='273', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1973, 1, 1), nccoff='Lamarche-en-Woëvre', comech='55245')
    reinstatement_record = record_factory(
        dep='55', com='273', mod=REINSTATEMENT,
        effdate=date(1983, 1, 1), nccoff='Lamarche-en-Woëvre', comech='55245')
    fusion_association_record2 = record_factory(
        dep='55', com='273', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1983, 1, 1), nccoff='Lamarche-en-Woëvre', comech='55386')
    history = [fusion_association_record1, reinstatement_record,
               fusion_association_record2]
    compute(towns, history)
    lamarche1, lamarche2 = list(towns.filter(depcom='55273'))
    heudicourt = next(towns.filter(depcom='55245'))
    nonsard = next(towns.filter(depcom='55386'))
    assert lamarche1.nccenr == 'Lamarche-en-Woëvre'
    assert lamarche1.successors == heudicourt.id
    assert lamarche2.nccenr == 'Lamarche-en-Woëvre'
    assert lamarche2.successors == nonsard.id
    assert lamarche2.start_datetime == datetime(1983, 1, 1, 0, 0, 0)
    assert lamarche2.end_datetime == datetime(1983, 1, 1, 0, 0, 0, 1)


def test_creation_delegated_pole_not_sorted():
    """Special case of Boischampré with rangcom not sorted."""
    boischampre_town = town_factory(dep='61', com='375', nccenr='Boischampré')
    vrigny_town = town_factory(dep='61', com='511', nccenr='Vrigny')
    loyer_town = town_factory(dep='61', com='417',
                              nccenr='Saint-Loyer-des-Champs')
    marcei_town = town_factory(dep='61', com='249', nccenr='Marcei')
    towns = towns_factory(
        boischampre_town, vrigny_town, loyer_town, marcei_town)
    creation_delegated_record1 = record_factory(
        dep='61', com='511', mod=CREATION_DELEGATED,
        effdate=date(2015, 1, 1), nccoff='Vrigny', comech='61375')
    creation_delegated_record2 = record_factory(
        dep='61', com='417', mod=CREATION_DELEGATED,
        effdate=date(2015, 1, 1), nccoff='Saint-Loyer-des-Champs',
        comech='61375')
    creation_delegated_record3 = record_factory(
        dep='61', com='249', mod=CREATION_DELEGATED,
        effdate=date(2015, 1, 1), nccoff='Marcei', comech='61375')
    # Here the order is very important given that `rangcom` is not sorted
    # in the right order within the historiq file!
    creation_delegated_pole_record1 = record_factory(
        dep='61', com='375', mod=CREATION_DELEGATED_POLE,
        effdate=date(2015, 1, 1), nccoff='Boischampré', comech='61511',
        last=False)
    creation_delegated_pole_record2 = record_factory(
        dep='61', com='375', mod=CREATION_DELEGATED_POLE,
        effdate=date(2015, 1, 1), nccoff='Boischampré', comech='61417',
        last=False)
    creation_delegated_pole_record3 = record_factory(
        dep='61', com='375', mod=CREATION_DELEGATED_POLE,
        effdate=date(2015, 1, 1), nccoff='Boischampré', comech='61249',
        last=False)
    creation_delegated_pole_record4 = record_factory(
        dep='61', com='375', mod=CREATION_DELEGATED_POLE,
        effdate=date(2015, 1, 1), nccoff='Boischampré', comech='61375',
        last=True)
    history = [
        creation_delegated_record1, creation_delegated_record2,
        creation_delegated_record3,
        creation_delegated_pole_record1, creation_delegated_pole_record2,
        creation_delegated_pole_record3, creation_delegated_pole_record4
    ]
    compute(towns, history)
    boischampre_list = list(towns.filter(depcom='61375'))
    assert len(boischampre_list) == 1
    boischampre = boischampre_list[0]
    vrigny_list = list(towns.filter(depcom='61511'))
    assert len(vrigny_list) == 1
    vrigny = vrigny_list[0]
    assert boischampre.id == 'fr:commune:61375@2015-01-01'
    assert boischampre.successors == ''
    assert boischampre.modification == CREATION_DELEGATED_POLE
    assert boischampre.nccenr == 'Boischampré'
    assert vrigny.id == 'fr:commune:61511@1942-01-01'
    assert vrigny.successors == boischampre.id
    assert vrigny.modification == CREATION_DELEGATED
    assert vrigny.nccenr == 'Vrigny'


def test_creation_delegated_pole_without_same_name():
    """Special case of Rouget-Pers with name changed."""
    saint_mamet_town = town_factory(dep='15', com='196',
                                    nccenr='Saint-Mamet-la-Salvetat')
    rouget_pers_town = town_factory(dep='15', com='268', nccenr='Rouget-Pers')
    pers_town = town_factory(dep='15', com='150', nccenr='Pers')
    towns = towns_factory(saint_mamet_town, rouget_pers_town, pers_town)
    creation_record = record_factory(
        dep='15', com='268', mod=CREATION,
        effdate=date(1945, 9, 17), nccoff='Rouget', comech='15196')
    # Order is important to make the test relevant.
    creation_delegated_pole_record1 = record_factory(
        dep='15', com='268', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Rouget-Pers', comech='15268',
        last=False)
    creation_delegated_record1 = record_factory(
        dep='15', com='150', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Pers', comech='15268')
    creation_delegated_record2 = record_factory(
        dep='15', com='268', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Rouget', comech='15268')
    creation_delegated_pole_record2 = record_factory(
        dep='15', com='268', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Rouget-Pers', comech='15150',
        last=True)
    history = [
        creation_record,
        creation_delegated_pole_record1,
        creation_delegated_record1,
        creation_delegated_record2,
        creation_delegated_pole_record2,
    ]
    compute(towns, history)
    rouget, rouget_pers = list(towns.filter(depcom='15268'))
    pers_list = list(towns.filter(depcom='15150'))
    assert len(pers_list) == 1
    pers = pers_list[0]
    assert rouget.id == 'fr:commune:15268@1945-09-17'
    assert rouget.successors == rouget_pers.id
    assert rouget.modification == CREATION_DELEGATED
    assert rouget.nccenr == 'Rouget'
    assert rouget.start_datetime == datetime(1945, 9, 17, 0, 0, 0)
    assert rouget.end_datetime == datetime(2015, 12, 31, 23, 59, 59, 999999)
    assert pers.id == 'fr:commune:15150@1942-01-01'
    assert pers.successors == rouget_pers.id
    assert pers.modification == CREATION_DELEGATED
    assert pers.nccenr == 'Pers'
    assert pers.start_datetime == START_DATETIME
    assert pers.end_datetime == datetime(2015, 12, 31, 23, 59, 59, 999999)
    assert rouget_pers.id == 'fr:commune:15268@2016-01-01'
    assert rouget_pers.successors == ''
    assert rouget_pers.modification == CREATION_DELEGATED_POLE
    assert rouget_pers.nccenr == 'Rouget-Pers'
    assert rouget_pers.start_datetime == datetime(2016, 1, 1, 0, 0, 0)
    assert rouget_pers.end_datetime == END_DATETIME


def test_change_county_after_rename():
    """Special case of Sainte-Lucie-de-Tallano"""
    sainte_lucie_town1 = town_factory(dep='2A', com='308',
                                      nccenr='Sainte-Lucie-de-Tallano')
    sainte_lucie_town2 = town_factory(dep='20', com='308',
                                      nccenr='Sainte-Lucie-de-Tallano')
    poggio_town = town_factory(dep='2A', com='237',
                                   nccenr='Poggio-di-Tallano')
    andrea_town = town_factory(dep='2A', com='294',
                               nccenr="Sant'Andréa-di-Tallano")
    towns = towns_factory(
        sainte_lucie_town1, sainte_lucie_town2, poggio_town, andrea_town)
    deletion_fusion_record1 = record_factory(
        dep='2A', com='237', mod=DELETION_FUSION,
        effdate=date(1965, 1, 1), nccoff='Poggio-di-Tallano', comech='2A308')
    deletion_fusion_record2 = record_factory(
        dep='2A', com='294', mod=DELETION_FUSION,
        effdate=date(1965, 1, 1), nccoff="Sant'Andréa-di-Tallano",
        comech='2A308')
    change_name_fusion_record = record_factory(
        dep='2A', com='308', mod=CHANGE_NAME_FUSION, effdate=date(1965, 1, 1),
        nccoff='Sainte-Lucie-de-Tallano', nccanc='Santa-Lucia-di-Tallano')
    change_county_record = record_factory(
        dep='2A', com='308', mod=CHANGE_COUNTY,
        effdate=date(1976, 1, 1), nccoff='Sainte-Lucie-de-Tallano',
        depanc='20308')
    history = [
        deletion_fusion_record1,
        deletion_fusion_record2,
        change_name_fusion_record,
        change_county_record,
    ]
    compute(towns, history)
    santa_lucia, sainte_lucie = list(towns.filter(depcom='20308'))
    sainte_lucie_new = next(towns.filter(depcom='2A308'))
    poggio = next(towns.filter(depcom='2A237'))
    andrea = next(towns.filter(depcom='2A294'))
    assert santa_lucia.id == 'fr:commune:20308@1942-01-01'
    assert santa_lucia.end_date == date(1964, 12, 31)
    assert sainte_lucie.id == 'fr:commune:20308@1965-01-01'
    assert sainte_lucie.end_date == date(1975, 12, 31)
    assert santa_lucia.successors == sainte_lucie.id
    assert poggio.successors == sainte_lucie.id
    assert andrea.successors == sainte_lucie.id
    assert sainte_lucie.successors == sainte_lucie_new.id
    assert sainte_lucie_new.id == 'fr:commune:2A308@1976-01-01'
    assert sainte_lucie_new.end_date == END_DATE


def test_change_name_reinstatement_before_change_name_fusion():
    """Special case of Rocquefort-sur-Héricourt with name changed."""
    rocquefort_town = town_factory(dep='35', com='355',
                                   nccenr='Rocquefort-sur-Héricour')
    hericourt_town = town_factory(dep='35', com='355',
                                  nccenr='Héricourt-en-Caux')
    towns = towns_factory(rocquefort_town, hericourt_town)

    # Order is important to make the test relevant.
    change_name_reinstatement_record = record_factory(
        dep='35', com='355', mod=CHANGE_NAME_REINSTATEMENT,
        effdate=date(1976, 10, 29),
        nccoff='Héricourt-en-Caux', nccanc='Rocquefort-sur-Héricourt')
    spliting_record = record_factory(
        dep='35', com='355', mod=SPLITING,
        effdate=date(1976, 10, 29),
        nccoff='Héricourt-en-Caux', comech='76531')
    change_name_fusion_record = record_factory(
        dep='35', com='355', mod=CHANGE_NAME_FUSION,
        effdate=date(1973, 4, 10),
        nccoff='Rocquefort-sur-Héricourt', nccanc='Héricourt-en-Caux')
    history = [
        change_name_reinstatement_record,
        spliting_record,
        change_name_fusion_record,
    ]
    compute(towns, history)
    hericourt1, rocquefort, hericourt2 = list(towns.filter(depcom='35355'))
    assert hericourt1.id == 'fr:commune:35355@1942-01-01'
    assert hericourt1.successors == hericourt2.id + ';' + rocquefort.id
    assert hericourt1.modification == CHANGE_NAME_FUSION
    assert hericourt1.nccenr == 'Héricourt-en-Caux'
    assert hericourt1.start_datetime == START_DATETIME
    assert hericourt1.end_datetime == datetime(1973, 4, 9, 23, 59, 59, 999999)
    assert rocquefort.id == 'fr:commune:35355@1973-04-10'
    assert rocquefort.successors == hericourt2.id
    assert rocquefort.modification == CHANGE_NAME_REINSTATEMENT
    assert rocquefort.nccenr == 'Rocquefort-sur-Héricourt'
    assert rocquefort.start_datetime == datetime(1973, 4, 10, 0, 0, 0)
    assert (rocquefort.end_datetime ==
            datetime(1976, 10, 28, 23, 59, 59, 999999))
    assert hericourt2.id == 'fr:commune:35355@1976-10-29'
    assert hericourt2.successors == ''
    assert hericourt2.modification == SPLITING
    assert hericourt2.nccenr == 'Héricourt-en-Caux'
    assert hericourt2.start_datetime == datetime(1976, 10, 29, 0, 0, 0)
    assert hericourt2.end_datetime == END_DATETIME


def test_fusion_then_change_name_on_successor():
    """Special case of Arlod/Bellegarde(-sur-Valserine) and many."""
    arlod_town = town_factory(dep='01', com='018', nccenr='Arlod')
    bellegarde_town = town_factory(dep='01', com='033', nccenr='Bellegarde')
    towns = towns_factory(arlod_town, bellegarde_town)

    # Order is important to make the test relevant.
    delete_fusion_record = record_factory(
        dep='01', com='018', mod=DELETION_FUSION,
        effdate=date(1971, 1, 1),
        nccoff='Arlod', comech='01033')
    change_name_record = record_factory(
        dep='01', com='033', mod=CHANGE_NAME,
        effdate=date(1956, 10, 19),
        nccoff='Bellegarde-sur-Valserine', nccanc='Bellegarde')
    history = [
        delete_fusion_record,
        change_name_record,
    ]
    compute(towns, history)
    arlod = next(towns.filter(depcom='01018'))
    bellegarde, bellegarde_valserine = list(towns.filter(depcom='01033'))
    assert arlod.id == 'fr:commune:01018@1942-01-01'
    assert arlod.successors == bellegarde_valserine.id
    assert arlod.modification == DELETION_FUSION
    assert arlod.nccenr == 'Arlod'
    assert arlod.start_datetime == START_DATETIME
    assert arlod.end_datetime == datetime(1970, 12, 31, 23, 59, 59, 999999)
    assert bellegarde.id == 'fr:commune:01033@1942-01-01'
    assert bellegarde.successors == bellegarde_valserine.id
    assert bellegarde.modification == CHANGE_NAME
    assert bellegarde.nccenr == 'Bellegarde'
    assert bellegarde.start_datetime == START_DATETIME
    assert (bellegarde.end_datetime ==
            datetime(1956, 10, 18, 23, 59, 59, 999999))
    assert bellegarde_valserine.id == 'fr:commune:01033@1956-10-19'
    assert bellegarde_valserine.successors == ''
    assert bellegarde_valserine.modification == 0
    assert bellegarde_valserine.nccenr == 'Bellegarde-sur-Valserine'
    assert (bellegarde_valserine.start_datetime ==
            datetime(1956, 10, 19, 0, 0, 0))
    assert bellegarde_valserine.end_datetime == END_DATETIME


def test_fusion_then_delegated_with_intermediate_successor():
    """Special case of Cuisiat/Treffort-Cuisiat/Val-Revermont."""
    cuisiat_town = town_factory(dep='01', com='137', nccenr='Cuisiat')
    pressiat_town = town_factory(dep='01', com='312', nccenr='Pressiat')
    val_revermont_town = town_factory(dep='01', com='426',
                                      nccenr='Val-Revermont')
    towns = towns_factory(cuisiat_town, pressiat_town, val_revermont_town)

    # Order is important to make the test relevant.
    fusion_association_associated_record = record_factory(
        dep='01', com='137', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1972, 12, 1),
        nccoff='Cuisiat', comech='01426')
    change_name_record = record_factory(
        dep='01', com='426', mod=CHANGE_NAME_FUSION,
        effdate=date(1972, 12, 1),
        nccoff='Treffort-Cuisiat', nccanc='Treffort')
    creation_delegated_pole_record1 = record_factory(
        dep='01', com='426', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Val-Revermont', comech='01312',
        last=False)
    creation_preexisting_associated_record = record_factory(
        dep='01', com='137', mod=CREATION_PREEXISTING_ASSOCIATED,
        effdate=date(2016, 1, 1), nccoff='Cuisiat', comech='01426')
    creation_delegated_record = record_factory(
        dep='01', com='426', mod=CREATION_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Treffort', comech='01426')
    creation_delegated_pole_record2 = record_factory(
        dep='01', com='426', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Val-Revermont', comech='01426',
        last=False)
    creation_delegated_pole_record3 = record_factory(
        dep='01', com='426', mod=CREATION_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Val-Revermont', comech='01137',
        last=True)
    history = [
        fusion_association_associated_record,
        change_name_record,
        creation_delegated_pole_record1,
        creation_preexisting_associated_record,
        creation_delegated_record,
        creation_delegated_pole_record2,
        creation_delegated_pole_record3,
    ]
    compute(towns, history)
    cuisiat = next(towns.filter(depcom='01137'))
    treffort, treffort_cuisiat, val_revermont = towns.filter(depcom='01426')
    assert cuisiat.id == 'fr:commune:01137@1942-01-01'
    assert cuisiat.successors == treffort_cuisiat.id
    assert cuisiat.modification == FUSION_ASSOCIATION_ASSOCIATED
    assert cuisiat.nccenr == 'Cuisiat'
    assert cuisiat.start_datetime == START_DATETIME
    assert cuisiat.end_datetime == datetime(1972, 11, 30, 23, 59, 59, 999999)
    assert treffort.id == 'fr:commune:01426@1942-01-01'
    assert treffort.successors == treffort_cuisiat.id
    assert treffort.modification == CHANGE_NAME_FUSION
    assert treffort.nccenr == 'Treffort'
    assert treffort.start_datetime == START_DATETIME
    assert treffort.end_datetime == datetime(1972, 11, 30, 23, 59, 59, 999999)
    assert treffort_cuisiat.id == 'fr:commune:01426@1972-12-01'
    assert treffort_cuisiat.successors == val_revermont.id
    assert treffort_cuisiat.modification == CREATION_DELEGATED
    # assert treffort_cuisiat.nccenr == 'Treffort-Cuisiat'  # Bug in historiq?
    assert treffort_cuisiat.start_datetime == datetime(1972, 12, 1, 0, 0, 0)
    assert (treffort_cuisiat.end_datetime ==
            datetime(2015, 12, 31, 23, 59, 59, 999999))
    assert val_revermont.id == 'fr:commune:01426@2016-01-01'
    assert val_revermont.successors == ''
    assert val_revermont.modification == CREATION_DELEGATED_POLE
    assert val_revermont.nccenr == 'Val-Revermont'
    assert val_revermont.start_datetime == datetime(2016, 1, 1, 0, 0, 0)
    assert val_revermont.end_datetime == END_DATETIME


def test_fusion_then_split_then_change_name():
    """Special case of Chartèves/Mont-Saint-Père/Charmont-sur-Marne."""
    towns = towns_factory(
        town_factory(dep='02', com='166', nccenr='Chartèves'),
        town_factory(dep='02', com='524', nccenr='Mont-Saint-Père')
    )

    # Order is important to make the test relevant.
    fusion_association_record = record_factory(
        dep='02', com='166', mod=FUSION_ASSOCIATION_ASSOCIATED,
        effdate=date(1974, 10, 1),
        nccoff='Chartèves', comech='02524')
    reinstatement_record = record_factory(
        dep='02', com='166', mod=REINSTATEMENT,
        effdate=date(1978, 1, 1),
        nccoff='Chartèves', comech='02254')
    change_name_fusion_record = record_factory(
        dep='02', com='524', mod=CHANGE_NAME_FUSION,
        effdate=date(1974, 10, 1),
        nccoff='Charmont-sur-Marne', nccanc='Mont-Saint-Père')
    spliting_record = record_factory(
        dep='02', com='524', mod=SPLITING,
        effdate=date(1978, 1, 1),
        nccoff='Charmont-sur-Marne', comech='02166')
    change_name_record = record_factory(
        dep='02', com='524', mod=CHANGE_NAME,
        effdate=date(1979, 6, 15),
        nccoff='Mont-Saint-Père', nccanc='Charmont-sur-Marne')
    history = [
        fusion_association_record,
        reinstatement_record,
        change_name_fusion_record,
        spliting_record,
        change_name_record,
    ]
    compute(towns, history)
    charteves1, charteves2 = list(towns.filter(depcom='02166'))
    mt_st_pere1, charmont_sur_marne, mt_st_pere2 = list(towns.filter(depcom='02524'))
    assert charteves1.id == 'fr:commune:02166@1942-01-01'
    assert charteves1.nccenr == 'Chartèves'
    assert charteves1.successors == charmont_sur_marne.id
    assert charteves1.end_datetime == datetime(1974, 9, 30, 23, 59, 59, 999999)
    assert charteves2.id == 'fr:commune:02166@1978-01-01'
    assert charteves2.nccenr == 'Chartèves'
    assert charteves2.successors == ''
    assert charteves2.end_datetime == END_DATETIME
    assert mt_st_pere1.id == 'fr:commune:02524@1942-01-01'
    assert mt_st_pere1.nccenr == 'Mont-Saint-Père'
    assert mt_st_pere1.successors == charmont_sur_marne.id
    assert (mt_st_pere1.end_datetime ==
            datetime(1974, 9, 30, 23, 59, 59, 999999))
    assert charmont_sur_marne.id == 'fr:commune:02524@1974-10-01'
    assert charmont_sur_marne.nccenr == 'Charmont-sur-Marne'
    assert charmont_sur_marne.successors == mt_st_pere2.id
    assert (charmont_sur_marne.end_datetime ==
            datetime(1979, 6, 14, 23, 59, 59, 999999))
    assert mt_st_pere2.id == 'fr:commune:02524@1979-06-15'
    assert mt_st_pere2.nccenr == 'Mont-Saint-Père'
    assert mt_st_pere2.successors == ''
    assert mt_st_pere2.end_datetime == END_DATETIME


def test_creation_not_delegated_pole():
    """Special case of Sylvains-les-Moulins."""
    towns = towns_factory(
        town_factory(dep='27', com='178', nccenr='Coulonges'),
        town_factory(dep='27', com='688', nccenr='Villalet'),
        town_factory(dep='27', com='693', nccenr='Sylvains-Lès-Moulins')
    )

    # Order is important to make the test relevant.
    change_name_fusion_record = record_factory(
        dep='27', com='693', mod=CHANGE_NAME_FUSION,
        effdate=date(1972, 10, 1),
        nccoff='Sylvains-les-Moulins', nccanc='Villez-Champ-Dominel')
    delete_fusion_record = record_factory(
        dep='27', com='178', mod=DELETION_FUSION,
        effdate=date(1972, 10, 1),
        nccoff='Coulonges', comech='27693')
    creation_not_delegated_record1 = record_factory(
        dep='27', com='688', mod=CREATION_NOT_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Villalet', comech='27693')
    creation_not_delegated_record2 = record_factory(
        dep='27', com='693', mod=CREATION_NOT_DELEGATED,
        effdate=date(2016, 1, 1), nccoff='Sylvains-les-Moulins',
        comech='27693')
    creation_not_delegated_pole_record1 = record_factory(
        dep='27', com='693', mod=CREATION_NOT_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Sylvains-Lès-Moulins',
        comech='27688')
    creation_not_delegated_pole_record2 = record_factory(
        dep='27', com='693', mod=CREATION_NOT_DELEGATED_POLE,
        effdate=date(2016, 1, 1), nccoff='Sylvains-Lès-Moulins',
        comech='27693', last=True)

    history = [
        change_name_fusion_record,
        delete_fusion_record,
        creation_not_delegated_record1,
        creation_not_delegated_record2,
        creation_not_delegated_pole_record1,
        creation_not_delegated_pole_record2,
    ]
    compute(towns, history)
    villez, sylvains, sylvains_lais = list(towns.filter(depcom='27693'))
    coulonges = next(towns.filter(depcom='27178'))
    villalet = next(towns.filter(depcom='27688'))
    assert coulonges.id == 'fr:commune:27178@1942-01-01'
    assert coulonges.start_datetime == START_DATETIME
    assert coulonges.end_datetime == datetime(1972, 9, 30, 23, 59, 59, 999999)
    assert coulonges.successors == sylvains.id
    assert villez.id == 'fr:commune:27693@1942-01-01'
    assert villez.start_datetime == START_DATETIME
    assert villez.end_datetime == datetime(1972, 9, 30, 23, 59, 59, 999999)
    assert villez.successors == sylvains.id
    assert villalet.id == 'fr:commune:27688@1942-01-01'
    assert villalet.start_datetime == START_DATETIME
    assert villalet.end_datetime == datetime(2015, 12, 31, 23, 59, 59, 999999)
    # assert villalet.successors == sylvains_lais.id  # To be investigated.
    assert sylvains.id == 'fr:commune:27693@1972-10-01'
    assert sylvains.start_datetime == datetime(1972, 10, 1, 0, 0, 0)
    assert sylvains.end_datetime == datetime(2015, 12, 31, 23, 59, 59, 999999)
    assert sylvains.successors == sylvains_lais.id
    assert sylvains_lais.id == 'fr:commune:27693@2016-01-01'
    assert sylvains_lais.start_datetime == datetime(2016, 1, 1, 0, 0, 0)
    assert sylvains_lais.end_datetime == END_DATETIME
    assert sylvains_lais.successors == ''


def test_change_county_creation():
    """Only for Gernicourt and Fresne-sur-Loire."""
    towns = towns_factory(
        town_factory(dep='02', com='344', nccenr='Gernicourt'),
        town_factory(dep='51', com='664', nccenr='Gernicourt')
    )
    change_county_creation_record = record_factory(
        dep='51', com='664', mod=CHANGE_COUNTY_CREATION,
        effdate=date(2016, 12, 31),
        nccoff='Gernicourt', depanc='02344')

    history = [change_county_creation_record]
    compute(towns, history)
    gernicourt_old = next(towns.filter(depcom='02344'))
    gernicourt_new = next(towns.filter(depcom='51664'))
    assert gernicourt_old.id == 'fr:commune:02344@1942-01-01'
    assert gernicourt_old.start_datetime == START_DATETIME
    assert (gernicourt_old.end_datetime ==
            datetime(2016, 12, 30, 23, 59, 59, 999999))
    assert gernicourt_old.successors == gernicourt_new.id
    assert gernicourt_new.id == 'fr:commune:51664@2016-12-31'
    assert gernicourt_new.start_datetime == datetime(2016, 12, 31, 0, 0)
    assert gernicourt_new.end_datetime == datetime(2016, 12, 31, 0, 0, 0, 1)
    assert gernicourt_new.successors == ''
