#!/usr/bin/env python3
import datetime

import influx_read
import influx_write


envs_display_names = {"gk8-etoro-06": "eToro Cloud Environment",
                      "gk8-etoro_01": "eToro Production BB",
                      "gk8-etoro_03": "eToro Deep Cold",
                      "gk8-evergreen-01": "Evergreen",
                      "gk8-galaxy-02": "Galaxy Production NY",
                      # "gk8-prosegur-03": "Prosegur Spain",
                      "gk8-prosegur_saopaulo-04": "Prosegur Brazil",
                      "gk8-secondmkt-01": "SecondMarket",
                      # "gk8-securrency-01": "Securrency Cloud Staging",
                      "gk8-starkware-01": "Starkware",
                      "gk8-tx24_dubai-02": "Tx24",
                      "gk8-customerspilot-01": "Customers Pilot",
                      "gk8-allunity_staging-01": "All Unity",
                      "gk8-dtcc_abudhabi_01": "DTCC",
                      "gk8-salesdemo-01": "Sales demo",
                      "gk8-sales-02": "Customer success"
}

v11_envs = ["gk8-etoro_03",
            # "gk8-prosegur-03",
            "gk8-secondmkt-01",
            "gk8-securrency-01",
            "gk8-etoro_01"]


for x in envs_display_names:
    envs_display_names[x] = envs_display_names[x] + " ("+x+")"

def write_nodes_health():
    envs_nodes_health = influx_read.most_severe_node_health_for_each_env()
    for env in envs_nodes_health:
        influx_write.write_point(measurement="MCS",
                                 field="nodes_health",
                                 value=envs_nodes_health[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])


def write_disk_usage():
    envs_disk_usage = influx_read.get_highest_cs_disk_usage()
    for env in envs_disk_usage:
        influx_write.write_point(measurement="DiskUsage",
                                 field="percentage",
                                 value=envs_disk_usage[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])

def write_memory_usage():
    envs_memory_usage = influx_read.get_highest_cs_memory_usage()
    for env in envs_memory_usage:
        influx_write.write_point(measurement="MemoryUsage",
                                 field="percentage",
                                 value=envs_memory_usage[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])

def write_state_sequence_sync():
    envs_sync = influx_read.get_state_sequences()
    for env in envs_sync:
        influx_write.write_point(measurement="StateSequenceSync",
                                 field="status",
                                 value=envs_sync[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])


def write_mongo_coms():
    mongo_coms = influx_read.get_mongo_com()
    for env in mongo_coms:
        influx_write.write_point(measurement="mongo",
                                 field="status",
                                 value=mongo_coms[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])



def write_last_seen():
    last_seen = influx_read.get_last_seen()
    for env in last_seen:
        influx_write.write_point(measurement="last_seen",
                                 field="val",
                                 value=last_seen[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])


def write_system_health():
    envs_disk_usage = influx_read.get_highest_cs_disk_usage()
    envs_ram_usage = influx_read.get_highest_cs_memory_usage()
    for env in envs_disk_usage:
        highest_usage = envs_disk_usage[env] if env in v11_envs else max(envs_disk_usage[env], envs_ram_usage[env])
        influx_write.write_point(measurement="ResourcesUsage",
                                 field="percentage",
                                 value=highest_usage,
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}])

def write_display_names():
    for env, display_name in envs_display_names.items():
        influx_write.write_point(measurement=display_name,
                                 field="full_env_name",
                                 value=env)


def write_cs_time_diff():
    time_diffs = influx_read.get_highest_cs_time_diff()
    for env in time_diffs:
        influx_write.write_point(measurement="cs_time_diff",
                                 field="highest",
                                 value=time_diffs[env],
                                 tags=[{'column': "EnvName",
                                        'val': envs_display_names[env]}]
                                 )


def write_avg_cpu_usage():
    usage = influx_read.get_mean_cpu_usage()
    for env in usage:
        influx_write.write_point(measurement="CPU",
                                 field=envs_display_names[env],
                                 value=usage[env]
                                 )

def write_mcs_version():
    versions = influx_read.get_mcs_version()
    for env in versions:
        if env not in envs_display_names:
            continue
        influx_write.write_point(measurement="product_version",
                                 field=envs_display_names[env],
                                 value=versions[env]
                                 )



# write_display_names()


funcs = [write_avg_cpu_usage, write_disk_usage, write_memory_usage,
         write_system_health, write_last_seen, write_nodes_health,
         write_mongo_coms, write_cs_time_diff, write_mcs_version]


for func in funcs:
    try:
        func()
    except Exception as e:
        print(func.__name__)
        print(e)

# try:
#     write_avg_cpu_usage()
#     write_system_health()
#     write_nodes_health()
#     # write_state_sequence_sync()
#     write_mongo_coms()
#     write_last_seen()
#     write_cs_time_diff()
#     write_disk_usage()
#     write_memory_usage()
#     print("Success")
# except Exception as e:
#     print(e)

