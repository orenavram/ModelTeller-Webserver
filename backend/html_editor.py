import logging
import os
import sys

logger = logging.getLogger('main')

import MODELTELLER_CONSTANTS as CONSTS
if os.path.exists('/bioseq/modelteller'): #remote run
    sys.path.append('/bioseq/bioSequence_scripts_and_constants/')

def edit_success_html(results_path, output_html_path, header, i):
    with open(output_html_path) as f:
        html_text = f.read()

    html_text = html_text.replace('RUNNING', 'FINISHED')
    html_text = html_text.replace(f'ModelTeller is now processing your request. This page will be automatically updated every 30 seconds (until the job is done). You can also reload it manually. Once the job has finished, the output will appear below. ', '')
    html_text = html_text.replace(f' (this may take a little longer because ModelTeller first computes the maximum-likelihood phylogeny according to the GTR+I+G model, but, once a model is predicted, computation of the resulting phylogeny will be rapid)', '')

    results = []
    with open(results_path) as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(line)

    html_text += f'''
    <div class="container" style="width: 700px">

    </div>
    <div class="container" align="center" style="width: 700px">
        <table class="table" style="font-size: 20px;">
            <thead>
                <tr>
                    <h2>
                        {header}:\n<br><br>\n
                        <font color="red">{results[0]}</font>
                    <!--final_tree_path {i}-->
                    <br><br>The maximum-likelihood tree for your input data using the above model is now being computed...
                    <!--features_contributions-->
                    </h2>
                    <br>
                    <h4>
                        The alternative models are (ranked from second best to worst): 
                    </h4>
                </tr>
            </thead>
            <tbody>'''

    if len(results) > 1:
        for i in range(1, len(results)):  # skip first because best model was already reported
            html_text += f'''<tr>
        <td align="center">{i+1}</td>
        <td align="center">{results[i].strip()}</td>\n</tr>'''

    html_text += '</tbody></table></div>'
    html_text += f'<hr {CONSTS.HR_STYLE}>\n'
    # html_text += '<div id="bottom_links" align="center"><span class="bottom_link"><a href="' + server_main_url + '" target="_blank">Home</a>&nbsp;|&nbsp<a href="' + server_main_url + 'overview.html" target="_blank">Overview</a>\n</span>\n<br>\n</div>\n</body>\n</html>\n'


    with open(output_html_path, 'w') as f:
        f.write(html_text)
        f.flush()



def edit_failure_html(output_html_path, run_number, msg):
    with open(output_html_path) as f:
        html_text = f.read()

    html_text = html_text.replace('RUNNING', 'FAILED')
    html_text = html_text.replace(f'ModelTeller is now processing your request. This page will be automatically updated every 30 seconds (until the job is done). You can also reload it manually. Once the job has finished, the output will appear below. ', '')
    html_text = html_text.replace(f'{CONSTS.ADMIN_EMAIL} is now processing your request. This page will be automatically updated every {CONSTS.RELOAD_INTERVAL} seconds (until the job is done). You can also reload it manually. Once the job has finished, several links to the output files will appear below. ','')
    html_text +='<br><br><br>'
    html_text +='<center><h2>'
    html_text +=f'<font color="red">{msg}</font><br><br>'
    html_text +=f'Please try to re-run your job or <a href="mailto:{CONSTS.ADMIN_EMAIL}?subject={CONSTS.PIPELINE_NAME}%20Run%20Number%20{run_number}">contact us</a> for further information'
    html_text +='</h2></center>'
    with open(output_html_path, 'w') as f:
        f.write(html_text)
        f.flush()


