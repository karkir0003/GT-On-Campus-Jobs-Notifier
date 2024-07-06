import configparser
import pymongo

config = configparser.ConfigParser()
config.read('config.ini')
database_config = config['DATABASE']


class MongoDatabase:
    def __init__(self, database="test"):
        print("Establishing connection to the database")
        self.connection_string = database_config['CONNECTION_STRING']
        self.client = pymongo.MongoClient(self.connection_string)
        self.database = self.client[database]

        self.verify_connection()

    def reset_connection(self):
        self.client = pymongo.MongoClient(self.connection_string)

    def verify_connection(self):
        for _ in range(5):
            try:
                self.client.server_info()
                print("Connected to the database")
                return
            except:
                self.reset_connection()
        
        raise "Failed to connect to the database"


class JobPostingDatabase(MongoDatabase):
    def __init__(self, database="test"):
        MongoDatabase.__init__(self, database=database)

    def get_job_postings_collection(self) -> pymongo.collection:
        return self.database["job_postings"]

    def get_job_postings_by_filter(self, filter):
        return list(self.get_job_postings_collection().find(filter))

    def add_job_posting(self, job_posting):
        return self.get_job_postings_collection().insert_one(job_posting)

    def get_all_job_postings(self):
        return list(self.get_job_postings_collection().find({}))


def create_unique_job_index():
    db = JobPostingDatabase()
    indexes_fields = ["title", "start_date", "end_date", "contact_name", "contact_email",
                      "description", "hours", "location", "pay_rate", "positions_available"]
    indexes = [(x, pymongo.ASCENDING) for x in indexes_fields]
    db.get_job_postings_collection().create_index(
        indexes, name="unique_job", unique=True)


def main():
    db = JobPostingDatabase()
    print(db.get_all_job_postings())


if __name__ == "__main__":
    main()
