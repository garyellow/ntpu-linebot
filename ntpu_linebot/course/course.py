# -*- coding:utf-8 -*-
ALL_COURSE_CODE = ["U", "M", "N", "P"]


class SimpleCourse:
    def __init__(
        self,
        year: int,
        term: int,
        no: str,
        title: str,
        teachers: list[str],
        times: list[str],
    ):
        self.__year = year
        self.__term = term
        self.__no = no
        self.__title = title
        self.__teachers = teachers
        self.__times = times

    @property
    def year(self) -> int:
        """Getter for year"""
        return self.__year

    @property
    def term(self) -> int:
        """Getter for term"""
        return self.__term

    @property
    def no(self) -> str:
        """Getter for no"""
        return self.__no

    @property
    def title(self) -> str:
        """Getter for title"""
        return self.__title

    @property
    def teachers(self) -> list[tuple[str, str]]:
        """Getter for teachers"""
        return self.__teachers

    @property
    def times(self) -> list[str]:
        """Getter for times"""
        return self.__times

    @property
    def uid(self) -> str:
        """Getter for uid"""
        return f"{self.__year}{self.__term}{self.__no}"

    def __str__(self) -> str:
        return self.uid


class Course(SimpleCourse):
    __REAL_BASE_URL = "https://sea.cc.ntpu.edu.tw"
    __TEACHER_QUERY_URL = "/pls/faculty/tec_course_table.s_table"
    __DETAIL_QUERY_URL = "/pls/dev_stud/course_query.queryGuide"
    __COURSE_QUERY_URL = "/pls/dev_stud/course_query_all.queryByKeyword"

    def __init__(
        self,
        year: int,
        term: int,
        no: str,
        title: str,
        teachers: list[str],
        teachers_url: list[str],
        times: list[str],
        locations: list[str],
        detail_url: str,
        note: str,
    ):
        super().__init__(year, term, no, title, teachers, times)
        self.__teachers_url = teachers_url
        self.__locations = locations
        self.__detail_url = detail_url
        self.__note = note

    @property
    def year(self) -> int:
        """Getter for year"""
        return super().year

    @property
    def term(self) -> int:
        """Getter for term"""
        return super().term

    @property
    def no(self) -> str:
        """Getter for no"""
        return super().no

    @property
    def title(self) -> str:
        """Getter for title"""
        return super().title

    @property
    def teachers(self) -> list[str]:
        """Getter for teachers"""
        return super().teachers

    @property
    def times(self) -> list[str]:
        """Getter for times"""
        return super().times

    @property
    def teachers_url(self) -> list[str]:
        """Getter for teachers_url"""
        return [
            self.__REAL_BASE_URL + self.__TEACHER_QUERY_URL + teacher_url
            for teacher_url in self.__teachers_url
        ]

    @property
    def locations(self) -> list[str]:
        """Getter for locations"""
        return self.__locations

    @property
    def detail_url(self) -> str:
        """Getter for detail_url"""
        return self.__REAL_BASE_URL + self.__DETAIL_QUERY_URL + self.__detail_url

    @property
    def note(self) -> str:
        """Getter for note"""
        return self.__note

    @property
    def teachers_name_url(self) -> list[tuple[str, str]]:
        """Getter for teachers_name_url"""
        return [
            (self.teachers[index], self.teachers_url[index])
            for index in range(len(self.teachers))
        ]

    @property
    def course_query_url(self) -> str:
        """Getter for course_query_url"""
        return (
            self.__REAL_BASE_URL
            + self.__COURSE_QUERY_URL
            + f"?qYear={self.year}&qTerm={self.term}&courseno={self.no}&seq1=A&seq2=M"
        )
