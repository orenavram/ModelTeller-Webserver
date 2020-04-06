#!/data/shared/python/anaconda3-5.1.0/bin/python3.6

import os

# constants to use when sending e-mails using the server admin's email address.
ADMIN_EMAIL = 'evolseq@mail.tau.ac.il' #'orenavram@gmail.com' #'shiranos@gmail.com' 'evolseq@mail.tau.ac.il'
SMTP_SERVER = 'mxout.tau.ac.il'

QUEUE_NAME = 'lifesciweb'
PIPELINE_NAME = 'ModelTeller'

# general paths
SERVERS_RESULTS_DIR = '/bioseq/data/results'
SERVERS_LOGS_DIR = '/bioseq/data/logs'

WEBSERVER_NAME = 'ModelTeller'
WEBSERVER_URL = 'https://modelteller.tau.ac.il'
#MODELTELLER_LOG = '/bioseq/modelteller/MODELTELLER_runs.log'
#APACHE_ERROR_LOG = '/var/log/httpd/modelteller.error_log'

RELOAD_INTERVAL = 30
RELOAD_TAGS = f'<META HTTP-EQUIV="REFRESH" CONTENT="{RELOAD_INTERVAL}"/>'

HR_STYLE = 'style="height:1px;border:none;color:#333;background-color:#333;"'

MODELTELLER_RESULTS_DIR = os.path.join(SERVERS_RESULTS_DIR, 'modelteller')
MODELTELLER_LOGS_DIR = os.path.join(SERVERS_LOGS_DIR, 'modelteller')
MODELTELLER_RESULTS_URL = os.path.join(WEBSERVER_URL, 'results')
MODELTELLER_HTML_DIR = '/data/www/html/modelteller'
MODELTELLER_EXEC = '/groups/itay_mayrose/shiranabad/MsMl/mt_online_sklearn/'

MAIN_SCRIPT = os.path.join(MODELTELLER_EXEC, 'main.py')

RESULT_MSG = 'Unresolved error'

CONTAINER_WIDTH = 'width: 700px'
CONTAINER_STYLE = f'{CONTAINER_WIDTH}'