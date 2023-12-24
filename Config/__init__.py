import os

from dotenv import load_dotenv
from slack_sdk import WebClient


load_dotenv()
slack_token = os.getenv('TOKEN')
slack_channel_id = os.getenv('CHANNEL_ID')
client = WebClient(token=slack_token)


class Configure:
    @classmethod
    # CINCINNATI CHILDREN'S HOSPITALS
    def convert_to_str_cch(cls, jobs) -> [str]:
        title_list = []
        for job in jobs:
            title_list.append(job.text)
        return title_list

    @classmethod
    def make_cch_object(cls, job_titles):
        pass
