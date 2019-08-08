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

## Development

Below is an example of a single entry in the list of failure causes:

```python
Single dailyFailureCause

{
    '_id': ObjectId('sc = 546d33efe4b0220750244af7'),
    'name': 'Apt failure - hash sum mismatch',
    'description': 'When using the \'apt\' package manager, the job may fail with "hash sum mismatch". This can occur when using a caching proxy, or a mirror in an inconsistent state. The job should be retried, and the content mirrored locally.',
    'comment': '',
    'categories': ['apt', 'network', 'debian', 'ubuntu'],
    'indications': [{'@class': 'com.sonyericsson.jenkins.plugins.bfa.model.indication.BuildLogIndication', 'pattern': '.*Hash Sum mismatch.*'}],
    'modifications': [{'user': 'branan', 'time': datetime.datetime(2014, 11, 17, 22, 42, 4, 410000)}],
    'lastOccurred': datetime.datetime(2019, 8, 6, 14, 1, 2, 955000)
}
```
