#!/groups/pupko/modules/python-anaconda3.6.5/bin/python

import os
import sys
import cgi
import cgitb
import subprocess
from time import time, ctime
from random import randint

import MODELTELLER_CONSTANTS as CONSTS
if os.path.exists('/bioseq/modelteller'): #remote run
    sys.path.append('/bioseq/modelteller/auxiliaries/')
    sys.path.append('/bioseq/bioSequence_scripts_and_constants/')

from directory_creator import create_dir # from /bioseq/modelteller/auxiliaries/
from email_sender import send_email # from /bioseq/bioSequence_scripts_and_constants/

def print_hello_world(output_path = '', run_number = 'NO_RUN_NUMBER'):

    hello_world_html = """
<html>
    <body>
        <h2>Hello World! """ + run_number + """</h2>
    </body>
</html>
    """
    if not output_path:
        print(hello_world_html)
    else:
        with open(output_path, 'w') as f:
            f.write(hello_world_html)

def write_to_debug_file(cgi_debug_path, content):
    with open(cgi_debug_path, 'a') as f:
        f.write(f'{ctime()}: {content}\n')

def write_html_prefix(output_path, run_number):
    with open(output_path, 'w') as f:
        f.write(f'''<html><head>

    <meta http-equiv="cache-control" content="no-cache, must-revalidate, post-check=0, pre-check=0" />
    <meta http-equiv="cache-control" content="max-age=0" />
    <meta http-equiv="expires" content="0" />
    <meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
    <meta http-equiv="pragma" content="no-cache" />
    {CONSTS.RELOAD_TAGS}

    <title>ModelTeller Job #{run_number}</title>
    <link rel="shortcut icon" type="image/x-icon" href="{CONSTS.WEBSERVER_URL}/pics/logo.gif" />

    <meta charset="utf-8">
    <!--<meta name="viewport" content="width=device-width, initial-scale=1">-->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css">

    <link rel="stylesheet" href="{CONSTS.WEBSERVER_URL}/css/general.css">
    <link rel="stylesheet" href="../webpage/css/general.css">

    </head><body>
    <nav role="navigation" class="navbar navbar-fixed-top">
        <div class="jumbotron" id="jumbo">
            <div class="container">            
                <div class="row" id="title-row" align="center">
                    <div class="col-md-1">
                    </div>
                    <div class="col-md-10" align="center">
                        <span id="server-title">ModelTeller</span><br>
                        <img src="{CONSTS.WEBSERVER_URL}/pics/logo.gif" id="nav_bar_image" style="height: 120px;"><br>
                        <span id="sub-title">A machine learning tool for phylogenetic model selection</span>
                        <br><br>
                    </div>
                </div>
            </div>       
        </div>
    </nav>
    <div id="behind-nav-bar-results">
    </div>
<br><div class="container" style="{CONSTS.CONTAINER_STYLE}" align="justify"> 
<H1 align=center>Job Status - <FONT color='red'>RUNNING</FONT></h1>
<br>ModelTeller is now processing your request. This page will be automatically updated every {CONSTS.RELOAD_INTERVAL} seconds (until the job is done). You can also reload it manually. Once the job has finished, the output will appear below. A link to this page was sent to your email in case you wish to view these results at a later time without recalculating them. Please note that the results will be kept in the server for 3 months.
<br><br></div>''')
        f.flush()


def upload_file(form, form_key_name, file_path, cgi_debug_path):
    write_to_debug_file(cgi_debug_path, f'{"#"*80}\nuploading file\n')
    filename = form[form_key_name].filename
    write_to_debug_file(cgi_debug_path, f'file name is:\n{filename}\n')
    content = form[form_key_name].value
    write_to_debug_file(cgi_debug_path, f'{filename} first 100 chars are: {content[:100]}\n')
    with open(file_path, 'wb') as f:
        f.write(content)


def write_running_parameters_to_html(output_path, job_title, msa_name, running_mode, features_contributions_as_text):
    with open(output_path, 'a') as f:

        # regular params row
        f.write(f"""<div class="container" style="{CONSTS.CONTAINER_STYLE}" align="justify">""")

        if job_title != '':
            f.write('<div class="row" style="font-size: 20px;">')
            f.write('<div class="col-md-12">')
            f.write(f'<b>Job title: </b>{job_title}')
            f.write('</div></div>')

        f.write('<div class="row" style="font-size: 20px;">')
        f.write('<div class="col-md-12">')
        f.write(f'<b>Alignment: </b>{msa_name}')
        f.write('</div></div>')

        f.write('<div class="row" style="font-size: 20px;">')
        f.write('<div class="col-md-12">')
        f.write(f'<b>Running mode: </b>{running_mode}')
        f.write('</div></div>')

        f.write('<div class="row" style="font-size: 20px;">')
        f.write('<div class="col-md-12">')
        f.write(f'<b>Compute features contributions: </b>{features_contributions_as_text}')
        f.write('</div></div>')

        f.write('</div><br>')


