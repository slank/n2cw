def strip_units(value):
    '''
    Strip unit characters from the end of value, leaving only the numeric data.
    '''
    while value[-1] not in '0123456789.':
        value = value[:-1]
    return value


def parse(output):
    metrics = {}
    if '|' in output:
        _, data = output.split('|', 2)

        metric_tokens = data.strip().split()
        for token in metric_tokens:
            pair = token.split(';')[0]
            key, value = pair.split('=')
            metrics[key] = strip_units(value)

    return metrics
