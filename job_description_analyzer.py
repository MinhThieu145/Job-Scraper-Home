import time

# libraries for S3
import boto3
import io

# the lbirary to retry and delay
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


# open ai stuff
import openai

openai.api_key='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'    
SLEEP_TIME_OPEN_AI_EACH_ROW = 1
SLEEP_TIME_WHEN_FAILED = 60
BUCKET_NAME_RESULT = 'job-description-process'
folder_name = 'indeed-scraper' # this is the folder name of the scraper in the S3 bucket


# Open AI get completion
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
def get_completion(prompt, model="gpt-3.5-turbo", temperature=0.0):
    messages = [{"role": "user", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message["content"]
    except Exception as e:
        # error code from openai
        print("Error:", str(e))
        print("Error details:", response)
        raise e

def GetSummaryPrompt(job_description):

    prompt = f'''
    Your task is to generate a short summary of the job description to suggest key \ 
    ideas to a job seeker. \

    Summarize the following job description, delimited by tripple bacticks: \
    in at most 3 sentences, and focus on key skills and requirements. \

    Job Description: ```{job_description}```

    '''

    response = get_completion(prompt)
    return response


# Extract key details from the job description
def GetKeyDetails(job_description):

    prompt = f'''
    Your task is to extract key information from a job description. 

    The job description is delimited by tripple bacticks\
    Format your response as a JSON object with the following keys listed below. \
    The description of each key is delimited by double bactick, this information is only for you to understand\
    the content of each key. Don't include it in your response. 
    - "Job Title:" ``What is the job title?``
    - "Technical Skills:" ``Skills like C++, Saleforce, AWS are considered technical skills``
    - "Other Responsibilities:" ``Skills like Business Analytics, Giving data-driven decisions are considered soft skills``
    - "General Technical SKills:" ``Grouping technical skills into a more general category, like "Cloud Computing"``
    - "Background Clearance:" `Broad knowledge of enterprise business systems, but particularly CRM, BI and BPM.
    `Does the job require a background clearance? Answer in Yes or No``
    - "Years of Experience:" ``How many years of experience are required?``
    - "Is this intern or entry position" ``Answer in Yes or No``

    Job Description: ```{job_description}```

    '''

    key_details = get_completion(prompt)
    return key_details

# Push the result to S3
def UploadDataFrameToS3(df, folder_name, file_name):
    # convert dataframe to CSV String
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # upload to S3
    s3 = boto3.client('s3')

    # folder name will also inlcude current date
    current_date = time.strftime("%Y-%m-%d", time.localtime())
    # change current date to result_date
    current_date = 'result-' + str(current_date)

    # add current date to the folder name path
    folder_name = folder_name + '/' + current_date

    # Upload the CSV string to S3 bucket
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=BUCKET_NAME_RESULT, Key=folder_name + '/' + file_name)



def main(df, df_name):

    # loop through each row
    for index, row in df.iterrows():
        # get the column called job_title
        job_title = row['job_title']

        # get the column called job_link
        job_link = row['job_link']

        # get the column called description
        job_description = row['description']

        # get the job_summary
        job_summary = GetSummaryPrompt(job_description)

        # get the key details
        key_details = GetKeyDetails(job_description)

        # add the job_summary to the dataframe
        df.loc[index, 'job_summary'] = job_summary

        # add the key_details to the dataframe
        df.loc[index, 'key_details'] = key_details

        # Upload to S3
        UploadDataFrameToS3(df=df, folder_name=folder_name, file_name=f'{df_name}.csv')





