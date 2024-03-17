#!/usr/bin/env python3
import argparse
import datetime
import json
import sys

import icalendar
from pkg_resources import resource_string
from tridentine_calendar import tridentine_calendar, utils

UVOC_DATA = json.loads(resource_string(__name__, "uvoc.json"))


def LiturgicalYearToIcal(liturgical_year):
    for date in utils.iterate_liturgical_year(liturgical_year.year):
        for elem in liturgical_year.calendar[date]:
            # Consider displaying outranking information.
            ics_event = icalendar.Event()
            full_name = elem.full_name(capitalize=True)
            if "url" not in UVOC_DATA[full_name]:
                continue
            url = UVOC_DATA[full_name]["url"]
            print("%s %s %s" % (date, full_name, url))
            description = f"<a href={url}>{full_name}</a>"
            ics_event.add("summary", full_name)
            ics_event.add("dtstart", date)
            ics_event.add("description", description)
            ics_event.add("dtstamp", datetime.datetime.now())
            ics_event.add("uid", utils.gen_uid())
            yield ics_event


def LiturgicalCalendarToIcal(liturgical_calendar):
    ics_calendar = icalendar.Calendar()
    ics_calendar.add("prodid", "-//github.oliviergt//Ordo//EN")
    ics_calendar.add("version", "2.0")
    ics_calendar.add("x-wr-calname", "UVOC Tridentine calendar")
    ics_calendar.add(
        "x-wr-caldesc",
        "Liturgical calendar using the 1962 Roman Catholic rubrics with links to propers "
        "provided by Una Voce Orange County (uvoc.org).",
    )
    for liturgical_year in liturgical_calendar.liturgical_years:
        ics_year = LiturgicalYearToIcal(
            liturgical_calendar.liturgical_years[liturgical_year]
        )
        for elem in ics_year:
            ics_calendar.add_component(elem)
    return ics_calendar.to_ical()


def ParseArgs(args):
    parser = argparse.ArgumentParser(
        description=(
            "Generate a liturgical calendar for uvoc.org using the 1962 Roman Catholic rubrics."
        )
    )
    parser.add_argument(
        "start_year",
        nargs=1,
        type=int,
        metavar="START_YEAR",
        help="The starting year (YYYY) for which to generate an ordo (inclusive).",
    )
    parser.add_argument(
        "end_year",
        nargs=1,
        type=int,
        metavar="END_YEAR",
        help="The last year (YYYY) for which to generate an ordo (inclusive).",
    )

    return parser.parse_args(args)


def Main(args):
    years = range(args.start_year[0], args.end_year[0] + 1)
    liturgical_calendar = tridentine_calendar.LiturgicalCalendar(years)
    ical = LiturgicalCalendarToIcal(liturgical_calendar)
    with open("ordo.ics", "wb") as f:
        f.write(ical)


if __name__ == "__main__":
    args = ParseArgs(sys.argv[1:])
    Main(args)
