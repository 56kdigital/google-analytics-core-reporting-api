import argparse
from googleapiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import pandas as pd
import time
import os
import errno
from datetime import datetime, timedelta
from time import sleep

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')

def initialize_analyticsreporting(CLIENT_SECRETS_PATH):
  '''Initializes the analyticsreporting service object.
  Returns:
    analytics an authorized analyticsreporting service object.
  '''
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  storage = file.Storage('analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
      credentials = tools.run_flow(flow, storage, flags)

  http = credentials.authorize(http=httplib2.Http())

  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI,cache_discovery=False)

  return analytics

def get_report(
    analytics,
    nextPageToken,
    start_date,
    end_date,
    view_id,
    metrics,
    dimensions,
    metric_filter_clauses,
    dimension_filter_clauses,
    order_bys,
    segments,
):
    '''Use the Analytics Service Object to query the Analytics Reporting API V4. This function will be called inside get_ga_data().'''
    return (
        analytics.reports()
        .batchGet(
            body={
                "reportRequests": [
                    {
                        "viewId": view_id,
                        "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                        "metrics": metrics,
                        "dimensions": dimensions,
                        "metricFilterClauses": metric_filter_clauses,
                        "dimensionFilterClauses": dimension_filter_clauses,
                        "orderBys": order_bys,
                        "pageToken": nextPageToken,
                        "pageSize": 10000,
                        "segments": segments,
                        "includeEmptyRows": "true",
                        "samplingLevel": "DEFAULT",
                        "hideTotals": "false",
                        "hideValueRanges": "false"
                    }
                ]
            }
        )
        .execute()
    )

def print_response(response):
    '''Transforming the raw data into a dataframe. This function will be called inside get_ga_data().'''
    list = []
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get(
            'metricHeaderEntries', []
        )
        rows = report.get('data', {}).get('rows', [])

        samplesReadCounts = report.get('data', {}).get('samplesReadCounts', [])
        if samplesReadCounts != []:
            print('Data has been sampled!')
            print(samplesReadCounts)
        samplingSpaceSizes = report.get('data', {}).get('samplingSpaceSizes', [])
        if samplingSpaceSizes != []:
            print(samplingSpaceSizes)

        for row in rows:
            dict = {}
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                dict[header] = dimension

            for i, values in enumerate(dateRangeValues):
                for metric, value in zip(metricHeaders, values.get('values')):
                    if ',' in value or ',' in value:
                        dict[metric.get('name')] = float(value)
                    else:
                        dict[metric.get('name')] = float(value)

            list.append(dict)

        df = pd.DataFrame(list)
        return df

def get_ga_data(
    analytics,
    start_date,
    end_date,
    view_id,
    metrics,
    dimensions,
    metric_filter_clauses,
    dimension_filter_clauses,
    order_bys,
    segments,
    SLEEP_TIME,
):
    '''Splitting one query into multiple queries to get one days unsampled data. This function will be called inside return_ga_data().'''
    ga = get_report(
        analytics,
        '',
        start_date,
        end_date,
        view_id,
        metrics,
        dimensions,
        metric_filter_clauses,
        dimension_filter_clauses,
        order_bys,
        segments,
    )
    df_total = print_response(ga)
    token = ga.get('reports', [])[0].get('nextPageToken')
    while token is not None:
        ga = get_report(
            analytics,
            token,
            start_date,
            end_date,
            view_id,
            metrics,
            dimensions,
            metric_filter_clauses,
            dimension_filter_clauses,
            order_bys,
            segments,
        )
        df = print_response(ga)
        df_total = df_total.append(df)
        token = ga.get('reports', [])[0].get('nextPageToken')
        sleep(SLEEP_TIME)

    return df_total

def return_ga_data(
    analytics,
    start_date,
    end_date,
    view_id,
    metrics,
    dimensions,
    metric_filter_clauses=[],
    dimension_filter_clauses=[],
    order_bys=[],
    segments=[],
    split_dates=True,
    group_by=[],
    SLEEP_TIME=2,
):
    '''Fetching day by day data. This function will be called in the external .py file'''
    if split_dates == False:
        return get_ga_data(
            analytics,
            start_date,
            end_date,
            view_id,
            metrics,
            dimensions,
            metric_filter_clauses,
            dimension_filter_clauses,
            order_bys,
            segments,
            SLEEP_TIME,
        )
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        delta = end_date - start_date
        dates = []

        for i in range(delta.days + 1):
            dates.append(start_date + timedelta(days=i))

        df_total = pd.DataFrame()
        for date in dates:
            date = str(date)
            df_total = df_total.append(
                get_ga_data(
                    analytics,
                    date,
                    date,
                    view_id,
                    metrics,
                    dimensions,
                    metric_filter_clauses,
                    dimension_filter_clauses,
                    order_bys,
                    segments,
                    SLEEP_TIME,
                )
            )
            sleep(SLEEP_TIME)

        if len(group_by) != 0:
            if df_total.empty:
                return df_total
            else:
                df_total = df_total.groupby(group_by, as_index=False).sum()
        return df_total