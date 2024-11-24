#!/usr/bin/env python3

import influxdb_client
import pandas as pd
import json
from typing import Optional

READ_ONLY_TOKEN = "WPxsht_EKrHMrBZZGRU7OIrHYcfOaxHKl0UPBaedU25hwoQXA0I-T6tXuRVv3eK9RsHUF6ikaapROalW5waIfg=="
org = "GK8-HealthCenter"
host = "https://us-east-1-1.aws.cloud2.influxdata.com"


client = influxdb_client.InfluxDBClient(url=host, token=READ_ONLY_TOKEN, org=org)
query_api = client.query_api()


def parse_flux_query(start:str='-10m', measurement:Optional[str]=None, field:Optional[str]=None, envs:Optional[list|str]=None, conds:Optional[dict]={}):
    q = f"""
    from(bucket: "data")
    |> range(start: {start})"""
    if measurement:
        q = f"""{q}
|> filter(fn: (r) => r._measurement == "{measurement}")"""

    if field:
        q = f"""{q}
    |> filter(fn: (r) => r._field == "{field}") """
    if envs:
        if isinstance(envs, str):
            envs = [envs]
        envs = ['\"'+x+'\"' for x in envs]
        envs = " or r.EnvName == ".join(envs)
        q = f"""{q}
    |> filter(fn: (r) => r.EnvName == {envs}) """
    for x in conds:
        q = f"""{q}
|> filter(fn: (r) => r.{x} == "{conds[x]}")"""
    return q


def get_ip_ports_env_dict():
    q = parse_flux_query(start="-1h", measurement="MCS", field="IpPort")
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "CurrencyName"], keep="first")
    df["_value"] = df["_value"].str.replace(r":[0-9][0-9]+", '', regex=True)
    ips = list(set(df["_value"].to_list()))
    res = {}
    for ip in ips:
        temp_df = df.loc[df["_value"]==ip]
        currencies = temp_df["CurrencyName"].to_list()
        envs = temp_df["EnvName"].to_list()
        assert len(currencies)==len(envs)
        res[ip] = {'currencies': currencies,
                   'envs': envs}
    return res


with open("ips_envs_mapping.json", 'w') as f:
    f.write(json.dumps(get_ip_ports_env_dict()))
