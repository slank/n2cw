#!/usr/bin/env python
'''
A wrapper for nagios-style checks that pushes check status and
perfdata to CloudWatch metrics.
'''
import botocore.session
from argparse import ArgumentParser
from subprocess import (
    check_output,
    CalledProcessError,
)


class TestClient(object):
    def __init__(self):
        import logging
        logging.basicConfig(level=logging.DEBUG)
        self.log = logging.getLogger(name="Testing")

    def put_metric_data(self, **kwargs):
        self.log.debug(kwargs)


class CW(object):
    def __init__(self, namespace, base_name, dimensions=None, test=False):
        self.namespace = namespace
        self.base_name = base_name
        self.dimensions = dimensions

        if test:
            self.client = TestClient()
        else:
            session = botocore.session.get_session()
            self.client = session.create_client('cloudwatch')

    def push(self, value, suffix):
        if suffix:
            metric_name = self.base_name + '-' + suffix
        else:
            metric_name = self.base_name

        args = {
            'NameSpace': self.namespace,
            'MetricName': metric_name,
            'Value': value,
        }
        if self.dimensions:
            args['Dimensions'] = self.dimensions
        self.client.put_metric_data(**args)


def strip_units(value):
    '''
    Strip unit characters from the end of value, leaving only the numeric data.
    '''
    while value[-1] not in '0123456789.':
        value = value[:-1]
    return value


def parse_metrics(output):
    metrics = {}
    if '|' in output:
        _, data = output.split('|', 2)

        metric_tokens = data.strip().split()
        for token in metric_tokens:
            pair = token.split(';')[0]
            key, value = pair.split('=')
            metrics[key] = strip_units(value)

    return metrics


def cli():
    usage = "%(prog)s [options] namespace base_name -- command"
    ap = ArgumentParser(usage=usage, description=__doc__)
    ap.add_argument('--dimensions', metavar='key=value,key=value',
                    help='CloudWatch metric dimensions')
    ap.add_argument('--noop', action='store_true',
                    help='Don\'t push metrics, just log')
    ap.add_argument('namespace', help='CloudWatch namespace')
    ap.add_argument('base_name', help='Base name for checks')
    ap.add_argument('command', nargs='*', help='Command (nagios check) to run')

    outp_opts = ap.add_mutually_exclusive_group()
    outp_opts.add_argument('--no-perfdata', action='store_false', default=True,
                           dest='send_perfdata', help="Don't send metrics for "
                           "performance data")
    outp_opts.add_argument('--no-status', action='store_false', default=True,
                           dest='send_status', help="Don't send the check "
                           "status output")

    args = ap.parse_args()

    result = 0
    try:
        output = check_output(args.command)
    except CalledProcessError as e:
        result = e.returncode
        output = e.output

    cw = CW(args.namespace, args.base_name, args.dimensions, args.noop)
    if args.send_status:
        cw.push(result, 'Status')
    if args.send_perfdata:
        for suffix, value in parse_metrics(output).iteritems():
            cw.push(value, suffix)

if __name__ == '__main__':
    cli()
