# GA-reporting-API
Using the google analytics reporting api to fetch data from GA. 

* ga_data.py
  - Contains the functions for connecting to GA, fetching the data and avoiding sampling.
    - To avoid sampling in each API request, we're using nextPageToken to enable more than 10,000 results in each API request.
    - In this code, by default, An API request will be made day by day no matter how large the date range you are giving, which means we're sending request for data at a daily level.
    - If the data is somehow sampled, a samplesReadCounts and samplingSpaceSizes will be printed out so you know that sampling has occured.
  - Functions:
    - initialize_analyticsreporting(CLIENT_SECRETS_PATH)
    - return_ga_data(analytics,
                       start_date,
                       end_date,
                       view_id,
                       metrics,
                       dimensions,
                       metric_filter_clauses=[],
                       dimension_filter_clauses=[],
                       order_bys=[],
                       segments=[],
                       split_dates = True,
                       group_by=[],
                       SLEEP_TIME = 2
                      )

* get_ga_data.py
  - This file contains the script in which you specify all variables for fetching the data from GA.
* key
  - Put your client_secret.json file in this folder.
