## Traffic simulator for wellfed
### Usage
To start the web server run the following command
```sh
python3 main.py
```
### Environment variables
If you want to change the default values, just set the environment variable in the shell: `export VAR=VALUE`

Name        | Default                 | Description
------------|-------------------------|------------
SIM_PORT    | 8050                    | The port of the web server
DEBUG       | False                   | If set to `True` enables hot reloading of the python code
WELLFED_URL | `http://localhost:5173` | The url of the wellfed frontend
