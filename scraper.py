from bs4 import BeautifulSoup, element
import requests
from datetime import datetime
from dateutil.parser import parse
import json

JOB_WEBSITE = 'https://studentcenter.gatech.edu/campus-jobs'
JOB_POSTING_CONTAINER_ID = 'block-views-job-postings-block-3'
JOB_POSTING_CLASS = 'views-row'

TITLE_CLASS = 'webform-component--position-title'
START_DATE_CLASS = 'webform-component--start-date'
END_DATE_CLASS = 'webform-component--end-date'
CONTACT_NAME_CLASS = 'webform-component--contact-name'
CONTACT_EMAIL_CLASS = 'webform-component--contact-email'
JOB_DESCRIPTION_CLASS = 'webform-component--job-description'
HOURS_SCHEDULE_CLASS = 'webform-component--hours-schedule'
LOCATION_CLASS = 'webform-component--location'
WORK_STUDY_CLASS = 'webform-component--work-study'
PAY_RATE_CLASS = 'webform-component--pay-rate'
POSITIONS_AVAILABLE_CLASS = 'webform-component--positions-available'


class JobPostingScraper:
    def __init__(self):
        self.jobs = []

    def getRawData(self):
        response = requests.get(JOB_WEBSITE)
        website_contents = None
        if (response.status_code == 200):
            website_contents = response.text
        else:
            raise "Error accessing website"

        return website_contents

    def getRawJobPostings(self):
        raw_data = self.getRawData()
        soup = BeautifulSoup(raw_data, 'html.parser')
        job_postings_container = soup.find(
            'div', {'id': JOB_POSTING_CONTAINER_ID})
        job_postings = job_postings_container.findAll(
            'div', {'class': JOB_POSTING_CLASS})

        return job_postings


class JobPostingParser:
    def __init__(self, raw_job_posting):
        self.raw_job_posting = raw_job_posting

    def parsePrefixSuffixComponent(self, class_name):
        raw_job_data = self.raw_job_posting.find('div', {'class': class_name})
        if raw_job_data is None:
            return None
        prefix = raw_job_data.find(
            'span', {'class': 'field-prefix'}).get_text()
        suffix = raw_job_data.find(
            'span', {'class': 'field-suffix'}).get_text()
        content = raw_job_data.contents[4]

        return f"{prefix} {content} {suffix}".strip()

    def parseBasicComponent(self, class_name):
        raw_job_data = self.raw_job_posting.find('div', {'class': class_name})
        if raw_job_data is None:
            return None
        return raw_job_data.contents[2].strip()

    def getTitle(self):
        return self.parsePrefixSuffixComponent(TITLE_CLASS)

    def getStartDate(self):
        str_date = self.parseBasicComponent(START_DATE_CLASS)
        return parse(str_date).isoformat()

    def getEndDate(self):
        str_date = self.parseBasicComponent(END_DATE_CLASS)
        return parse(str_date).isoformat()

    def getContactName(self):
        return self.parsePrefixSuffixComponent(CONTACT_NAME_CLASS)

    def getContactEmail(self):
        return self.parseBasicComponent(CONTACT_EMAIL_CLASS)

    def getDescription(self):
        raw_job_description = self.raw_job_posting.find(
            'div', {'class': JOB_DESCRIPTION_CLASS})
        return raw_job_description.find('div', {'class': 'webform-long-answer'}).get_text().strip()

    def getHoursSchedule(self):
        return self.parsePrefixSuffixComponent(HOURS_SCHEDULE_CLASS)

    def getLocation(self):
        return self.parsePrefixSuffixComponent(LOCATION_CLASS)

    def getWorkStudy(self):
        return self.parsePrefixSuffixComponent(WORK_STUDY_CLASS)

    def getPayRate(self):
        return self.parsePrefixSuffixComponent(PAY_RATE_CLASS)

    def getPositionsAvailable(self):
        return self.parsePrefixSuffixComponent(POSITIONS_AVAILABLE_CLASS)

    def getJob(self):
        return {
            'title': self.getTitle(),
            'start_date': self.getStartDate(),
            'end_date': self.getEndDate(),
            'contact_name': self.getContactName(),
            'contact_email': self.getContactEmail(),
            'description': self.getDescription(),
            'hours': self.getHoursSchedule(),
            'location': self.getLocation(),
            'work_study': self.getWorkStudy(),
            'pay_rate': self.getPayRate(),
            'positions_available': self.getPositionsAvailable(),
            'created_at': datetime.now()
        }


def main():
    scraper = JobPostingScraper()
    job_postings = scraper.getRawJobPostings()

    jobs = [JobPostingParser(x).getJob() for x in job_postings]

    #print(json.dumps(jobs, indent=4))


if __name__ == "__main__":
    main()
