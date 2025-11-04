from django.apps import AppConfig


class IndexConfig(AppConfig):
    name = "index"
    # def ready(self):
    #     from .views import get_top_random_by_genre
    #     for _, keywords in [
    #         ('Action',   ['Action']),
    #         ('Drama',    ['Drama']),
    #         ('Comedy',   ['Comedy']),
    #         ('Romance',  ['Romance']),
    #         ('Sci-Fi',   ['Science Fiction','Sci-Fi','Sci Fi']),
    #     ]:
    #         get_top_random_by_genre(keywords)
