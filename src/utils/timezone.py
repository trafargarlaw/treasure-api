import zoneinfo

from datetime import datetime
from datetime import timezone as datetime_timezone

from src.core.conf import settings


class TimeZone:
    def __init__(self, tz: str = settings.DATETIME_TIMEZONE):
        self.tz_info = zoneinfo.ZoneInfo(tz)

    def now(self) -> datetime:
        """
        Get timezone time

        :return:
        """
        return datetime.now(self.tz_info)

    def f_datetime(self, dt: datetime) -> datetime:
        """
        Convert datetime to timezone time

        :param dt:
        :return:
        """
        return dt.astimezone(self.tz_info)

    def f_str(self, date_str: str, format_str: str = settings.DATETIME_FORMAT) -> datetime:
        """
        Convert time string to timezone time

        :param date_str:
        :param format_str:
        :return:
        """
        return datetime.strptime(date_str, format_str).replace(tzinfo=self.tz_info)

    @staticmethod
    def f_utc(dt: datetime) -> datetime:
        """
        Convert timezone time to UTC (GMT) timezone

        :param dt:
        :return:
        """
        return dt.astimezone(datetime_timezone.utc)


timezone: TimeZone = TimeZone()
