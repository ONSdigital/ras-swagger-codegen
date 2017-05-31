# RAS-Swagger-Codegen

This is an experimental services aimed at automatically generating Microservice boilerplate code directly from the swagger API service. It's now is a usable state but be warned it's still a little short on documentation and error checking.

Switch to the [GitHub Pages version of this page.](https://onsdigital.github.io/ras-swagger-codegen/)

### Dependencies

In order to use this repository you will need to install Java on your machine and the [swagger-codegen](https://github.com/swagger-api/swagger-codegen) application. Please follow the link for details about how to do this.

After checking out the repository, create another folder at the same level in your directory tree called 'ras-repos', this is where the auto-generated code will be created.

#### Synchronise Swagger API with Codebase

```bash
./swagger_refresh.py
```

This will iterrogate the **packages.txt** file to recover the list of API's were going to manage. When you create a new API the first thing you will need to do is to add an entry to this file. For now the format is very simple, one line per API in the following format;

* api-name - this is the name of the API defined in swagger
* version  - this is the version of the API we're working with
* repo     - this is the name of the GitHub repository we are targetting
* url      - is the prefix (username) we're aiming for in swagger
* hostname - is the name of the host we're want to test against

Please see the demo entry for a live example.

After running the script, you should find a working file-tree in ../ras-repos/(**repo**) and you should be able to
use the **yaml_tool** script to configure your local customisations / logic.

```bash
./yaml_tool.py (repo) [(cmd) [(options)]]
```
If you try;

```bash
./yaml_tool.py (repo) list
```
You should see a list of endpoints the code generator has deployed, this should all 'work' and deploy a default response. In order to cusomise an endpoint, use;

```bash
./yaml_tool (repo) implement (endpoint)
```

Where (endpoint) is the function name associated with the endpoint as found from the results of the **list** command. The generated code can be found in the **controllers** folder, do not modify this code as it will be overwritten. All customisations will be implemented in the 'controllers_local' folder which is not touched by the code generator.

After implementing your new endpoint(s), you can modify the endpoint routing table using;

```bash
yaml_tool (repo) route
```

When you come to test your code locally, move to your repo and use the;

```bash
./scripts/run.sh
```

Shell script. This will (if necessary) create a virtual environment (virtenv) and all the depencies listed in your **requirements.txt** file. The "main" file that's executed is **__main__.py**, this will be overwritten by the code generator so avoid modifying this. If you need modifications, refer to the 'templates' folder in this repo which is used to tweak the code generator's results.

### Git

When you have an initial repository ready to go, create a new repository on GitHub then run;

```bash
./scripts/git_push.sh ONSdigital (repo) "Initial commit"
```

### CodeCov

In order to get Travis working with CodeCov, you will need to edit templates/scripts/cckeys.json and add a key
for your repo. The format is {'<repo name>': '<secret'} where the secret can be obtained by running;

```bash
travis encrypt CODECOV_TOKEN="...." -r ONSdigital/<repo name>
```

If you don't have 'travis', it's available via 'gem'. (it's ruby package)
On Ubuntu;
```bash
apt install ruby ruby-dev
gem install travis
```

## Examples

##### See what's been implemented so far ...

```bash
$ ./yaml_tool.py ras-collection-instrument-demo list
[X] get_collection_instrument_by_id :: /collectioninstrument/id/{id}
[X] static_typ_uri_get :: /static/{typ}/{uri}
[X] define_batch_survey_ce_count_post :: /define_batch/{survey}/{ce}/{count}
[X] surveys_get :: /surveys
[X] upload_survey_ce_post :: /upload/{survey}/{ce}
[X] activate_survey_ce_post :: /activate/{survey}/{ce}
[X] download_csv_get :: /download_csv
[X] clear_batch_survey_ce_post :: /clear_batch/{survey}/{ce}
[X] status_survey_ce_get :: /status/{survey}/{ce}
[ ] collectioninstrument_get :: /collectioninstrument
[ ] collectioninstrument_id_id_options :: /collectioninstrument/id/{id}
[ ] collectioninstrument_get :: /collectioninstrument
[ ] collectioninstrument_post :: /collectioninstrument
[ ] get_collection_instrument_by_id :: /collectioninstrument/id/{id}
[ ] collectioninstrument_id_id_options :: /collectioninstrument/id/{id}
[ ] collectioninstrument_id_id_put :: /collectioninstrument/id/{id}
```

##### Implement a new routine ...
```bash
$ ./yaml_tool.py ras-collection-instrument-demo implement get_collection_instrument_by_id
```

##### See how much we've done ...
```bash
$ ./yaml_tool.py ras-collection-instrument-demo status
Total of "16" endpoints, "9" implemented "56"%
```

##### Explicitly update the routing table ...
```bash
$ ./yaml_tool.py ras-collection-instrument-demo route
```
##### Where's my stuff?!

In the generated code;

* swagger_server/controllers_local - your code goes here
* swagger_server/models_local - database models go in here (see below)
* swagger_server/tests_local - your tests go here

In swagger-codegen;

* templates - ONS specific changes to the default generated code go here

To Force a rebuild on all your repo's, remove the contents of the /apis folder.

..
##### Specifying database models

Database models should be added to swagger_server/models_local. These can be structured however you choose,
albeit with the following two constraints:

* All model classes must inherit from the Base class in swagger_server/models_local/base.py. This enables the DB creation script to 'inject' a postgres schema by directly manipulating the metadata of the common Base.
* All models should be aliased in the module swagger_server/models_local/_model.py, which is imported by the DB creation script. 
