from rest_framework.response import Response
from rest_framework import pagination

from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound

class CustomPagination(pagination.PageNumberPagination):
    
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            #return the first page
            self.page = paginator.page(1)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
    
    def get_paginated_response(self, data):
            
        if self.page.has_previous():
            if self.page.has_next():
                page_number = int(self.page.next_page_number()) - 1
            else:
                page_number = 1
        else:
            page_number = 1
            
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'page': page_number,
            'last_page': self.page.paginator.num_pages,
            'results': data,
        })