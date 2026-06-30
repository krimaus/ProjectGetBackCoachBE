run app in dev mode -> `PYTHONPATH=src poetry run fastapi dev src/app/main.py`
run docker with db -> `sudo docker compose up`
database needs to be running for tests

vscode settings.json:
```
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "src"
  ],
"python.testing.cwd": "${workspaceFolder}",
"python-envs.defaultEnvManager": "ms-python.python:poetry",
"python-envs.defaultPackageManager": "ms-python.python:poetry",
"files.exclude": {
  "**/__pycache__": true,
  "**/*.pyc": true
}
}
```

wyszukanie nieaktywnych zawodników
endpointy do podpowiedzi przy wyszukiwaniu