from datetime import datetime, time, timedelta
import pprint
from pymongo import MongoClient
import config
client = MongoClient(config.SERVER)
db = client.jenkinsbfa
failureCausesCollection = db.failureCauses
categorizedFailures = []
uncategorizedFailures = []
midnight = datetime.combine(datetime.today(), time.min)
yesterday_midnight = midnight - timedelta(days=1)
dailyFailureCauses = failureCausesCollection.find({'lastOccurred': {'$gte': yesterday_midnight, '$lt': midnight}})
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
    failures = failureCausesCollection.find({'lastOccurred': {'$gte': yesterday_midnight, '$lt': midnight}, 'categories': {'$in': [uniqueCategory]}})
    categoryInfo = {}
    categoryInfo['category'] = uniqueCategory
    categoryInfo['failures'] = failures.count()
    failureCounts.append(categoryInfo)

uncategorizedFailureInfo = {}
uncategorizedFailureInfo['category'] = u'uncategorized'
uncategorizedFailureInfo['failures'] = len(uncategorizedFailures)
failureCounts.append(uncategorizedFailureInfo)

pprint.pprint(failureCounts)