def post_html_editing(output_html_path):

    # e.g, /bioseq/data/results/modelteller/157457949814305833525824301409/output.html
    run_number = output_html_path.split('/')[5]

    # appending end of html
    with open(output_html_path, 'a') as f:
        f.write(f'<br>\n<h4 class=footer><p align=\'center\'>Questions and comments are welcome! Please <span class="admin_link"><a href="mailto:{CONSTS.ADMIN_EMAIL}?subject={CONSTS.PIPELINE_NAME}%20Run%20Number%20{run_number}">contact us</a></span></p></h4>\n<br>\n')
        f.write('<br><br>\n</body>\n</html>\n')

    from time import sleep
    logger.info(f'Waiting {2*CONSTS.RELOAD_INTERVAL} seconds to remove html refreshing headers...')
    # Must be after flushing all previous data. Otherwise it might refresh during the writing.. :(
    sleep(2)# * CONSTS.RELOAD_INTERVAL)
    with open(output_html_path) as f:
        html_content = f.read()
    html_content = html_content.replace(CONSTS.RELOAD_TAGS, '')
    with open(output_html_path, 'w') as f:
        f.write(html_content)


def edit_results_html(status_ok, results_paths, output_html_path, run_number='NO_RUN_NUMBER', msg=''):
    if results_paths == []:
        status_ok = False
    if not status_ok:
        edit_failure_html(output_html_path, run_number, CONSTS.RESULT_MSG if not msg else msg)
    elif not os.path.exists(results_paths[0]): # sanity check that the first path exists
        edit_failure_html(output_html_path, run_number, f'Results path does not exists!!\n{results_paths[0]}')
    else:
        if len(results_paths) == 1:
            edit_success_html(results_paths[0], output_html_path, 'Best model for your alignment is', 0)
        else:
            for i in range(len(results_paths)):
                edit_success_html(results_paths[i], output_html_path, f'Best model for alignment number {i+1} is', i)
    # post_html_editing(output_html_path)


def show_final_tree_in_html(tree_path, output_html_path, i=0):
    with open(output_html_path) as f:
        html_text = f.read()

    # e.g, /bioseq/data/results/modelteller/157457949814305833525824301409/final_tree.txt
    run_number, final_tree_name = tree_path.split('/')[5:7]

    html_text = html_text.replace(f'<!--final_tree_path {i}-->',
            f'<br><br>'
            f'Click '
            f'<a href="{CONSTS.MODELTELLER_RESULTS_URL}/{run_number}/{final_tree_name}" target="_blank">here</a> '
            f'for its corresponding ML tree')
    html_text = html_text.replace('<br><br>The maximum-likelihood tree for your input data using the above model is now being computed...', '')
    with open(output_html_path, 'w') as f:
        f.write(html_text)


def show_features_contribution_in_html(features_contributions_path, output_html_path):
    with open(output_html_path) as f:
        html_text = f.read()

    # e.g, /bioseq/data/results/modelteller/157457949814305833525824301409/feature_contribution.csv
    run_number, features_contributions_file_name = features_contributions_path.split('/')[5:7]

    html_text = html_text.replace('<!--features_contributions-->',
            f'<br><br>'
            f'Click '
            f'<a href="{CONSTS.MODELTELLER_RESULTS_URL}/{run_number}/{features_contributions_file_name}" target="_blank">here</a> '
            f'for the models features contributions')
    with open(output_html_path, 'w') as f:
        f.write(html_text)



def notify_by_email(addressee, status_ok, output_html_path, msg=''):
    from email_sender import send_email  # from /bioseq/bioSequence_scripts_and_constants/
    if not msg:
        msg = f"{CONSTS.PIPELINE_NAME} pipeline {'FINISHED' if status_ok else 'FAILED'}. Results can be found at {output_html_path}."
    logger.info(msg)
    send_email(CONSTS.SMTP_SERVER, CONSTS.ADMIN_EMAIL, addressee,
               subject=f"{CONSTS.PIPELINE_NAME} {'FINISHED' if status_ok else 'FAILED'}", content=msg)

if __name__ == '__main__':
    from modelteller_cgi import write_html_prefix
    output_html_path = 'output.html'
    print(os.getcwd())
    write_html_prefix(output_html_path, 'debug')
    edit_results_html(True, [], output_html_path, 'test', 'Job failed :(')
