# Jenkins BFA Stats

This script is used to pull stats from a MongoDB instance holding data from Jenkins Build Failure Analyzer. Right now it just prints to the console. Eventually it will expose a Prometheus endpoint.

## Status

This is a work in progress and is not ready for production use

## Configuration

You will need to create `config.py` and add a line like below to it:

```python
SERVER = 'mongodb://mongodb.example.com:27017/'
```

## Usage

```bash
pip install pymongo
python get-stats-for-yesterday.py
```
