from librus import LibrusSession

import json
import copy

from modules.wrapper_classes import GradeWrapper, LibrusSessionWrapper, SubjectSemesterInfoWrapper
from modules.mail import MailBuilder
from modules import utils


class Notifier():
    def __init__(self):
        librus_username = utils.get_config_entry('librus_username')
        librus_password = utils.get_config_entry('librus_password')

        self._session = LibrusSessionWrapper(LibrusSession())
        self._session.login(librus_username, librus_password)

        self._messages = []
        self._announcements = []
        self._announcement_log_filename = utils.get_config_entry('announcement_log_filename')

        self._subject_semester_info = []
        self._grades_to_notify = []
        self._grades_log_filename = utils.get_config_entry('grades_log_filename')

    def check_for_messages(self):
        for m in self._session.list_messages(get_content=True):
            if not m.is_read:
                self._messages.append({'message_id': m.message_id, 'sent_at': m.sent_at, 'subject': m.subject,
                                       'sender': m.sender, 'is_read': m.is_read, 'content': m.content})

    def _is_announcement_proceeded(self, current_announcement):
        with open(self._announcement_log_filename, 'r', encoding='utf-8') as f:
            previous_announcements = f.read()

        if len(previous_announcements) == 0:
            return False

        previous_announcements = json.loads(previous_announcements)
        for a in previous_announcements:
            if a['date'] == current_announcement['date'] and a['title'] == current_announcement['title']:
                return True

        return False

    def check_for_announcements(self):
        for a in self._session.list_announcements():

            announcement = {'title': a.title, 'content': a.content,
                            'author': a.author, 'date': f'{a.date}'}

            if self._is_announcement_proceeded(announcement):
                break

            self._announcements.append(announcement)

    def _log_last_read_announcement(self):

        if len(self._announcements) == 0:
            return

        logfile_entry = []
        with open(self._announcement_log_filename, 'r', encoding='utf-8') as f:
            current_announcements = json.loads(f.read())
            if len(current_announcements) == 0:
                return
            logfile_entry += current_announcements

        logfile_entry += [{'date': f'{a["date"]}', 'title': a['title']}
                          for a in self._announcements]
        logfile_entry = sorted(
            logfile_entry, key=lambda sort_by: sort_by['date'], reverse=True)

        with open(self._announcement_log_filename, 'w', encoding='utf-8') as f:
            json.dump(logfile_entry, f, ensure_ascii=False)

    def check_grades(self):
        for ssi in self._session.list_subject_semester_info():
            self._subject_semester_info.append(SubjectSemesterInfoWrapper(ssi))

        self._prepare_grades_to_notify()
        self._update_grades_log()

    def _prepare_grades_to_notify(self):
        with open(self._grades_log_filename, "r", encoding="utf-8") as file:
            current_grades = json.loads(file.read())

        semester_info = copy.deepcopy(self._subject_semester_info)
        for ssi in semester_info:
            for cg in current_grades:
                grade = json.loads(cg)
                if grade["subject_name"] == ssi.subject_name:

                    for grades_first_sem in grade["grades_first_semester"]:
                        ssi.grades_first_semester.remove(grades_first_sem)

                    for grades_second_sem in grade["grades_second_semester"]:
                        ssi.grades_second_semester.remove(grades_second_sem)

            for grade in ssi.grades_first_semester:
                self._grades_to_notify.append(GradeSimple(ssi.subject_name, grade))

            for grade in ssi.grades_second_semester:
                self._grades_to_notify.append(GradeSimple(ssi.subject_name, grade))

    def _update_grades_log(self):
        with open(self._grades_log_filename, "w", encoding="utf-8") as file:
            json.dump([ssi.to_json() for ssi in self._subject_semester_info], file, ensure_ascii=False)

    def _get_mail_subject(self):
        subject = '[Librus] '
        if len(self._messages) > 0:
            subject += f'Nowe wiadomości: {len(self._messages)}.'
        if len(self._announcements) > 0:
            subject += f'Nowe ogłoszenia: {len(self._announcements)}.'
        if len(self._grades_to_notify) > 0:
            subject += f'Nowe oceny: {len(self._grades_to_notify)}.'

        return subject

    def _get_messages_content(self):
        content = ''
        for m in self._messages:
            content += f'Wiadomość od {m["sender"]} z dnia {m["sent_at"]} o tytule {m["subject"]}\n'
            content += f'Treść wiadomości:\n{m["content"]}'
            content += '\n\n----------------------------------------------------\n\n'

        return content

    def _get_announcements_content(self):
        content = ''
        for a in self._announcements:
            content += f'Ogłoszenie od {a["author"]} z dnia {a["date"]} o tytule {a["title"]}'
            content += f'Treść ogłoszenia:\n{a["content"]}'
            content += '\n\n----------------------------------------------------\n\n'

        return content

    def _get_grade_content(self) -> str:
        content = ""
        for grade in self._grades_to_notify:
            content += f"Nowa ocena z przedmiotu {grade.subject}: {grade.grade}\n"
        content += '\n\n----------------------------------------------------\n\n'

        return content

    def _get_content(self):
        return self._get_messages_content() + self._get_announcements_content() + self._get_grade_content()

    def send_notification(self, receivers):
        if len(self._messages) > 0 or len(self._announcements) > 0 or len(self._grades_to_notify) > 0:
            mail = MailBuilder().subject(self._get_mail_subject()).content(
                self._get_content()).receivers(receivers).build()
            mail.send()

            self._log_last_read_announcement()
        else:
            print('No entries to notify')


class GradeSimple:
    def __init__(self, subject: str, grade: str):
        self.subject = subject
        self.grade = grade

    def __str__(self):
        return f"subject={self.subject}, grade={self.grade}"
