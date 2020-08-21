import sys
import re
import logging
import argparse
import requests

from getpass import getpass
from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vText
from datetime import datetime

WEEKDATES = ['Mandag', 'Tirsdag', 'Onsdag',
             'Torsdag', 'Fredag', 'Lørdag', 'Søndag']

STANDARD_OUTPUT_FILE_NAME = 'skema.ics'

GET_URL = 'https://timetable.scitech.au.dk/apps/skema/VaelgElevskema.asp?webnavn=skema&sprog=da'
POST_URL = 'https://timetable.scitech.au.dk/apps/skema/ElevSkema.asp'


def fix_spacing(string):
    return re.sub(r'\s+', ' ', string).strip()


def get_local_html(file_name):
    if not re.match(r'.*\.html\b', file_name.lower()):
        msg = ' The input filename should end with the .html extension'
        logging.warning(msg)
        sys.exit(-1)

    try:
        with open(file_name, 'rb') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except FileNotFoundError:
        logging.warning(f' {file_name} does not exist')
        sys.exit(-1)
    return soup


def retrieve_html():
    while True:
        au_id = input("What is your auID? ")
        password = getpass()

        body = {
            'ID': au_id,
            'password': password
        }

        session = requests.session()
        session.get(GET_URL)
        logging.info("  Logging into AUs server")
        html = session.post(POST_URL, body).text
        session.close()

        if "Ugyldigt" in html:
            logging.info("  Failed logging in")
            print("Wrong auID or password")
            prompt = "Try again? [Y/n] "
            if input(prompt).lower().strip == 'n':
                sys.exit(-1)
            else:
                continue

        logging.info("  Successfully retrieved skema info")
        return BeautifulSoup(html, 'html.parser')


def html_to_json(soup):
    courses_dict = {}
    courses = soup.find_all('h3')
    for i, course in enumerate(soup.find_all('h3')):
        activities = course.find_next_siblings("strong")
        course_dict = {}
        if i != len(courses)-1:
            cut = len(activities) - \
                  len(courses[i+1].find_next_siblings("strong"))
            activities = activities[:cut]

        for activity in activities:
            activity_list = []
            table = activity.find_next_sibling('table')
            for tr in table.find_all('tr'):
                activity_dict = {}
                tds = tr.find_all('td')
                activity_dict['day'] = tds[1].get_text().strip()
                activity_dict['time'] = tds[2].get_text().strip()
                activity_dict['place'] = fix_spacing(tds[3].get_text())
                activity_dict['weeks'] = list(tds[4].get_text().split()[1:])
                activity_list.append(activity_dict)
            course_dict[activity.get_text().strip()] = activity_list

        courses_dict[course.get_text().strip()] = course_dict

    return courses_dict


def get_datetime(start_week, day, time, minutes):
    year = datetime.now().year
    day_idx = WEEKDATES.index(day) + 1
    time_str = str(time).zfill(2)
    min_str = str(minutes).zfill(2)
    day_str = f'{year}-W{start_week-1}-{day_idx}-{time_str}:{min_str}'
    return datetime.strptime(day_str, '%Y-W%W-%w-%H:%M')


def get_event_from_dict(course, activity_name, activity_dict, academic):
    events = []

    for week in activity_dict['weeks']:
        event = Event()
        event.add('summary', f'{course} ({activity_name})')
        logging.info(f'  Creating event:')
        logging.info(f'\tName: {course} ({activity_name})')

        start_week, end_week = week.split('-')
        if ',' in end_week:
            end_week = end_week[:-1]

        start_week, end_week = int(start_week), int(end_week)
        logging.info(f'\tWeeks: {start_week}-{end_week}')

        day = activity_dict['day']
        place = activity_dict['place']
        logging.info(f'\tDay: {day}')
        logging.info(f'\tPlace: {place}')

        start_time, end_time = map(int, activity_dict['time'].split(' - '))

        start_min = '15'
        if not academic:
            start_min = '00'

        logging.info(f'\tTime: {start_time}:{start_min}-{end_time}:00')

        event.add('dtstart', get_datetime(start_week, day,
                                          start_time, start_min))

        event.add('dtend', get_datetime(start_week, day, end_time, '00'))
        event.add('rrule', {'FREQ': 'WEEKLY',
                            'INTERVAL': 1,
                            'COUNT': end_week-start_week+1})
        event['location'] = vText(place)

        events.append(event)

    return events


def make_cal(courses_dict, academic):
    cal = Calendar()
    cal.add('version', '2.0')

    for course, course_dict in courses_dict.items():
        for activity, activity_list in course_dict.items():
            for activity_dict in activity_list:
                for event in get_event_from_dict(course,
                                                 activity,
                                                 activity_dict,
                                                 academic):
                    cal.add_component(event)
    return cal


def calendar_to_file(cal, file_name):
    with open(file_name, 'wb') as f:
        f.write(cal.to_ical())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
             description='Retrieve AU skema as ics')

    parser.add_argument('-i', '--input',
                        help='the filename of a local input file ending in .html')

    parser.add_argument('-l', '--logging', action='store_true',
                        help='show the log')

    parser.add_argument('-n', '--notacademic', action='store_true',
                        help='turn off academic starting time')

    parser.add_argument('-o', '--output',
                        help='output file name ending in .ics')

    args = parser.parse_args()

    if args.logging:
        logging.basicConfig(level=logging.INFO)

    academic = not args.notacademic

    if args.output:
        output_file_name = args.output
    else:
        output_file_name = STANDARD_OUTPUT_FILE_NAME

    if not re.match(r'.*\.ics\b', output_file_name.lower()):
        msg = ' The output filename should end with the .ics extension'
        logging.warning(msg)
        sys.exit(-1)

    if args.input:
        logging.info(f' Parsing: {args.input}')
        soup = get_local_html(args.input)
    else:
        logging.info(f' Retriving skema information from AUs server')
        soup = retrieve_html()

    courses_dict = html_to_json(soup)

    logging.info(' Generating ics file:')
    cal = make_cal(courses_dict, academic)

    logging.info(f' Writing to {output_file_name}')
    calendar_to_file(cal, output_file_name)
    print(f'Generated {output_file_name}')
