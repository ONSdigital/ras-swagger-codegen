# RAS-Swagger-Codegen

This is an experimental services aimed at automatically generating Microservice boilerplate code directly from the swagger API service. Please do not attempt to use this just for the moment, however in principle this is how it's supposed to work.

After checking out the repository, create another folder at the same level in your directory tree called 'ras-repos', this is where the auto-generated code will be created.

###

```bash
./swagger_refresh.py
```

This will iterrogate the **packages.txt** file to recover the list of API's were going to manage. When you create a new API the first thing you will need to do is to add an entry to this file. For now the format is very simple, one line per API in the following format;

api-name - this is the name of the API defined in swagger
version  - this is the version of the API we're working with
repo     - this is the name of the GitHub repository we are targetting
url      - is the prefix (username) we're aiming for in swagger
hostname - is the name of the host we're want to test against

Please see the demo entry for a live example. [this is likely to change]

After running the script, you should find a working file-tree in ../ras-repos/(**repo**) and you should be able to use the **yaml_tool** script to configure your local customisations / logic.

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
./run.sh
```

Shell script. This will (if necessary) create a virtual environment (virtenv) and all the depencies listed in your **requirements.txt** file. The "main" file that's executed is **__main__.py**, this will be overwritten by the code generator so avoid modifying this. If you need modifications, refer to the 'templates' folder in this repo which is used to tweak the code generator's results.

### Git

When you have an initial repository ready to go, create a new repository on GitHub then run;

```bash
./git_push.sh ONSdigital (repo) "Initial commit"
```