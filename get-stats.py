#!/usr/bin/env python3

import datetime
import pprint
import time
from prometheus_client import start_http_server
from prometheus_client.core import CounterMetricFamily, REGISTRY
from pymongo import MongoClient
import config

client = MongoClient(config.SERVER)
db = client.jenkinsbfa
failureCausesCollection = db.failureCauses

def get_daily_failures(self):
    dailyFailures = {}
    categorizedFailures = []
    uncategorizedFailures = []
    midnight = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
    yesterday_midnight = midnight - datetime.timedelta(days=1)
    dailyFailureCauses = failureCausesCollection.find({'lastOccurred': {'$gte': midnight}})
    daily_failure_causes_count = dailyFailureCauses.count()
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
                
    dailyFailures['categorizedFailures'] = categorizedFailures
    dailyFailures['uncategorizedFailures'] = uncategorizedFailures
    dailyFailures['midnight'] = midnight
    dailyFailures['yesterday_midnight'] = yesterday_midnight
    dailyFailures['daily_failure_causes_count'] = daily_failure_causes_count
    dailyFailures['uniqueCategories'] = uniqueCategories
    return dailyFailures

def get_failure_counts(self):
    dailyFailures = get_daily_failures(self)
    failureCounts = []
    for uniqueCategory in dailyFailures['uniqueCategories']:
        categoryInfo = {}
        categoryInfo['category'] = uniqueCategory.lower()
        categoryInfo['failures'] = failureCausesCollection.collection.count_documents({'lastOccurred': {'$gte': dailyFailures['midnight']}, 'categories': {'$in': [uniqueCategory]}})
        failureCounts.append(categoryInfo)

    uncategorizedFailureInfo = {}
    uncategorizedFailureInfo['category'] = u'uncategorized'
    uncategorizedFailureInfo['failures'] = len(dailyFailures['uncategorizedFailures'])
    failureCounts.append(uncategorizedFailureInfo)

    failure_causes_info = {}
    failure_causes_info['category'] = u'all'
    failure_causes_info['failures'] = dailyFailures['daily_failure_causes_count']
    failureCounts.append(failure_causes_info)
    print(failureCounts)
    return failureCounts

class CustomCollector(object):
    def collect(self):
        c = CounterMetricFamily('jenkins_bfa_failures', 'Total failures since midnight', labels=['failure_category'])
        failureCounts = get_failure_counts(self)
        for failureCount in failureCounts:
            metric_name = failureCount['category']
            metric_value = failureCount['failures']
            c.add_metric([metric_name], metric_value)
        yield c

REGISTRY.register(CustomCollector())


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    while True:
        CustomCollector.collect
        time.sleep(30.0 - time.time() % 30.0)
