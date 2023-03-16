# Jira Synthetic Data Image 

## Introduction
The aim of this project is to refresh the dev instance of Jira, replacing legacy data with synthetic data. This repo houses a Docker image which stores a script (Jira.py) to create projects and issues in Jira and populate them with comments. Any changes made to the script will trigger a pipeline to rebuild the image and store in ECR. This image is then called in the main pipeline, which is stored in [Gitlab](https://gitlab.digital.homeoffice.gov.uk/aminah.ahmed/jira_synth_refresh). This pipeline contains a drone step which will actually run the file. 

## How to Use
1. Clone repo.
2. Checkout to development branch.
3. Make changes where required.
4. Ensure requirement.txt file is updated with any new requirements.
5. Commit changes and push to development. 

## Script Walkthrough
This script runs on a blank instance in Jira. It primarily makes use of the Atlassian module for Python. The steps are as follows:
1. Establish a connection with Jira. The username and password are stored as Drone secrets in the main pipeline which is available in [Gitlab](https://gitlab.digital.homeoffice.gov.uk/aminah.ahmed/jira_synth_refresh) 
```python
def connection():
    global jira
    jira = Jira(
        url='https://jira.shs-dev.dsa-notprod.homeoffice.gov.uk',
        username=os.environ['USERNAME'],
        password=os.environ['PASSWORD'])
```
2. Generate random material - This uses a python module called essential_generators.
3. Get Project IDs - This step is necessary as when a blank instance of Jira is created, by a default project is made. This project will also need the blank instance of populating in the subsequent steps so this function adds this to the list of projects.
4. Create Projects - This function makes use of the Atlassian python module to generate projects. 
5. Create Issues - Each project is then populated with 3 tickets, this can be increased/decreased by amending line 104. The issue type and priority are randomly selected from some of the defaults available in Jira.
```python
def create_issues(issues):
    for x in range(issues):
        for i in ids[:3]:      ####<------ Change number of issues created here ####
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
```
6. Add Comments - 3 comments are added to each issue. As with step 5, the number of comments can be changed by amending line 122. Each comment is a randomly generated sentence. 
```python
def comments(no_comments):
    for i in ids[:3]:     ####<------ Change number of comments created here ####
        issues=jira.get_project_issuekey_all(i)
        for x in issues:
            for y in range(no_comments):
                jira.issue_add_comment(x, gen.sentence())
            logging.info('%s %s comments(s) created successfully. %s \n', SUCCESS, no_comments, isotime )

```
7. Run functions 


## Credits
Aminah Ahmed | Ben Gilbert | Christopher Rogers 
