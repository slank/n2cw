import botocore.session
import urllib2


AWS_MD_AZ_URL = 'http://169.254.169.254/latest/meta-data/placement/availability-zone'


def detect_region():
    try:
        return urllib2.urlopen(AWS_MD_AZ_URL, timeout=1).read()[:-1]
    except urllib2.URLError:
        return None


def cloudwatch_client(profile=None, region=None):
    if region is None:
        region = detect_region()
    session = botocore.session.get_session()
    session.set_config_variable('region', region)
    if profile:
        session.set_config_variable('profile', profile)
    return session.create_client('cloudwatch')


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
        self.dimensions = []
        for k, v in dimensions.iteritems():
            self.dimensions.append({'Name': k, 'Value': v})
        self.data = []

        if test:
            self.client = TestClient()
        else:
            self.client = cloudwatch_client()

    def add(self, suffix, value):
        try:
            value = int(value)
        except ValueError:
            value = float(value)

        if suffix:
            metric_name = self.base_name + '-' + suffix
        else:
            metric_name = self.base_name

        self.data.append({
            'MetricName': metric_name,
            'Value': value,
            'Dimensions': self.dimensions,
        })

    def push(self):
        args = {
            'Namespace': self.namespace,
            'MetricData': self.data,
        }
        self.client.put_metric_data(**args)
