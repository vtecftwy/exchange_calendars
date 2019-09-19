#
# Copyright 2019 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import time, timedelta

import pandas as pd
from pandas.tseries.holiday import Easter, GoodFriday, Holiday
from pandas.tseries.offsets import Day
from pytz import timezone, UTC

from .common_holidays import (
    new_years_day,
    maundy_thursday,
    european_labour_day,
    assumption_day,
    all_saints_day,
    immaculate_conception,
    christmas_eve,
    christmas,
    new_years_eve,
)
from .trading_calendar import (
    HolidayCalendar,
    TradingCalendar,
    MONDAY,
    TUESDAY,
    WEDNESDAY,
    THURSDAY,
    FRIDAY,
    WEEKDAYS,
)


def nearest_monday(datetime_index):
    """
    If the holiday falls on a Saturday, Sunday or Monday then the date is
    unchanged (Sat/Sun observances are not made up), otherwise use the closest
    Monday to the date.
    """
    day = datetime_index.weekday()

    if day in (TUESDAY, WEDNESDAY, THURSDAY):
        return datetime_index - timedelta(day - MONDAY)
    elif day == FRIDAY:
        return datetime_index + timedelta(3)
    return datetime_index


def tuesday_and_wednesday_to_friday(datetime_index):
    """
    If Evangelical Church Day (Halloween) falls on a Tuesday, it is observed
    the preceding Friday. If it falls on a Wednesday, it is observed the next
    Friday. If it falls on Thu, Fri, Sat, Sun, or Mon the date is unchanged.
    """
    day = datetime_index.weekday()

    if day == TUESDAY:
        return datetime_index - timedelta(4)
    elif day == WEDNESDAY:
        return datetime_index + timedelta(2)
    return datetime_index


def not_2010(datetime_index):
    """
    In 2010 Independence Day fell on a Saturday. Normally this would mean that
    Friday is a half day, but instead it is a full day off, so we need to
    exclude it from the usual half day rules.
    """
    return datetime_index[datetime_index.year != 2010]


NewYearsDay = new_years_day()

MaundyThursday = maundy_thursday()
MondayPriorToCorpusChristi = Holiday(
    'Monday Prior to Corpus Christi',
    month=1,
    day=1,
    offset=[Easter(), Day(57)],
    end_date='2008',
)

LabourDay = european_labour_day()

NavyDay = Holiday('Navy Day', month=5, day=21)

SaintPeterAndSaintPaulDay = Holiday(
    'Saint Peter and Saint Paul Day',
    month=6,
    day=29,
    observance=nearest_monday,
)

OurLadyOfMountCarmelDay = Holiday(
    "Our Lady of Mount Carmel's Day",
    month=7,
    day=16,
    start_date='2008',
)

AssumptionDay = assumption_day()

PublicHolidayMonday = Holiday(
    'Public Holiday Preceeding a Tuesday Independence Day',
    month=9,
    day=17,
    start_date='2003',
    days_of_week=(MONDAY,),
)
DayBeforeIndependenceDay = Holiday(
    'Day Before Independence Day',
    month=9,
    day=17,
    observance=not_2010,
    days_of_week=(TUESDAY, WEDNESDAY, THURSDAY, FRIDAY),
)
IndependenceDay = Holiday('Independence Day', month=9, day=18)
ArmyDay = Holiday('Army Day', month=9, day=19)
PublicHolidayFriday = Holiday(
    'Public Holiday Following a Thursday Army Day',
    month=9,
    day=20,
    start_date='2003',
    days_of_week=(FRIDAY,),
)

DiaDeLaRaza = Holiday(
    'Dia de la Raza',
    month=10,
    day=12,
    observance=nearest_monday,
)

EvangelicalChurchDay = Holiday(
    'Evangelical Church Day',
    month=10,
    day=31,
    observance=tuesday_and_wednesday_to_friday,
    start_date='2008',
)
AllSaintsDay = all_saints_day()

ImmaculateConception = immaculate_conception()

ChristmasEve = christmas_eve(days_of_week=WEEKDAYS)
Christmas = christmas()

DayBeforeBankHoliday = Holiday(
    'Day Before Bank Holiday',
    month=12,
    day=30,
    days_of_week=WEEKDAYS,
)
BankHoliday = new_years_eve()


class XSGOExchangeCalendar(TradingCalendar):
    """
    Calendar for the Santiago Stock Exchange (Bolsa de Comercio de Santiago) in
    Chile.

    Open Time: 9:30 AM, CLT/CLST (Chile Standard Time/Chile Summer Time)
    Close Time: 4:00 PM, CLT (March to October)
                5:00 PM, CLST (November to February)

    Regularly-Observed Holidays:
      - New Year's Day
      - Good Friday
      - Corpus Christi (until 2007, inclusive)
      - Labour Day
      - Navy Day
      - Saint Peter and Saint Paul Day
      - Feast Day of Our Lady of Mount Carmel (starting 2008)
      - Assumption Day
      - Independence Day
      - Army Day
      - Dia de la Raza
      - Evangelical Church Day
      - All Saints' Day
      - Immaculate Conception
      - Christmas Day
      - Bank Holiday

    Holidays No Longer Observed:
      - N/A

    Early Closes:
      - Maundy Thursday
      - Day before Independence Day
      - Christmas Eve
      - Day before Bank Holiday
    """
    name = 'XSGO'
    tz = timezone('America/Santiago')

    open_times = (
        (None, time(9, 31)),
    )
    early_close_1230 = time(12, 30)
    early_close_130 = time(13, 30)

    @property
    def close_times(self):
        # The equity market close time changes twice per year. In March it
        # changes to 4:00PM for winter and in November it changes to 5PM for
        # summer.
        return tuple(self._starting_dates_and_close_times())

    @property
    def regular_holidays(self):
        return HolidayCalendar([
            NewYearsDay,
            GoodFriday,
            MondayPriorToCorpusChristi,
            LabourDay,
            NavyDay,
            SaintPeterAndSaintPaulDay,
            OurLadyOfMountCarmelDay,
            AssumptionDay,
            PublicHolidayMonday,
            IndependenceDay,
            ArmyDay,
            PublicHolidayFriday,
            DiaDeLaRaza,
            EvangelicalChurchDay,
            AllSaintsDay,
            ImmaculateConception,
            Christmas,
            BankHoliday,
        ])

    @property
    def adhoc_holidays(self):
        return [
            # Bicentennial Celebration.
            pd.Timestamp('2010-09-17', tz=UTC),
            pd.Timestamp('2010-09-20', tz=UTC),
            # New Year's Day Observed. It is unclear why this happened only for
            # this one year.
            pd.Timestamp('2017-01-02', tz=UTC),
            # Census Day.
            pd.Timestamp('2017-04-19', tz=UTC),
            # Pope Visit.
            pd.Timestamp('2018-01-16', tz=UTC),
        ]

    @property
    def special_closes(self):
        return [
            (
                self.early_close_1230,
                HolidayCalendar([ChristmasEve, DayBeforeBankHoliday]),
            ),
            (
                self.early_close_130,
                HolidayCalendar([MaundyThursday, DayBeforeIndependenceDay]),
            ),
        ]

    def _starting_dates_and_close_times(self):
        yield ((None, time(17)))
        for year in range(1980, 2050):
            yield (pd.Timestamp('{}-03-01'.format(year)), time(16))
            yield (pd.Timestamp('{}-11-01'.format(year)), time(17))
