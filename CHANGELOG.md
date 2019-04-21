# CHANGELOG

## 11.0.0 — Not published yet

* Use COG 2018 (previously 2017) from INSEE as source.

## 10.0.2 - 2017-12-01

* Handle special case of Mauvezin-sur-Gupie, fix #59

## 10.0.1 - 2017-10-30

* Deal with Centre region renaming in 2015, fix #57

## 10.0.0 - 2017-08-22

* Integrate intercommunalities (ie. French EPCIs) historical data.

## 9.0.1 — 2017-06-20

* Fix 2A, 2B and 17 departements’ parents references.

## 9.0.0 — 2017-05-30

* Switch to GeoIDs, see https://github.com/etalab/geoids

## 8.1.4 — 2017-05-25

* Handle special cases of Pretz and Avanchers, fixed #42.

## 8.1.3 — 2017-05-18

* Correct successors/ancestors in case of fusions then splits.

## 8.1.2 — 2017-05-12

* Add 2-letters ISO codes for overseas collectivities.

## 8.1.0 — 2017-05-12

* Add overseas collectivities.

## 8.0.0 — 2017-05-12

* Rename `counties` to `departements` and `towns` to `communes` in exports.

## 7.0.1 — 2017-04-23

* Fixed #24: Misunderstanding of modification code 332 + special cases.

## 7.0.0 — 2017-04-19

* Use COG 2017 (previously 2016) from INSEE as source.

## 6.6.0 — 2017-04-17

* Handle overseas counties.

## 6.5.0 — 2017-03-31

* Handle special cases manually, fixed #27 and #34.

## 6.4.0 — 2017-03-24

* Fixed #29: Handle creation not delegated pole case.
* Fixed #28: Ensure successors are updated correctly.
* Fixed #25: Ensure end date/successors are correctly set.
* Fixed #26: Handle articles for towns from history file.


## 6.3.0 — 2016-12-12

* Wrong start dates for 11 counties.


## 6.2.0 — 2016-12-06

* Newly generated towns files for previous bug.


## 6.1.0 — 2016-12-06

* Wrong INSEE codes for Ardèche and Ardennes.


## 6.0.0 — 2016-12-06

* French counties export.
* Add parents for towns.


## 5.0.0 — 2016-12-01

* Switch the name column in exports for CSV readability.
* Use ids for Chef-lieux in regions export.


## 4.0.0 — 2016-12-01

* Change ids for towns and regions (again) for consistency with INSEE.


## 3.0.0 — 2016-12-01

* Change ids for towns and regions for uniqueness with counties.


## 2.0.0 — 2016-11-18

* Export format of regions has changed to be consistent with towns.


## 1.0.0 — 2016-10-25

* French towns and regions exports with 2016-01-01 updates.
