#!/usr/bin/env python3
import influxdb_client
import pandas as pd
import json
import re
from typing import Optional
from datetime import datetime as dt, timedelta



prod_envs = ["gk8-etoro-06",
             "gk8-etoro_01",
             "gk8-etoro_03",
             "gk8-evergreen-01",
             "gk8-galaxy-02",
             # "gk8-prosegur-03",
             "gk8-prosegur_saopaulo-04",
             "gk8-secondmkt-01",
             # "gk8-securrency-01",
             "gk8-starkware-01",
             "gk8-tx24_dubai-02",
             "gk8-customerspilot-01",
             "gk8-allunity_staging-01",
             "gk8-dtcc_abudhabi_01",
             "gk8-salesdemo-01",
             "gk8-sales-02"]

v11_envs = ["gk8-etoro_03",
            # "gk8-prosegur-03",
            "gk8-secondmkt-01",
            "gk8-securrency-01",
            "gk8-etoro_01"]

env_and_used_currencies = {"gk8-etoro-06": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","DOT","XRP","SMR","XLM","XTZ"],
                           "gk8-etoro_01": ["BTC","BCH","ADA","ATOM","ETH","ETHW","HBAR","MIOTA","NEAR","XRP","SMR","XLM","XTZ"],
                           "gk8-etoro_03": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","XRP","SMR","XLM","XTZ"],
                           "gk8-evergreen-01": ["BTC","BCH","AETH","AURORA","BASE","ETH","GLMR", "OETH", "MATIC"],
                           "gk8-galaxy-02": ["ARB","AVAX","BTC","BCH","ADA","ATOM","ETH","HBAR","NEAR","DOT","XLM","XTZ"],
                           # "gk8-prosegur-03": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","XRP","SMR","XLM","XTZ"],
                           "gk8-prosegur_saopaulo-04": ["BTC","ETH","XRP"],
                           "gk8-secondmkt-01": ["BTC","BCH","ADA","ATOM","ETH","HBAR","NEAR","MATIC","XRP","SMR","XLM","XTZ"],
                           # "gk8-securrency-01": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","XRP","SMR","XLM","XTZ"],
                           "gk8-starkware-01": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","XRP","SMR","XLM","XTZ"],
                           "gk8-tx24_dubai-02": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR", "DOT","XRP","SMR","XLM","XTZ"],
                           "gk8-customerspilot-01": ["BTC","BCH","ADA","ETH","XLM"],
                           "gk8-allunity_staging-01": ["BTC","BCH","ADA","ETH","HBAR","XTZ", "TRX"],
                           "gk8-dtcc_abudhabi_01": ["BTC","BCH","ADA","ETH","MIOTA","SMR","HBAR","XTZ", "TRX", "XRP", "ATOM", "XLM", "NEAR", "DOT"],
                           "gk8-salesdemo-01": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","DOT","XRP","SMR","XLM","XTZ", "TRX"],
                           "gk8-sales-02": ["BTC","BCH","ADA","ATOM","ETH","HBAR","MIOTA","NEAR","DOT","XRP","SMR","XLM","XTZ", "TRX", "AETH"]}




READ_ONLY_TOKEN = "TOKEN"
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


def get_latest_nodes_health():
    q = parse_flux_query(start="-10m", measurement='MCS', field='Health')
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "CurrencySymbol"], keep="first")
    return df


def most_severe_node_health_for_each_env(envs:list=prod_envs):
    df = get_latest_nodes_health()
    severity = ["Error", "Warning", "Unknown", "OK"]
    res = {}
    for env in envs:
        status = []
        x = df.loc[df["EnvName"]==env]
        x = pd.Series(x._value.values, index=x.CurrencySymbol).to_dict()
        for currency in env_and_used_currencies[env]:
            if currency in x:
                status.append(x[currency])
            else:
                status.append("Unknown")
        status = ["OK" if y==3 else y for y in status]
        status = ["Warning" if y == 2 else y for y in status]
        status = ["Error" if y == 1 else y for y in status]
        for i in severity:
            if i in status:
                res[env] = i
                break
    return res

def get_highest_cs_disk_usage(envs:list=prod_envs):
    q = parse_flux_query(start='-10m', conds={"SystemHealthType":"DiskUsage"})
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "_measurement", "_field"], keep="first")
    total_dict = {}
    usage_dict = {}
    for env in envs:
        total_df = df.loc[df["_field"]=="TotalMB"]
        total_df = total_df.loc[total_df["EnvName"]==env]
        x = pd.Series(total_df._value.values, index=total_df._measurement).to_dict()
        total_dict[env] = x
        used_df = df.loc[df["_field"] == "UsedMB"]
        used_df = used_df.loc[used_df["EnvName"] == env]
        x = pd.Series(used_df._value.values, index=used_df._measurement).to_dict()
        usage_dict[env] = x
    highest_usage_percentage = {}
    for env in envs:
        if sorted(list(usage_dict[env].keys())) == sorted(list(total_dict[env].keys())):
            percentages = [100 * usage_dict[env][x]/total_dict[env][x]*1000//10/100 for x in usage_dict[env].keys()]
            if len(percentages) > 0:
                highest_usage_percentage[env] = max(percentages)
    return highest_usage_percentage


def get_state_sequences(envs=prod_envs):
    q = parse_flux_query(field="StateSequence")
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "_measurement"], keep="first")
    states = {}
    for env in envs:
        temp_df = df[df["EnvName"] == env]
        s = pd.Series(temp_df._value.values, index=temp_df._measurement).to_dict()
        if "MCS" in s and "Cold" in s:
            states[env] = "OK" if s['MCS']-s['Cold'] <= 1 else "Error"
        else:
            states[env] = "Unknown"
    return states


