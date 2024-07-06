import sqlite3
from scraper import JobPostingScraper, JobPostingParser
from database import JobPostingDatabase
from pymongo import errors


DATABASE_COLUMNS = ["job_title", "start_date", "end_date", "contact_name", "contact_email",
                    "description", "hours", "location", "work_study", "pay_rate", "positions_available"]

# Populate the database with default values for the first time


def seed_database(database="test"):
    scraper = JobPostingScraper()
    job_postings = scraper.getRawJobPostings()

    jobs = [JobPostingParser(x).getJob() for x in job_postings]

    db = JobPostingDatabase(database=database)    
    for job in jobs:
        db.add_job_posting(job)

"""
Is there a new job?
"""

def populate_new_jobs(database="test"):
    db = JobPostingDatabase(database=database)

    # scrape for current data
    scraper = JobPostingScraper()
    job_postings = scraper.getRawJobPostings()

    jobs = [JobPostingParser(x).getJob() for x in job_postings]
    new_jobs = []

    for job in jobs:
        try:
            db.add_job_posting(job)
            new_jobs.append(job)
        # Because of unique index, duplicate jobs will throw DuplicateKeyError
        except errors.DuplicateKeyError as e:
            # Found a duplicate job, ignore this job
            continue
        except Exception as e:
            print(e)

    return new_jobs


def main():
    seed_database(database="prod")  # happen only once. NEVER RUN THIS LINE!
    # new_jobs = populate_new_jobs()
    # print(new_jobs)


if __name__ == "__main__":
    main()