def write_cmds_file(cmds_file, run_number, parameters):
    # the queue does not like very long commands so I use a dummy delimiter (!@#) to break the commands for q_submitter
    new_line_delimiter = ';!@#'
    # the code contains features that are exclusive to Python3.6 (or higher)!
    required_modules = ' '.join(['python/python-anaconda3.2019.3'])
    with open(cmds_file, 'w') as f:
        f.write(f'module load {required_modules}')
        f.write(new_line_delimiter)
        f.write(f'{" ".join(["python", CONSTS.MAIN_SCRIPT, parameters])}\tmodelteller{run_number}\n') # MT stands for Model Teller

def run_cgi():

    # prints detailed error report on BROWSER when backend crashes
    # This line MUST appear (as is) BEFORE any error occurs to get a report about the exception!! otherwise you'll get a non-informatvie message like "internal server error"
    cgitb.enable()

    # print_hello_world() # for debugging
    form = cgi.FieldStorage()  # extract POSTed object

    # random_chars = "".join(choice(string.ascii_letters + string.digits) for x in range(20))
    run_number = str(round(time())) + str(randint(10 ** 19, 10 ** 20 - 1))  # adding 20 random digits to prevent users see data that are not their's
    if False:
        run_number = 'debug'  # str(round(time())) + str(randint(1000,9999)) # adding 4 random figures to prevent users see data that are not their's

    results_url = os.path.join(CONSTS.MODELTELLER_RESULTS_URL, run_number)
    output_url = os.path.join(results_url, 'output.html')

    wd = os.path.join(CONSTS.MODELTELLER_RESULTS_DIR, run_number)
    create_dir(wd)
    output_path = os.path.join(wd, 'output.html')
    cgi_debug_path = os.path.join(wd, 'cgi_debug.txt')
    #print('Content-Type: text/html\n')  # For more details see https://www.w3.org/International/articles/http-charset/index#scripting
    # print_hello_world(wd+'/test.txt') # comment out for debugging
    # print_hello_world(output_html_path, run_number) # comment out for debugging

    write_html_prefix(output_path, run_number)  # html's prefix must be written BEFORE redirecting...

    print(f'Location: {output_url}')  # Redirects to the results url. MUST appear before any other print.
    print('Content-Type: text/html\n')  # For more details see https://www.w3.org/International/articles/http-charset/index#scripting
    sys.stdout.flush()  # must be flushed immediately!!!

    # email field should ALWAYS exist in the form (even if it's empty!!)
    # if it's not there, someone sent a request not via the website so they should be blocked.
    # confirm_email is hidden field that only spammer bots might fill in...
    if 'email' not in form or ('confirm_email' in form and form['confirm_email'].value != ''):
        exit()

    # uncomment to send the admin a notification email EVERY time there's a new request
    send_email(smtp_server=CONSTS.SMTP_SERVER, sender=CONSTS.ADMIN_EMAIL,
               receiver='orenavram@gmail.com', subject=f'ModelTeller - A new job has been submitted: {run_number}',
               content=f"{os.path.join(CONSTS.WEBSERVER_URL, 'results', run_number, 'cgi_debug.txt')}\n{os.path.join(CONSTS.WEBSERVER_URL, 'results', run_number, 'output.html')}")

    try:
        if form['email'].value != '':
            write_to_debug_file(cgi_debug_path, f"{form['email'].value.strip()}\n\n")

        with open(cgi_debug_path, 'a') as f:
            # for debugging
            f.write(f'{"#"*50}\n{ctime()}: A new CGI request has been recieved!\n')
            sorted_form_keys = sorted(form.keys())
            f.write(f'These are the keys that the CGI received:\n{"; ".join(sorted_form_keys)}\n\n')
            f.write('Form values are:\n')
            for key in sorted_form_keys:
                if 'alignment' in key or 'topology' in key:
                    # avoid writing the whole file
                    f.write(f'100 first characters of {key} = {form[key].value[:100]}\n')
                else:
                    f.write(f'{key} = {form[key]}\n')
            f.write('\n\n')

        # extract form's values:
        user_email = form['email'].value.strip()

        job_title = ''
        if form['job_title'].value != '':
            job_title = form['job_title'].value.strip()

        features_contributions = 0
        if 'features_contributions' in form:
            # form['features_contributions'].value.strip() == '
            features_contributions = 1
        features_contributions_as_text = "Yes" * features_contributions + "No" * (1 - features_contributions)

        # This is hidden field that only spammer bots might fill in...
        confirm_email_add = form['confirm_email'].value  # if it is contain a value it is a spammer.

        msa_path = os.path.join(wd, 'data.fas')
        if 'alignment_str' in form:
            write_to_debug_file(cgi_debug_path, f'{"#"*80}\nmsa is raw\n')
            with open(msa_path, 'w') as f:
                f.write(form['alignment_str'].value)
        else:
            upload_file(form, 'alignment_file', msa_path, cgi_debug_path)

        write_to_debug_file(cgi_debug_path, f'msa was saved to disk successfully\n\n')

        running_mode_code = form['running_mode'].value
        if running_mode_code == '2':
            user_defined_topology_path = os.path.join(wd, 'user_defined_topology.txt')
            upload_file(form, 'user_defined_topology', user_defined_topology_path, cgi_debug_path)
            running_mode_code += f' -u {user_defined_topology_path}'


        # human readable parameters for results page and confirmation email
        msa_name = 'Raw text' if 'alignment_str' in form else form['alignment_file'].filename
        user_defined_topology = form['user_defined_topology'].filename if running_mode_code.startswith('2') else ''
        if running_mode_code == '0':
            running_mode = 'Select the best model for branch-lengths estimation'
        elif running_mode_code == '1':
            running_mode = 'Use a fixed GTR+I+G topology (this may take a little longer because ModelTeller first computes the maximum-likelihood phylogeny according to the GTR+I+G model, but, once a model is predicted, computation of the resulting phylogeny will be rapid)'
        else:
            running_mode = f'User defined topology (with {user_defined_topology})'

        write_running_parameters_to_html(output_path, job_title, msa_name, running_mode, features_contributions_as_text)
        write_to_debug_file(cgi_debug_path, f'{ctime()}: Running parameters were written to html successfully.\n')


        parameters = f'-m {msa_path} -j {run_number} -p {running_mode_code} -f {features_contributions}'

        cmds_file = os.path.join(wd, 'qsub.cmds')
        write_cmds_file(cmds_file, run_number, parameters)

        log_file = cmds_file.replace('cmds', 'log')
        # complex command with more than one operation (module load + python q_submitter.py)
        # submission_cmd = 'ssh bioseq@powerlogin "module load python/anaconda_python-3.6.4; /bioseq/bioSequence_scripts_and_constants/q_submitter_power.py {cmds_file} {wd} -q {CONSTS.QUEUE_NAME} --verbose > {log_file}"'

        # simple command when using shebang header
        submission_cmd = f'ssh bioseq@powerlogin /bioseq/bioSequence_scripts_and_constants/q_submitter_power.py {cmds_file} {wd} -q {CONSTS.QUEUE_NAME} --verbose > {log_file}'

        write_to_debug_file(cgi_debug_path, f'\nSSHing and SUBMITting the JOB to the QUEUE:\n{submission_cmd}\n')

        subprocess.call(submission_cmd, shell=True)

        if user_email != '':
            with open(os.path.join(wd, 'user_email.txt'), 'w') as f_email:
                f_email.write(f'{user_email}\n')

            notification_content = f"Your submission configuration is:\n\n"
            if job_title:
                notification_content += f'Job title: {job_title}\n'
            notification_content += f'Alignment: {msa_name}\n' \
                                    f'Running mode: {running_mode}\n' \
                                    f'Compute features contributions: {features_contributions_as_text}\n' \
                                    f'Once the analysis will be ready, we will let you know! ' \
                                    f'Meanwhile, you can track the progress of your job at:\n{os.path.join(CONSTS.WEBSERVER_URL, "results", run_number, "output.html")}\n\n'

            # Send the user a notification email for their submission
            send_email(smtp_server=CONSTS.SMTP_SERVER,
                       sender=CONSTS.ADMIN_EMAIL,
                       receiver=f'{user_email}',
                       subject=f'{CONSTS.WEBSERVER_NAME} - Your job has been submitted!{" (Job name: "+str(job_title) if job_title else ""})',
                       content=notification_content)

        write_to_debug_file(cgi_debug_path, f'\n\n{"#"*50}\nCGI finished running!\n{"#"*50}\n')

    except Exception as e:
        msg = 'CGI crashed before the job was submitted :('
        with open(output_path) as f:
            html_content = f.read()
        html_content = html_content.replace('RUNNING', 'FAILED')
        html_content += f'<br><br><br><center><h2><font color="red">{msg}</font><br><br>Please try to re-run your job or <a href="mailto:{CONSTS.ADMIN_EMAIL}?subject={CONSTS.PIPELINE_NAME}%20Run%20Number%20{run_number}">contact us</a> for further information</h2></center><br><br>\n</body>\n</html>\n'
        with open(output_path, 'w') as f:
            f.write(html_content)

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        write_to_debug_file(cgi_debug_path, f'\n{"$"*50}\n\n{msg}\n\n{fname}: {exc_type}, at line: {exc_tb.tb_lineno}\n\n{"$"*60}')

        # logger.info(f'Waiting {2*CONSTS.RELOAD_INTERVAL} seconds to remove html refreshing headers...')
        # Must be after flushing all previous data. Otherwise it might refresh during the writing.. :(
        from time import sleep

        sleep(2 * CONSTS.RELOAD_INTERVAL)
        with open(output_path) as f:
            html_content = f.read()
        html_content = html_content.replace(CONSTS.RELOAD_TAGS, '')
        with open(output_path, 'w') as f:
            f.write(html_content)

if __name__ == '__main__':
    run_cgi()