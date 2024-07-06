import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.parser import parse
import configparser
import groupme_bot

from email_templates.new_job_info import get_new_job_email_template
from email_templates.new_subscriber import get_new_subscriber_template

config = configparser.ConfigParser()
config.read('config.ini')
google_config = config['GOOGLE']


def get_email_content(subject, template):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = u"{}".format(subject)
    msg.attach(MIMEText(template, "html", "utf-8"))

    return msg.as_string().encode('ascii')


def send_welcome_message(email_address):
    template = get_new_subscriber_template()
    subject = "Welcome to the GT On-Campus Jobs notification service!"
    email_content = get_email_content(subject, template)
    send_email([email_address], email_content)


def send_new_job_notification(email_list, job_detail):
    start_date = parse(job_detail['start_date']).strftime("%m/%d/%Y")
    end_date = parse(job_detail['end_date']).strftime("%m/%d/%Y")

    # TODO - Add unsubscribe link for for each subscriber while generating the template
    template = get_new_job_email_template(
        job_detail["title"], start_date, end_date, job_detail["pay_rate"],
        job_detail["work_study"], job_detail["positions_available"],
        job_detail["location"], job_detail["hours"], job_detail["description"],
        job_detail["contact_name"], job_detail["contact_email"])

    subject = "GT On-Campus Jobs | Now Hiring {}".format(job_detail["title"])
    email_content = get_email_content(subject, template)

    # TODO - Investigate why the server closes when sending email to multiple users:
    # HOTFIX - Send email a subscriber at a time
    remaining_emails = email_list
    for _ in range(3):
        if len(remaining_emails) == 0:
            break

        failed_emails = []
        for receiver_email in remaining_emails:
            try:
                send_email([receiver_email], email_content)
            except Exception as e:
                failed_emails.append(receiver_email)
                print(e)

        remaining_emails = failed_emails

    if len(remaining_emails) > 0:
        groupme_bot.send_message(
            f"There were {len(remaining_emails)} exceptions while sending email")


def send_email(email_list, email_content):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"

    sender_email = "gtstudentjobs@gmail.com"
    password = google_config['EMAIL_PASSWORD']

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server) as server:
        # server.ehlo()  # Can be omitted
        # server.starttls(context=context)
        # server.ehlo()  # Can be omitted
        server.login(sender_email, password)

        server.sendmail(sender_email, email_list, email_content)


def main():
    # import bson
    # import database

    # db = database.JobPostingDatabase(database="prod")
    # test_job = db.get_job_postings_by_filter(
    #     {"_id": bson.ObjectId('600f3c1c529f71f1fc50f023')})[0]
    # print(test_job)

    # from mailchimp import OnCampusJobList
    # custom_list = OnCampusJobList().get_email_list()
    # print(len(custom_list))

    send_welcome_message("sebop97458@nonicamy.com")

    # send_new_job_notification(["hadeyaw586@laklica.com", "prettyandsimple@example.com",
    #                            "firstname.lastname@example.com", "email@subdomain.example.com", "firstname+lastname@example.com"], test_job)
    pass


if __name__ == "__main__":
    main()
