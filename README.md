⚠️ Not maintained anymore. See https://github.com/etalab/decoupage-administratif

# GeoHisto

**Historic information for French regions, counties, overseas collectivities and towns based on INSEE and Wikipedia data, exported as (re)usable CSV files.**

It might be useful if you have to deal with redirections and is in use by the [geozones](https://github.com/etalab/geozones) project to feed [data.gouv.fr](http://www.data.gouv.fr/fr/).


## Usage

If you’re only interested in generated data, check out the `exports` folder which contains CSV files related to [intercommunalities](exports/epci), [regions](exports/regions/), [counties](exports/departements/), [overseas collectivities](exports/collectivites/) and [towns](exports/communes/). There is a dedicated documentation at these places.


## Sources

Source files are coming from the [INSEE downloads page](https://www.insee.fr/fr/information/3363419) which allows to retrieve information related to the “Code officiel géographique 2018”. We’re using the list of existing towns and their history which are both available within the `sources` folder.

Additionaly, files containing the population for almost all towns has been computed too in the `sources` folder. They are coming from [a XLS dataset](http://www.insee.fr/fr/ppp/bases-de-donnees/recensement/populations-legales/pages2015/zip/HIST_POP_COM_RP13.zip) provided by  [INSEE](http://www.insee.fr/fr/ppp/bases-de-donnees/recensement/populations-legales/), manually completed with Wikipedia data for [Lyon](https://fr.wikipedia.org/wiki/Arrondissements_de_Lyon) and [Marseille](https://fr.wikipedia.org/wiki/Secteurs_et_arrondissements_de_Marseille) districts, and converted into CSV.

[Intercommunalities source files are fully documented into their folder](sources/epci).


## Development

The project only requires [click](http://click.pocoo.org/5/) dependency (you can install it with `pip install -r requirements.txt` within a virtualenv but YMMV), you have to run it with Python 3 though:

    $ python -m geohisto

Note that it takes about 7 minutes to generate the towns export.

Optionally, you can specify a date to only export towns valid at that given date:

    $ python -m geohisto --at-date 2016-01-01

It will be generated within the `exports/communes/` folder with an explicit name.

To also generate the intercommunalities, you need to add the `--intercommunalities` flag.

    $ python -m geohisto --intercommunalities

The whole process takes about one hour and a half to generate both towns and intercommunalities exports (on a core i7 with 16Gb RAM).
You may add some extra output to see the progress by setting the verbosity to `debug`:

    $ python -m geohisto --intercommunalities -v debug

## Tests

If you plan to contribute, you have to install [pytest](http://doc.pytest.org/en/latest/) and launch the test suite:

    $ python -m pytest tests

Note that the duration of the whole test suite run is about 5 minutes.

That's why you would probably prefer to run a particular test:

    $ python -m pytest tests/test_actions.py::test_change_name


## Licenses

See [LICENSE.md](LICENSE.md) file for code and produced data.
