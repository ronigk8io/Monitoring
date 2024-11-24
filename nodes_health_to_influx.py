#!/usr/bin/env python3
import re

import influxdb_client
import json
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import Optional
from datetime import datetime as dt, timedelta


with open("ips_envs_mapping.json", 'r') as f:
    ip_to_env_and_currency = json.loads(f.read())

org = "GK8-HealthCenter"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"
WRITE_TOKEN = "FZ5D_pbWgWTRLoszSxzH2UV_XfPpQMaCPcAEIySC0z4Lzg-lrPxUCn0AK0Y9vjuPB-7lpP8jMJyycreBwIMMnw=="
client = influxdb_client.InfluxDBClient(url=host, token=WRITE_TOKEN, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)


def write_point(measurement:str, field:str, value, tags:Optional[list[dict]]):
    p = influxdb_client.Point(measurement)
    if tags:
        for x in tags:
            p = p.tag(x['column'], x['val'])
    p = p.field(field, value)
    write_api.write(bucket='customer_view_data', org=org, record=p)


def read_latest_check():
    with open("latest_check", 'r') as f:
        latest_check = f.read()
    t = dt.strptime(latest_check.split("\n")[0], "%Y-%m-%d %H:%M:%S")
    if (dt.now() - t) > timedelta(minutes=130):
        return
    tested_nodes = latest_check.split("\n")[1].replace('\'', "\"")
    tested_nodes = json.loads(tested_nodes)
    issues = latest_check.split("\n")[2:]
    res = {}
    for row in issues:
        if len(row)>0 and re.findall(r".*\|.*\|.*\|.*\|.*\|.*\|.*", row) == [row]:
            srow = row.split(" | ")
            ip = srow[4]
            currency_symbol = srow[0]
            our_blocknum = srow[2]
            online_blocknum = srow[3]
            if our_blocknum.isdigit() and online_blocknum.isdigit():
                if int(our_blocknum) <= 0:
                    res[ip] = [currency_symbol, "Error"]
                elif int(online_blocknum) <= 0:
                    res[ip] = [currency_symbol, "Monitoring Failed"]
                else:
                    res[ip] = abs(int(our_blocknum)-int(online_blocknum))
            elif our_blocknum.isdigit():
                res[ip] = [currency_symbol, "Monitoring Failed"]
            else:
                res[ip] = [currency_symbol, "Error"]
    for node in tested_nodes:
        ip = node['ip']
        currency_symbol = node['currency']
        if ip not in res:
            res[ip] = [currency_symbol, "OK"]
    for ip in res:
        res[ip][0] = res[ip][0].upper()
    return res



def write_nodes_status_to_influx(nodes_status):
    for ip in nodes_status:
        if ip not in ip_to_env_and_currency:
            continue
        currencies = ip_to_env_and_currency[ip]['currencies']
        envs = ip_to_env_and_currency[ip]['envs']
        for i in range(len(currencies)):
            write_point(measurement="monitoring_server",
                        field="status",
                        value=nodes_status[ip][1],
                        tags=[{'column': "MonitoringEnvName",
                               'val': envs[i]},
                              {'column': "CurrencyName",
                               'val': currencies[i]},
                              {'column': 'ip',
                               'val': ip}
                          ])
            write_point(measurement="monitoring_server",
                        field="node_ip",
                        value=ip,
                        tags=[{'column': "MonitoringEnvName",
                               'val': envs[i]},
                              {'column': "CurrencyName",
                               'val': currencies[i]},
                              ])

write_nodes_status_to_influx(read_latest_check())





