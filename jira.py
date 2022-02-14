from atlassian import Jira
from essential_generators import DocumentGenerator
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
from datetime import datetime
import re
import time 
from random_word import RandomWords
import os 
import random


isotime = datetime.now().isoformat('T', 'seconds')

CRITICAL="\U0001F198" #logging.critical
ERROR="\U00002757"    #logging.error
WARNING="\U000026A0"  #logging.warning
INFO="\U00002139"     #logging.debug
SUCCESS="\U00002705"  #logging.info

logging.basicConfig(format='%(message)s', level=logging.INFO)

# Establish a connrection with Jira
def connection():
    global jira
    jira = Jira(
        url='https://jira.shs-dev.dsa-notprod.homeoffice.gov.uk',
        username=os.environ['USERNAME'],
        password=os.environ['PASSWORD'])

# Generates random material 
def generator():
    global gen
    gen = DocumentGenerator()

# Get project ids 
def project_ids():
    mylist=jira.projects(included_archived=None)
    global ids
    ids=[]
    for i in mylist:
        for key, value in i.items():
            if key=='key':
                ids.append(value)

    return ids

# Create projects 
def create_projects(projects):
    url = 'https://jira.shs-dev.dsa-notprod.homeoffice.gov.uk/rest/api/2/project'
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
        
    for i in range(projects):
        r=RandomWords()
        project_name=r.get_random_word(hasDictionaryDef="true",minLength=5, maxLength=12)
        project_key=project_name[:4].upper()
    

        if project_name.isascii()==False or (project_key in ids):
            project_name=r.get_random_word(hasDictionaryDef="true",minLength=5, maxLength=12)
            project_key = project_name[:4].upper()

        payload = json.dumps( {
            "key": project_key,
            "name": project_name,
            "projectTypeKey": "software",
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-kanban-template",
            "description": "Example Project description",
            "lead": "admin",
            # "avatarId": 10200
            "avatarId": random.choice([10011,10200,10324,10318])
        } )

        response = requests.request(
        "POST",
        url,
        auth=HTTPBasicAuth('admin', 'admin'),
        data=payload,
        headers=headers
        )

        # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

        stat=str(response.status_code)
        if re.search('20.',stat):
            logging.info('%s Space created successfully \n Name:%s Key:%s %s \n', SUCCESS, project_name, project_key, isotime )
        elif re.search('40.',stat):
            logging.error('%s Failed to create space - Invalid key \n Name:%s Key:%s %s \n', ERROR, project_name, project_key, isotime)            
        elif re.search('50.',stat):
            logging.critical('%s Failed to create space - Site not available \n Name:%s Key:%s %s \n', CRITICAL, project_name, project_key, isotime) 
            time.sleep(5)
        else:
            logging.critical('%s Failed to create space \n Name:%s Key:%s %s \n', CRITICAL, project_name, project_key, isotime )


## Create issues  
def create_issues(issues):
    for x in range(issues):
        for i in ids[:3]:
            try:
                jira.issue_create(
                    fields={
                        "project": {"key": i},
                        "issuetype": {"name": random.choice(['Bug','Story','Task'])},
                        "summary": gen.sentence(),
                        "description": gen.paragraph(),
                        "priority": {"name": random.choice(['Low','Lowest','Medium','High','Highest'])}
                    }
                )
                logging.info('%s Issue(s) created successfully. %s \n', SUCCESS, isotime )
            except:
                logging.error('%s Cannot create issues(s). %s \n', ERROR, isotime )


# Add comments to issues 
def comments(no_comments):
    for i in ids[:3]:
        issues=jira.get_project_issuekey_all(i)
        for x in issues:
            for y in range(no_comments):
                jira.issue_add_comment(x, gen.sentence())
            logging.info('%s %s comments(s) created successfully. %s \n', SUCCESS, no_comments, isotime )


# Functions:
connection()
generator()
project_ids()
try:
    create_projects(projects = int(os.environ['PROJECTS']))
except:
    logging.raiseExceptions
project_ids()
create_issues(issues = int(os.environ['ISSUES']))
comments(projects = int(os.environ['COMMENTS']))

