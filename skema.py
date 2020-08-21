import sys
import re
import logging
import argparse

from bs4 import BeautifulSoup
from icalendar import Calendar, Event, vText
from datetime import datetime

WEEKDATES = ['Mandag', 'Tirsdag', 'Onsdag',
             'Torsdag', 'Fredag', 'Lørdag', 'Søndag']

STANDARD_OUTPUT_FILE_NAME = 'skema.ics'


def fix_spacing(string):
    return re.sub(r'\s+', ' ', string).strip()


def html_to_json(file_name):
    try:
        with open(file_name, 'rb') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except FileNotFoundError:
        print(f'{file_name} does not exist')
        sys.exit(-1)

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
        logging.info(f'Creating event: {course} ({activity_name})')

        start_week, end_week = week.split('-')
        if ',' in end_week:
            end_week = end_week[:-1]

        start_week, end_week = int(start_week), int(end_week)
        logging.info(f'Weeks: {start_week}-{end_week}')

        day = activity_dict['day']
        place = activity_dict['place']
        logging.info(f'Day: {day}')
        logging.info(f'Place: {place}')

        start_time, end_time = map(int, activity_dict['time'].split(' - '))

        logging.info(f'Time: {start_time}:15-{end_time}:00')

        start_min = '15'
        if not academic:
            start_min = '00'

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
             description='Convert skema HTML to ical file')

    parser.add_argument('input_file_name', metavar='filename',
                        help='the filename of the input file ending in .html')

    parser.add_argument('-l', '--logging', action='store_true',
                        help='show the log')

    parser.add_argument('-n', '--notacademic', action='store_true',
                        help='turn off academic starting time')

    parser.add_argument('-o', '--output',
                        help='output file name ending in .ics')

    args = parser.parse_args()

    if args.logging:
        logging.basicConfig(level=logging.INFO)

    input_file_name = args.input_file_name
    academic = not args.notacademic

    if args.output:
        output_file_name = args.output
    else:
        output_file_name = STANDARD_OUTPUT_FILE_NAME

    logging.info(f'Parsing: {input_file_name}')

    courses_dict = html_to_json(input_file_name)

    logging.info(f'Generating ical file')
    cal = make_cal(courses_dict, academic)

    logging.info(f'Writing to {output_file_name}')
    calendar_to_file(cal, output_file_name)
