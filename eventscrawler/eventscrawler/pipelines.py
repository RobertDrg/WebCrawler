# Define your item pipelines here
# useful for handling different item types with a single interface
import sys
import hashlib
import mysql.connector
import json
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter
from datetime import datetime

# Different date formats used in the program
date_formats = ['%A, %B %d, %Y', '%d %B %Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S',
                '%B %d, %Y', '%d %b %Y', '%dth %B %Y', '%dth %b %Y']


# This function converts date to a standardized format
# If the input date is not in any of the predefined formats, it returns False
# If the date is in the past, it also returns False
def reformat_event_date(given_date):
    found_format = False
    if ' - ' in given_date:
        day, _, end_day, month, year = given_date.split()
        given_date = f"{day} {month} {year}"
    given_date = given_date.replace(" ET", "")
    given_date = given_date.replace(" CT", "")
    given_date = given_date.replace("\n", "")
    for date_format in date_formats:
        try:
            given_date = datetime.strptime(str(given_date), str(date_format))
            found_format = True
        except ValueError as e:
            pass
    if not found_format and given_date != "not found":
        return False

    if given_date != 'not found':
        if given_date < datetime.today():
            print('Date already passed!!')
            given_date = "passed"
            return given_date
        given_date = given_date.strftime('%Y-%m-%d')
    return given_date


def categorize_topics(topics):
    categories = {
        'Technology and Innovation': ['cloud', 'platforms', 'artificial intelligence', 'machine learning', 'robotics',
                                      'automation', 'cybersecurity', 'digital trade', 'e-health', 'computing',
                                      '#technology', 'software', 'testing', 'IT', 'it', 'technological',
                                      'Technological'
                                      ],
        'Economics and Finance': ['finance', 'banking', 'accounting', 'monetary', 'economics', 'macroeconomics',
                                  'microeconomics', 'development', 'trade', 'wealth', 'income', 'institutional',
                                  'Islamic', 'economic', 'monetary', 'financial', 'public', 'Monetary', 'inflation',
                                  'Economics'],
        'Agriculture and Food Security': ['agriculture', 'farmers', 'food security', 'climate', 'resource', 'energy',
                                          'environmental'],
        'Education and Research': ['education', 'teaching', 'research', 'phd', 'post-doc', 'interdisciplinary',
                                   'methodologies', 'scholars', 'students'],
        'Infrastructure and Engineering': ['civil engineering', 'infrastructure', 'transportation', 'water',
                                           'management', 'industrial'],
        'Social Sciences': ['employment', 'labor market', 'technologies', 'gig economy', 'gender', 'humanities',
                            'migration', 'refugees', 'governance', 'impact', 'sustainable'],
        'Conferences and Events': ['conference', 'call for papers', 'research conference', 'symposium', 'meeting'],
        'Health and Medicine': ['health', 'medicine', 'pandemic', 'medical', 'biotechnology', 'age'],
        'Politics and Geopolitics': ['politics', 'geopolitics', 'international relations', 'trade', 'China', 'Russia',
                                     'Ukraine', 'Euro area'],
        'Management and Business': ['management', 'business', 'finance', 'marketing', 'entrepreneurship',
                                    'strategic management', 'Management']
    }

    categorized = False

    if isinstance(topics, str):
        topics = [topics]

    for topic in topics:
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in topic:
                    topics = category
                    categorized = True
                    break
            if categorized:
                break

    if not categorized:
        topics = 'Other'

    return str(topics)


class MySqlPipeline:

    def __init__(self):
        self.item_hash = None
        self.already_loaded_events = set()
        self.ids_seen = set()
        self.curr = None
        self.connection = None
        self.file = open('items.jsonl', 'a', encoding='utf-8')

    # called when the spider is opened
    # creates a connection to the MySQL database using the credentials specified,
    # creates a cursor to interact with the database, and calls the create_table function
    def open_spider(self, spider):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='drg10proj10!',
                database='myevents'
            )
        except mysql.error as err:
            print(f"Error connecting to Database: {err}")
            sys.exit(1)

        self.curr = self.connection.cursor()
        self.create_table()

    # creates the events_tb table in the database if it doesn't already exist
    def create_table(self):
        self.curr.execute("""CREATE TABLE IF NOT EXISTS events_tb(
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        event_url text,
                        event_title text,
                        date_time text,
                        call_for_papers_date text,
                        location text,
                        topics text,
                        hash text
                        )""")

    # called when the spider is closed. It closes the file object, cursor, and database connection
    def close_spider(self, spider):
        self.file.close()
        self.curr.close()
        self.connection.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('event_title') == "not found":
            raise DropItem(f"Missing event title in {item}")

        if adapter.get('location') == "not found":
            raise DropItem(f"Missing event location in {item}")

        if adapter['event_title'] in self.already_loaded_events:
            raise DropItem(f"Duplicate event found: {item}")
        else:
            self.already_loaded_events.add(adapter['event_title'])

        if adapter['date_time']:
            adapter['date_time'] = reformat_event_date(adapter['date_time'])
        else:
            raise DropItem(f"Missing event date in {item}")
        if not adapter['date_time'] or adapter['date_time'] == "passed":
            raise DropItem(f"Event date passed or not found in {item}")

        if adapter['call_for_papers_date'] != "Expired":
            adapter['call_for_papers_date'] = reformat_event_date(adapter['call_for_papers_date'])

        if adapter.get('location'):
            adapter['location'] = adapter['location'].replace("\n", "")

        adapter['topics'] = categorize_topics(adapter['topics'])
        if not adapter['topics']:
            raise DropItem(f"Missing event topic in {item}")
        elif type(adapter['topics']) is list:
            adapter['topics'] = ', '.join(adapter['topics'])

        item_hash = hashlib.sha1(json.dumps(dict(item), sort_keys=True).encode('utf-8')).hexdigest()
        if item_hash in self.ids_seen:
            return item
        else:
            self.ids_seen.add(item_hash)
            self.curr.execute("SELECT id FROM events_tb WHERE hash=%s", (item_hash,))
            result = self.curr.fetchone()

            if result:
                return item
            else:
                line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
                decoded_line = line.encode('utf-8').decode('unicode-escape')
                self.file.write(decoded_line)
                self.curr.execute("""INSERT INTO events_tb (
                event_url, event_title, date_time, call_for_papers_date, location, topics, hash)
                 values (%s,%s,%s,%s,%s,%s, %s)""",
                                  (
                                      item.get('event_url'),
                                      item.get('event_title'),
                                      item.get('date_time'),
                                      item.get('call_for_papers_date'),
                                      item.get('location'),
                                      item.get('topics'),
                                      item_hash
                                  ))
                self.connection.commit()
                return item
