from django.core.paginator import Paginator


def paginate_queryset(queryset, per_page, page_number):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
