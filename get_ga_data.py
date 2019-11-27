import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from ga_data import *

# Set your client secret path where you put your client credentials 
CLIENT_SECRETS_PATH = 'key/client_secret.json'

# Replace the string with your clients view id
# https://support.google.com/analytics/answer/1009618
# {"viewId": string}
view_id = ""

# Set the date range for your data
# https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/DateRange
# {"startDate": string, "endDate": string}
start_date = "2019-01-01"
end_date = "2019-01-01"

# Set at least one metric
# https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#Metric
# {"expression": string, "alias": string, "formattingType": enum(MetricType)}
metrics = [{"expression": "ga:transactionRevenue"}, 
           {"expression": "ga:transactions"},
           {"expression": "ga:itemQuantity"},
           {"expression": "ga:itemRevenue"},
           {"expression": "ga:itemsPerPurchase"}]

# Set at least one dimension
# https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#Dimension
#{"name": string, "histogramBuckets": [ string ]}
dimensions = [{"name": "ga:date"},
              {"name": "ga:month"},
              {"name": "ga:campaign"},
              {"name": "ga:transactionId"}]

# Filter out your data based on metric values
# https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#MetricFilterClause
# {"metricName": string, "not": boolean, "operator": enum(Operator), "comparisonValue": string}
metric_filter_clauses = [{"filters":[{"metricName": "", "operator": "", "expressions": [""]}]}]

# Filter out your data based on dimension values
#  https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#DimensionFilterClause
# {"dimensionName": string, "not": boolean, "operator": enum(Operator), "expressions": [ string ], "caseSensitive": boolean}
dimension_filter_clauses = [{"filters":[{"dimensionName": "ga:sourceMedium", "operator": "EXACT", "expressions": ["google / cpc"]}]}]

# Specifies the sorting option
# https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#OrderBy
# {"fieldName": string, "orderType": enum(OrderType), "sortOrder": enum(SortOrder)}
order_bys = [{"fieldName": "", "orderType": "", "sortOrder": ""}]

# Replace with your own segmentId which yo can find in Query Explorer
segments = [{"segmentId": ""}]

# Your data will be grouped by the dimensions or segments you use 
group_by = [""]

# Initiate the analytics client
analytics = initialize_analyticsreporting(CLIENT_SECRETS_PATH)

# Set timer on extraction
start_time = time.time()

# Define dataframe and call the function return_ga_data() from the library
# Comment uncomment the variables that are not being used
df = return_ga_data(analytics,
                    start_date = start_date,
                    end_date = end_date,
                    view_id = view_id,
                    metrics = metrics,
                    dimensions = dimensions,
                    #metric_filter_clauses = metric_filter_clauses,
                    dimension_filter_clauses = dimension_filter_clauses,
                    #order_bys = order_bys,
                    #segments = segments,
                    #group_by = group_by
                   )

# Print runtime on function
print('Running Time --- %s seconds ---' % (time.time() - start_time))

# Save your data to a csv file
df.to_csv('df.csv', index=False)