import rest_framework.pagination


class IdPagination(rest_framework.pagination.CursorPagination):
    ordering = ["-id"]
