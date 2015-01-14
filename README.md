# n2cw - Nagios to CloudWatch

n2cw is a wrapper for check scripts that implement the
[Nagios Plugin API](http://nagios.sourceforge.net/docs/3_0/pluginapi.html). It
runs the specified check command and pushes the results, optionally including
metrics for all [perfdata](http://nagios.sourceforge.net/docs/3_0/perfdata.html).

## Installation

```
pip install n2cw
```

## Usage

```
usage: n2cw [options] namespace base_name -- command

A wrapper for nagios-style checks that pushes check status and perfdata to
CloudWatch metrics.

positional arguments:
  namespace             CloudWatch namespace
  base_name             Base name for checks
  command               Command (nagios check) to run

optional arguments:
  -h, --help            show this help message and exit
  --dimensions key=value,key=value
                        CloudWatch metric dimensions
  --noop                Don't push metrics, just log
  --no-perfdata         Don't send metrics for performance data
  --no-status           Don't send the check status output
```

`command` is the full command line, with arguments, for the nagios plugin you
wish to run.

## Example

```
n2cw --dimensions "Host=webserver1" MySuperWebsite Disk -- ./check_disk -w 10% -c 5% -p / -k 
```

If the output of check_disk was ...

```
DISK OK - free space: / 7292772 kB (49% inode=88%);| /=7402636kB;15481742;15481741;0;15481840
```

The following metrics would be pushed to CloudWatch:

```
Namespace       Metric Name  Value    Dimensions
-----------------------------------------------------
MySuperWebsite  Disk-Status  0        Host=webserver1
MySuperWebsite  Disk-/       7292772  Host=webserver1
```

The value of the *-Status* metric is the check return code (so OK is 0, WARNING
is 1, etc).
