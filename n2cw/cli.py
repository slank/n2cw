#!/usr/bin/env python
'''
A wrapper for nagios-style checks that pushes check status and
perfdata to CloudWatch metrics.
'''
import sys
from argparse import (
    ArgumentParser,
    Action,
)
from subprocess import (
    check_output,
    CalledProcessError,
)
from . import (
    aws,
    metrics,
)


class ParseKv(Action):
    '''Parse key-value pairs from a string in the form key=value,key=value'''
    def __call__(self, parser, namespace, values, option_string=None):
        kv = getattr(namespace, self.dest, {})
        kv.update(dict(p.split('=') for p in values.split(',')))
        setattr(namespace, self.dest, kv)


def cli(args=sys.argv[:]):
    usage = "%(prog)s [options] namespace base_name -- command"
    ap = ArgumentParser(usage=usage, description=__doc__)
    ap.add_argument('--dimensions', metavar='key=value,key=value', default={},
                    action=ParseKv, help='CloudWatch metric dimensions')
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

    cw = aws.CW(args.namespace, args.base_name, args.dimensions, args.noop)
    if args.send_status:
        cw.add('Status', result)
    if args.send_perfdata:
        for suffix, value in metrics.parse(output).iteritems():
            cw.add(suffix, value)

    cw.push()

if __name__ == '__main__':
    cli()
