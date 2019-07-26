from datetime import datetime, time, timedelta
import pprint
from prometheus_client import start_http_server
from prometheus_client.core import CounterMetricFamily, REGISTRY
from pymongo import MongoClient
import config
client = MongoClient(config.SERVER)
db = client.jenkinsbfa
failureCausesCollection = db.failureCauses
categorizedFailures = []
uncategorizedFailures = []
midnight = datetime.combine(datetime.today(), time.min)
yesterday_midnight = midnight - timedelta(days=1)
dailyFailureCauses = failureCausesCollection.find({'lastOccurred': {'$gte': midnight}})
for dailyFailureCause in dailyFailureCauses:
    if 'categories' in dailyFailureCause.keys():
        categorizedFailures.append(dailyFailureCause)
    else:
        uncategorizedFailures.append(dailyFailureCause)

uniqueCategories = []
for categorizedFailure in categorizedFailures:
    categories = categorizedFailure['categories']
    for category in categories:
        if category not in uniqueCategories:
            uniqueCategories.append(category)

failureCounts = []
for uniqueCategory in uniqueCategories:
    failures = failureCausesCollection.find({'lastOccurred': {'$gte': midnight}, 'categories': {'$in': [uniqueCategory]}})
    categoryInfo = {}
    categoryInfo['category'] = uniqueCategory.lower()
    categoryInfo['failures'] = failures.count()
    failureCounts.append(categoryInfo)

uncategorizedFailureInfo = {}
uncategorizedFailureInfo['category'] = u'uncategorized'
uncategorizedFailureInfo['failures'] = len(uncategorizedFailures)
failureCounts.append(uncategorizedFailureInfo)

# pprint.pprint(failureCounts)

class CustomCollector(object):
    def collect(self):
        c = CounterMetricFamily('jenkins_bfa_failures_total', 'Total failures since midnight', labels=['failure_category'])
        for failureCount in failureCounts:
            metric_name = failureCount['category']
            metric_value = failureCount['failures']
            c.add_metric([metric_name], metric_value)
        c.add_metric(['all'], dailyFailureCauses.count())
        yield c

REGISTRY.register(CustomCollector())


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    while True:
        CustomCollector.collect
