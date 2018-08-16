#!/data/shared/python/anaconda3-5.1.0/bin/python3.6

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
    <link rel="shortcut icon" type="image/x-icon" href="{CONSTS.MODELTELLER_URL}/pics/logo.gif" />

    <meta charset="utf-8">
    <!--<meta name="viewport" content="width=device-width, initial-scale=1">-->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css">

    <link rel="stylesheet" href="{CONSTS.MODELTELLER_URL}/css/general.css">
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
                        <img src="{CONSTS.MODELTELLER_URL}/pics/logo.gif" id="nav_bar_image" style="height: 120px;"><br>
                        <span id="sub-title">A machine learning tool for phylogenetic model selection</span>
                        <br><br>
                    </div>
                </div>
            </div>       
        </div>
    </nav>
    <div id="behind-nav-bar-results">
    </div>
<br><div class="container" style="width: 700px" align="justify"> 
<H1 align=center>Job Status - <FONT color='red'>RUNNING</FONT></h1>
<br>ModelTeller is now processing your request. This page will be automatically updated every {CONSTS.RELOAD_INTERVAL} seconds (until the job is done). You can also reload it manually. Once the job has finished, the output will appear below. A link to this page was sent to your email in case you wish to view these results at a later time without recalculating them. Please note that the results will be kept in the server for 3 months.
<br><br></div>''')
        f.flush()


def write_running_parameters_to_html(output_path, job_title, file_name = ''):
    with open(output_path, 'a') as f:

        # regular params row
        f.write("""<div class="container">""")

        f.write('<div class="row" style="font-size: 20px;">')
        if job_title != '':
            f.write('<div class="col-md-6">')
            f.write(f'<b>Job title: </b>{job_title}<br><br>')
            f.write('</div>')
            f.write('</div><div class="row" style="font-size: 20px;">')

        # f.write('<div class="col-md-3">')
        # f.write(f'<b>MSA: </b>{file_name if file_name else "Raw alignment"}')
        # f.write('</div>')
        f.write('</div><br>')


def write_cmds_file(cmds_file, run_number, parameters):
    # the queue does not like very long commands so I use a dummy delimiter (!@#) to break the commands for q_submitter
    new_line_delimiter = ';!@#'
    # the code contains features that are exclusive to Python3.6 (or higher)!
    required_modules = ' '.join(
        ['python/anaconda_python-3.6.4'])
    with open(cmds_file, 'w') as f:
        f.write(f'module load {required_modules}')
        f.write(new_line_delimiter)
        f.write(f'{" ".join(["python", CONSTS.MAIN_SCRIPT, parameters])}\tMT{run_number}') # MT stands for Model Teller

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

    # Send me a notification email every time there's a new request
    send_email(smtp_server=CONSTS.SMTP_SERVER, sender=CONSTS.ADMIN_EMAIL,
               receiver='shiranos@gmail.com', subject=f'MODELTELLER - A new job has been submitted: {run_number}',
               content=f"{os.path.join(CONSTS.MODELTELLER_URL, 'results', run_number, 'cgi_debug.txt')}\n{os.path.join(CONSTS.MODELTELLER_URL, 'results', run_number, 'output.html')}")

    try:
        if form['email'].value != '':
            with open(cgi_debug_path, 'a') as f:
                f.write(f"{form['email'].value.strip()}\n\n")

        with open(cgi_debug_path, 'a') as f:
            # for debugging
            f.write(f'{"#"*50}\n{ctime()}: A new CGI request has been recieved!\n')
            sorted_form_keys = sorted(form.keys())
            f.write(f'These are the keys that the CGI received:\n{"; ".join(sorted_form_keys)}\n\n')
            f.write('Form values are:\n')
            for key in sorted_form_keys:
                if 'alignment' not in key:
                    f.write(f'{key} = {form[key]}\n')
            for key in sorted_form_keys:
                if 'alignment' in key:
                    f.write(f'100 first characters of {key} = {form[key].value[:100]}\n')
            f.write('\n\n')

        # extract form's values:
        user_email = form['email'].value.strip()

        job_title = ''
        if form['job_title'].value != '':
            job_title = form['job_title'].value.strip()

        # This is hidden field that only spammer bots might fill in...
        confirm_email_add = form['confirm_email'].value  # if it is contain a value it is a spammer.

        msa_path = os.path.join(wd, 'data.fas')
        if 'alignment_str' in form:
            with open(cgi_debug_path, 'a') as f:
                f.write(f'{"#"*80}\nmsa is raw\n')
            with open(msa_path, 'w') as f:
                f.write(form['alignment_str'].value)
        else:
            with open(cgi_debug_path, 'a') as f:
                f.write(f'{"#"*80}\nuploading msa file\n')

            filename = form['alignment_file'].filename
            with open(cgi_debug_path, 'a') as f:
                f.write(f'file name is:\n{filename}')# (of type {type(form[run + "_R1"].value)}) and {run_R2_filename} (of type {type(form[run + "_R2"].value)})\n')

            msa = form['alignment_file'].value
            with open(cgi_debug_path, 'a') as f:
                f.write(f'{filename} first 100 chars are: {msa[:100]}\n')

            with open(msa_path, 'wb') as f:
                f.write(msa)

        with open(cgi_debug_path, 'a') as f:
            f.write(f'msa was saved to disk successfully\n')

        parameters = f'-m {msa_path} -j {run_number}'

        cmds_file = os.path.join(wd, 'qsub.cmds')
        write_cmds_file(cmds_file, run_number, parameters)

        log_file = cmds_file.replace('cmds', 'log')
        # complex command with more than one operation (module load + python q_submitter.py)
        # submission_cmd = 'ssh bioseq@lecs2login "module load python/anaconda_python-3.6.4; python /bioseq/bioSequence_scripts_and_constants/q_submitter.py {} {} -q {} --verbose > {}"'.format(cmds_file, wd, queue_name, log_file)

        # simple command when using shebang header
        submission_cmd = f'ssh bioseq@lecs2login /bioseq/bioSequence_scripts_and_constants/q_submitter.py {cmds_file} {wd} -q bioseq --verbose > {log_file}'

        write_to_debug_file(cgi_debug_path, f'\nSSHing and SUBMITting the JOB to the QUEUE:\n{submission_cmd}\n')

        subprocess.call(submission_cmd, shell=True)

        if user_email != '':
            with open(os.path.join(wd, 'user_email.txt'), 'w') as f:
                f.write(f'{user_email}\n')

        write_to_debug_file(cgi_debug_path, f'\n\n{"#"*50}\nCGI finished running!\n{"#"*50}\n')

    except Exception as e:
        msg = 'CGI crashed before the job was submitted :('
        with open(output_path) as f:
            html_content = f.read()
        html_content = html_content.replace('RUNNING', 'FAILED')
        html_content += f'<br><br><br><center><h2><font color="red">{msg}</font><br><br>Please try to re-run your job or <a href="mailto:{CONSTS.ADMIN_EMAIL}?subject={CONSTS.PIPELINE_NAME}%20Run%20Number%20{run_number}">contact us</a> for further information</h2></center><br><br>\n</body>\n</html>\n'
        with open(output_path, 'w') as f:
            html_content = f.write(html_content)

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
            html_content = f.write(html_content)

if __name__ == '__main__':
    run_cgi()