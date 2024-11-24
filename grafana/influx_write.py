#!/usr/bin/env python3
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import Optional
from datetime import datetime

org = "GK8-HealthCenter"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"
WRITE_TOKEN = "TOKEN"

client = influxdb_client.InfluxDBClient(url=host, token=WRITE_TOKEN, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)




def write_point(measurement:str, field:str, value, tags:Optional[list[dict]]=None, timestamp:Optional[datetime]=None):
    p = influxdb_client.Point(measurement)
    if tags:
        for x in tags:
            p = p.tag(x['column'], x['val'])
    if timestamp:
        p = p.time(time=timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    p = p.field(field, value)
    write_api.write(bucket='customer_view_data', org=org, record=p)







