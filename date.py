# -*- coding: UTF-8 -*-
"""
@author: wycai@pku.edu.cn
"""


class Date:
    def __init__(self, date_str: str = None, year: int = None, month: int = None, day: int = None):
        if date_str:
            split = date_str.split('-')
            if len(split) == 3:
                self.year = int(split[0])
                self.month = int(split[1])
                self.day = int(split[2])
            elif len(split) == 2:
                self.year = None
                self.month = int(split[0])
                self.day = int(split[1])
            else:
                raise ValueError('date_str format is wrong.')
        else:
            self.year = year
            assert month, 'month can not be None.'
            self.month = month
            assert day, 'day can not be None.'
            self.day = day

    def to_str(self, show_year: bool = True):
        if self.year and show_year:
            return '%04d-%02d-%02d' % (self.year, self.month, self.day)
        else:
            return '%02d-%02d' % (self.month, self.day)

    def __repr__(self):
        if self.year:
            return '%04d-%02d-%02d' % (self.year, self.month, self.day)
        else:
            return '%02d-%02d' % (self.month, self.day)

    def __eq__(self, other):
        assert isinstance(other, Date), 'Can not compare Date with other class.'
        if self.__dict__ == other.__dict__:
            return True
        else:
            return False

    def __gt__(self, other):
        assert isinstance(other, Date), 'Can not compare Date with other class.'
        if self.year and other.year:
            if self.year > other.year:
                return True
            elif self.year < other.year:
                return False
            else:
                if self.month > other.month:
                    return True
                elif self.month < other.month:
                    return False
                else:
                    if self.day > other.day:
                        return True
                    else:
                        return False
        else:
            if self.month > other.month:
                return True
            elif self.month < other.month:
                return False
            else:
                if self.day > other.day:
                    return True
                else:
                    return False

    def __ge__(self, other):
        assert isinstance(other, Date), 'Can not compare Date with other class.'
        if self.year and other.year:
            if self.year > other.year:
                return True
            elif self.year < other.year:
                return False
            else:
                if self.month > other.month:
                    return True
                elif self.month < other.month:
                    return False
                else:
                    if self.day >= other.day:
                        return True
                    else:
                        return False
        else:
            if self.month > other.month:
                return True
            elif self.month < other.month:
                return False
            else:
                if self.day >= other.day:
                    return True
                else:
                    return False

    def __lt__(self, other):
        assert isinstance(other, Date), 'Can not compare Date with other class.'
        if self.year and other.year:
            if self.year < other.year:
                return True
            elif self.year > other.year:
                return False
            else:
                if self.month < other.month:
                    return True
                elif self.month > other.month:
                    return False
                else:
                    if self.day < other.day:
                        return True
                    else:
                        return False
        else:
            if self.month < other.month:
                return True
            elif self.month > other.month:
                return False
            else:
                if self.day < other.day:
                    return True
                else:
                    return False

    def __le__(self, other):
        assert isinstance(other, Date), 'Can not compare Date with other class.'
        if self.year and other.year:
            if self.year < other.year:
                return True
            elif self.year > other.year:
                return False
            else:
                if self.month < other.month:
                    return True
                elif self.month > other.month:
                    return False
                else:
                    if self.day <= other.day:
                        return True
                    else:
                        return False
        else:
            if self.month < other.month:
                return True
            elif self.month > other.month:
                return False
            else:
                if self.day <= other.day:
                    return True
                else:
                    return False
