# Agent Check: Zookeeper
{{< img src="integrations/zookeeper/zookeepergraph.png" alt="Zookeeper Dashboard" responsive="true" popup="true">}}
## Overview

The Zookeeper check tracks client connections and latencies, monitors the number of unprocessed requests, and more.

## Setup
### Installation

The Zookeeper check is packaged with the Agent, so simply [install the Agent](https://app.datadoghq.com/account/settings#agent) on your Zookeeper servers.

### Configuration

Create a file `zk.yaml` in the Agent's `conf.d` directory.

#### Metric Collection

*  Add this configuration setup to your `zk.yaml` file to start gathering your [Zookeeper metrics](#metrics):

```
init_config:

instances:
  - host: localhost
    port: 2181
    timeout: 3
```

* See the [sample zk.yaml](https://github.com/DataDog/integrations-core/blob/master/zk/conf.yaml.example) for all available configuration options.

* [Restart the Agent](https://docs.datadoghq.com/agent/faq/agent-commands/#start-stop-restart-the-agent) to start sending Zookeeper metrics to Datadog.

#### Log Collection

**Available for Agent >6.0**

Zookeeper uses the `log4j` logger per default. To activate the logging into a file and customize the format edit the `log4j.properties` file:

```
# Set root logger level to INFO and its only appender to R
log4j.rootLogger=INFO, R
log4j.appender.R.File=/var/log/zookeeper.log
log4j.appender.R.layout=org.apache.log4j.PatternLayout
log4j.appender.R.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} %-5p [%t] %c{1}:%L - %m%n
```

By default, our integration pipeline support the following conversion patterns:

  ```
  %d{yyyy-MM-dd HH:mm:ss} %-5p %c{1}:%L - %m%n
  %d [%t] %-5p %c - %m%n
  %r [%t] %p %c %x - %m%n
  ```

Make sure you clone and edit the integration pipeline if you have a different format.

* Collecting logs is disabled by default in the Datadog Agent, enable it in your `datadog.yaml` file with:

  ```
  logs_enabled: true
  ```

* Add this configuration setup to your `zk.yaml` file to start collecting your Zookeeper Logs:

  ```
  logs:
    - type: file
      path: /var/log/zookeeper.log
      source: zookeeper
      service: myapp
      #To handle multi line that starts with yyyy-mm-dd use the following pattern
      #log_processing_rules:
      #  - type: multi_line
      #    name: log_start_with_date
      #    pattern: \d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])
  ```

* See the [sample zk.yaml](https://github.com/DataDog/integrations-core/blob/master/zk/conf.yaml.example) for all available configuration options.

* [Restart the Agent](https://docs.datadoghq.com/agent/faq/agent-commands/#start-stop-restart-the-agent) to start sending Zookeeper Logs to Datadog.

### Validation

[Run the Agent's `status` subcommand](https://docs.datadoghq.com/agent/faq/agent-commands/#agent-status-and-information) and look for `zk` under the Checks section.

## Compatibility

The Zookeeper check is compatible with all major platforms.

## Data Collected
### Metrics

As of zookeeper 3.4.0, the `mntr` admin command is provided for easy parsing of
zookeeper stats. This check first parses the `stat` admin command for a version
number. If the zookeeper version supports `mntr`, it is also parsed.

Duplicate information is being reported by both `mntr` and `stat`: the duplicated
 `stat` metrics are only kept for backward compatibility.

**Important:** if available, make use of the data reported by `mntr`, not `stat`.

| Metric reported by `mntr` | Duplicate reported by `stat` |
| ------------------------- | ---------------------------- |
| `zookeeper.avg_latency` | `zookeeper.latency.avg` |
| `zookeeper.max_latency` | `zookeeper.latency.max` |
| `zookeeper.min_latency` | `zookeeper.latency.min` |
| `zookeeper.packets_received` | `zookeeper.packets.received` |
| `zookeeper.packets_sent` | `zookeeper.packets.sent` |
| `zookeeper.num_alive_connections` | `zookeeper.connections` |
| `zookeeper.znode_count` | `zookeeper.nodes` |

See [metadata.csv](https://github.com/DataDog/integrations-core/blob/master/zk/metadata.csv)
for a list of metrics provided by this check.

#### Deprecated metrics

Following metrics are still sent but will be removed eventually:
 * `zookeeper.bytes_received`
 * `zookeeper.bytes_sent`
 * `zookeeper.bytes_outstanding`

### Events
The Zookeeper check does not include any event at this time.

### Service Checks

**zookeeper.ruok**:

Sends `ruok` to the monitored node. Returns `OK` with an `imok` response, `WARN` in the case of a different response and `CRITICAL` if no response is received..

**zookeeper.mode**:

The Agent submits this service check if `expected_mode` is configured in `zk.yaml`. The check returns `OK` when Zookeeper's actual mode matches `expected_mode`, otherwise `CRITICAL`.

## Troubleshooting
Need help? Contact [Datadog Support](http://docs.datadoghq.com/help/).

## Further Reading
Learn more about infrastructure monitoring and all our integrations on [our blog](https://www.datadoghq.com/blog/)
