from PyAsoka.Instruments import Log

from datetime import datetime, timedelta, timezone
from enum import Enum, auto


class ATimepoint:

    class Format(Enum):
        FULL = auto()
        SIMPLE = auto()

    def __init__(self, year: int = -1, month: int = -1, day: int = -1,
                 hour: int = -1, minute: int = -1, second: int = -1, tzone: int = None, timepoint=None):
        self._year_ = -1
        self._month_ = -1
        self._day_ = -1
        self._hour_ = -1
        self._minute_ = -1
        self._second_ = -1
        self._timezone_ = 3
        self.set(year, month, day, hour, minute, second, tzone, timepoint)

    def __add__(self, other):
        timepoint = ATimepoint()
        if isinstance(other, ATimepoint):
            timepoint.fromTimedelta(self.toTimedelta() + other.toTimedelta())
        elif isinstance(other, datetime):
            timepoint.fromTimedelta(self.toTimedelta() + ATimepoint(timepoint=other).toTimedelta())
        elif isinstance(other, int):
            timepoint.fromTimedelta(self.toTimedelta() + timedelta(seconds=other))
        else:
            Log.exception_unsupportable_type(type(other))
        return timepoint

    def __sub__(self, other):
        timepoint = ATimepoint()
        if isinstance(other, ATimepoint):
            timepoint.fromTimedelta(self.toTimedelta() - other.toTimedelta())
        elif isinstance(other, datetime):
            timepoint.fromTimedelta(self.toTimedelta() - ATimepoint(timepoint=other).toTimedelta())
        elif isinstance(other, int):
            timepoint.fromTimedelta(self.toTimedelta() - timedelta(seconds=other))
        else:
            Log.exception_unsupportable_type(type(other))
        return timepoint

    def set(self, year: int = -1, month: int = -1, day: int = -1,
                 hour: int = -1, minute: int = -1, second: int = -1, tzone: int = None, timepoint=None):
        if timepoint is not None:
            if issubclass(type(timepoint), ATimepoint):
                self.fromTimepoint(timepoint)
            elif issubclass(type(timepoint), datetime):
                self.fromDatetime(timepoint)
        else:
            self._year_ = year
            self._month_ = month
            self._day_ = day
            self._hour_ = hour
            self._minute_ = minute
            self._second_ = second
            self._timezone_ = 3 if tzone is None else tzone

    def strftime(self, _format):
        return self.toDatetime().strftime(_format)

    def __str__(self):
        return f'{self.day():02}.{self.month():02}.{self.year():04} ' \
               f'{self.hour():02}:{self.minute():02}:{self.second():02} UTC {self._timezone_}'

    def encode(self):
        return f'{self.day()}.{self.month()}.{self.year()}.{self.hour()}.{self.minute()}.{self.second()}.{self._timezone_}'

    def year(self, _format: Format = Format.SIMPLE):
        if self._year_ == -1:
            return 0
        if _format is self.Format.SIMPLE:
            return self._year_

    def month(self, _format: Format = Format.SIMPLE):
        if self._month_ == -1:
            return 0
        if _format is self.Format.SIMPLE:
            return self._month_

    def day(self, _format: Format = Format.SIMPLE):
        if self._day_ == -1:
            return 0
        if _format is self.Format.SIMPLE:
            return self._day_

    def hour(self, _format: Format = Format.SIMPLE):
        if self._hour_ == -1:
            return 0
        if _format is self.Format.SIMPLE:
            return self._hour_

    def minute(self, _format: Format = Format.SIMPLE):
        if self._minute_ == -1:
            return 0
        if _format is self.Format.SIMPLE:
            return self._minute_

    def second(self, _format: Format = Format.SIMPLE):
        if self._second_ == -1:
            return 0
        if _format is self.Format.SIMPLE:
            return self._second_

    def timezone(self):
        return self._timezone_

    def days(self):
        return self.toTimedelta().days

    def fromTimepoint(self, timepoint):
        if issubclass(type(timepoint), ATimepoint):
            self._year_ = timepoint.year()
            self._month_ = timepoint.month()
            self._day_ = timepoint.day()
            self._hour_ = timepoint.hour()
            self._minute_ = timepoint.minute()
            self._second_ = timepoint.second()
            self._timezone_ = timepoint.timezone()
        else:
            Log.exception_unsupportable_type(type(timepoint))

    def fromDatetime(self, timepoint):
        if issubclass(type(timepoint), datetime):
            self._year_ = timepoint.year
            self._month_ = timepoint.month
            self._day_ = timepoint.day
            self._hour_ = timepoint.hour
            self._minute_ = timepoint.minute
            self._second_ = timepoint.second
            self._timezone_ = 3
        else:
            Log.exception_unsupportable_type(type(timepoint))

    def fromTimedelta(self, tdelta: timedelta):
        if isinstance(tdelta, timedelta):
            self.fromDatetime(datetime(1, 1, 1) + tdelta)
            if tdelta.days < 365 and self._year_ == 1:
                self._year_ = 0
            if tdelta.days < 28 and self._month_ == 1:
                self._month_ = 0
            if tdelta.days < 0 and self._day_ == 1:
                self._day_ = 0
        else:
            Log.exception_unsupportable_type(type(tdelta))

    def toDatetime(self):
        return datetime(self.year() if self._year_ > 0 else 1,
                        self.month() if self._month_ > 0 else 1,
                        self.day() if self._day_ > 0 else 1,
                        self.hour() if self._hour_ != -1 else 0,
                        self.minute() if self._minute_ != -1 else 0,
                        self.second() if self._second_ != -1 else 0)

    def toTimedelta(self):
        return self.toDatetime() - datetime(1, 1, 1)

    @staticmethod
    def decode(string: str):
        args = string.split('.')
        if len(args) > 6:
            return ATimepoint(int(args[2]), int(args[1]), int(args[0]),
                              int(args[3]), int(args[4]), int(args[5]), int(args[6]))


    @staticmethod
    def now():
        return ATimepoint(timepoint=datetime.now())