def get_last_seen(envs=prod_envs):
    with open("last_seen.json", 'r') as f:
        res = json.loads(f.read())
    for x in list(res.keys()):
        if x not in envs:
            res.pop(x)
    q = parse_flux_query(field="LastSeen")
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName"], keep="first")
    d = pd.Series(df._value.values, index=df.EnvName).to_dict()
    for env in envs:
        if env in d:
            try:
                res[env] = (dt.fromtimestamp(int(d[env])) + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            except:
                res[env] = "Unknown"
        elif env not in res:
            res[env] = "Unknown"
    with open("last_seen.json", 'w') as f:
        f.write(json.dumps(res))
    return res


def get_mongo_com(envs=prod_envs):
    q = parse_flux_query(field="MongoCommunication")
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "_measurement"], keep="first")
    res = {}
    for env in envs:
        temp_df = df.loc[df["EnvName"]==env]
        if len(temp_df)==0:
            continue
        if any(df["_value"]!=True):
            res[env]="Error"
            continue
        res[env] = "OK"
    return res



def get_ip_ports_env_dict():
    # q = parse_flux_query(start="-24h", measurement="MCS", field="IpPort")
    # r = json.loads(query_api.query(q).to_json())
    # df = pd.DataFrame(r)
    # df = df.sort_values(by="_time", ascending=False)
    # df = df.drop_duplicates(subset=["EnvName", "CurrencyName"], keep="first")
    # df["_value"] = df["_value"].str.replace(r":[0-9][0-9]+", '', regex=True)
    # df.to_csv("df.csv")
    df = pd.read_csv("df.csv")
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


def get_highest_cs_memory_usage(envs:list=prod_envs):
    q = parse_flux_query(start='-10m', conds={"SystemHealthType":"MemoryUsage"})
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "_measurement", "_field"], keep="first")
    total_dict = {}
    usage_dict = {}
    for env in envs:
        total_df = df.loc[df["_field"]=="TotalMB"]
        total_df = total_df.loc[total_df["EnvName"]==env]
        x = pd.Series(total_df._value.values, index=total_df._measurement).to_dict()
        total_dict[env] = x
        used_df = df.loc[df["_field"] == "UsedMB"]
        used_df = used_df.loc[used_df["EnvName"] == env]
        x = pd.Series(used_df._value.values, index=used_df._measurement).to_dict()
        usage_dict[env] = x
    highest_usage_percentage = {}
    for env in envs:
        assert sorted(list(usage_dict[env].keys())) == sorted(list(total_dict[env].keys()))
        percentages = [100 * usage_dict[env][x]/total_dict[env][x]*1000//10/100 for x in usage_dict[env].keys()]
        if len(percentages) > 0:
            highest_usage_percentage[env] = max(percentages)
    return highest_usage_percentage

def get_highest_cs_time_diff(envs:list=prod_envs):
    q = parse_flux_query(start='-10m', measurement="MCS", field="CosignerTimeDiff")
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName", "CosignerIndex"], keep="first")
    res = {}
    for env in envs:
        if env in v11_envs:
            res[env] = "V11"
            continue
        temp_df = df.loc[df["EnvName"]==env]
        if len(temp_df)==0:
            continue
        max_time_diff = max(temp_df._value)
        res[env] = max_time_diff
    return res

def get_mean_cpu_usage(envs:list = prod_envs, time_interval_mins=15):
    q = parse_flux_query(start=f'-{str(time_interval_mins)}m', field="Usage", conds={"SystemHealthType":"Cpu"})
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.groupby(["EnvName", "_measurement"]).mean(numeric_only=True).reset_index()
    df = df.sort_values(by=["_value"], ascending=False)
    df = df.drop_duplicates(["EnvName"], keep="first")
    temp = pd.Series(df._value.values, index=df.EnvName).to_dict()
    res = {}
    for env, val in temp.items():
        if env in envs:
            res[env] = val
    return res

def get_mcs_version():
    q = parse_flux_query(start=f'-10m', field="ProductVersion", measurement='MCS')
    r = json.loads(query_api.query(q).to_json())
    df = pd.DataFrame(r)
    df = df.sort_values(by="_time", ascending=False)
    df = df.drop_duplicates(subset=["EnvName"], keep="first")
    return pd.Series(df._value.values, index=df.EnvName).to_dict()


