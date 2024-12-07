from librus import Grade, LibrusSession, SubjectSemesterInfo

import json


class GradeWrapper(Grade):
    def __init__(self, grade: Grade):
        self._grade = grade

    def __str__(self) -> str:
        return (f"{self._grade.grade=}, {self._grade.comment=}, {self._grade.title=}, {self._grade.added_date=}, "
                f"{self._grade.teacher=}, {self._grade.correction_grade=}, {self._grade.added_by}")


class LibrusSessionWrapper(LibrusSession):
    def __init__(self, librus_session: LibrusSession):
        self._librus_session = librus_session

    def get_grades(self):
        response = self._html_session.get(url='https://synergia.librus.pl/przegladaj_oceny/uczen')
        grades = []

        print(response.html)

        for subject in response.html.find('.line0') + response.html.find('.line1'):
            if len(subject.find('td')) == 10 and subject.find('td')[1].text != 'Ocena' and subject.find('td')[
                1].text != '1':
                subject_name = subject.find('td')[1].text
                print(f"{subject_name=}")
                print(f"{subject.find('td')[2].text}")
                for ocena in subject.find("span"):
                    print(f"\t{ocena=}")


class SubjectSemesterInfoWrapper(SubjectSemesterInfo):
    def __init__(self, subject_semester_info: SubjectSemesterInfo):
        self._subject_semester_info = subject_semester_info

        self.subject_name = self._subject_semester_info.subject_name

        if self._subject_semester_info.grades_first_semester == 'Brak ocen':
            self.grades_first_semester = []
        else:
            self.grades_first_semester = self._subject_semester_info.grades_first_semester.split(" ")

        if self._subject_semester_info.grades_second_semester == "Brak ocen":
            self.grades_second_semester = []
        else:
            self.grades_second_semester = self._subject_semester_info.grades_second_semester.split(" ")

    def __str__(self):
        return (f"{self._subject_semester_info.subject_name=}, "
                f"{self._subject_semester_info.grades_first_semester=}, "
                f"{self._subject_semester_info.grade_first_semester_prediction=}, "
                f"{self._subject_semester_info.grade_first_semester=}, "
                f"{self._subject_semester_info.grades_second_semester=}, "
                f"{self._subject_semester_info.grade_second_semester_prediction=}, "
                f"{self._subject_semester_info.grade_second_semester=}")

    def to_json(self):
        tmp = {"subject_name": self._subject_semester_info.subject_name,
               "grades_first_semester": self.grades_first_semester,
               "grades_second_semester": self.grades_second_semester}

        return json.dumps(tmp, ensure_ascii=False)
