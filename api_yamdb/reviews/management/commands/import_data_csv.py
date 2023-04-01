import csv

from django.core.management.base import BaseCommand

from reviews.forms import (
    CategoriesForm,
    CommentsForm,
    GenreTitleForm,
    GenresForm,
    ReviewsForm,
    TitlesForm,
    UserForm
)


FILENAME_MODEL_DICT = {
    'users.csv': UserForm,
    'category.csv': CategoriesForm,
    'genre.csv': GenresForm,
    'titles.csv': TitlesForm,
    'genre_title.csv': GenreTitleForm,
    'review.csv': ReviewsForm,
    'comments.csv': CommentsForm,
}
DATA_PATH = 'static/data/'


class Command(BaseCommand):
    help = ('Imports data from a local csv file if there is flag --filename '
            'or all files if there is not. '
            'Expects files named category.csv, comments.csv, '
            'genre.csv, genre_title.csv, review.csv, titles.csv, users.csv')

    def add_arguments(self, parser):
        parser.add_argument('--category.csv',
                            action='store_true',
                            help='Import category.csv file in database '
                                 'if it contains valid ids and data')
        parser.add_argument('--comments.csv',
                            action='store_true',
                            help='Import comments.csv file in database '
                                 'if it contains valid ids and data')
        parser.add_argument('--genre.csv',
                            action='store_true',
                            help='Import genre.csv file in database '
                                 'if it contains valid ids and data')
        parser.add_argument('--genre_title.csv',
                            action='store_true',
                            help='Import genre_title.csv file in database '
                                 'if it contains valid ids and data')
        parser.add_argument('--review.csv',
                            action='store_true',
                            help='Import review.csv file in database '
                                 'if it contains valid ids and data')
        parser.add_argument('--titles.csv',
                            action='store_true',
                            help='Import titles.csv file in database '
                                 'if it contains valid ids and data')
        parser.add_argument('--users.csv',
                            action='store_true',
                            help='Import users.csv file in database '
                                 'if it contains valid ids and data')

    def _choice_of_particular(self, **kwargs):
        for keys in FILENAME_MODEL_DICT.keys():
            if kwargs[keys]:
                self.filename = keys
                return True
        return False

    def _save_row_to_database(self, row):
        form = FILENAME_MODEL_DICT[self.filename](data=row)
        if form.is_valid():
            form.save()
            self.imported_counter += 1
            return form
        return form

    def _stdout_error(self, form, row):
        self.skipped_counter += 1
        self.stderr.write(
            f'{"_" * 120}\nErrors while import {self.file_path} | {row}:\n'
        )
        self.stderr.write(f'{form.errors.as_data()}\n')

    def _import_csv(self):
        with open(self.file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                form = self._save_row_to_database(row=row)
                if form.errors:
                    self._stdout_error(form=form, row=row)

    def prepare(self):
        self.imported_counter = 0
        self.skipped_counter = 0

    def main(self):
        self.stdout.write(f'{"_" * 120}\nStarting import {self.filename}')
        self._import_csv()

    def finalise(self):
        self.stdout.write(f'Import {self.filename} ends\n'
                          f'Instances imported: {self.imported_counter}\n'
                          f'Instances skipped: {self.skipped_counter}\n')

    def handle(self, *args, **kwargs):
        if self._choice_of_particular(**kwargs):
            self.prepare()
            self.file_path = DATA_PATH + self.filename
            self.main()
            self.finalise()

        else:
            for keys, values in FILENAME_MODEL_DICT.items():
                self.prepare()
                self.filename = keys
                self.file_path = DATA_PATH + self.filename
                self.main()
                self.finalise()
