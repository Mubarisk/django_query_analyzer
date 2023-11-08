from django.db import connection
import time
from .models import QueryAnalyzer


class QueryAnalyzerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # exclude admin urls
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        # exclude the path /query-analyzer/
        if request.path.startswith('/query-analyzer/'):
            return self.get_response(request)
        #  exclude swagger urls
        if request.path.startswith('/swagger/'):
            return self.get_response(request)

        if request.path.startswith('/docs/'):
            return self.get_response(request)

        query_list = []
        # Start timing the request processing
        start_time = time.time()

        response = self.get_response(request)

        # Calculate the time taken for the request
        total_time = time.time() - start_time

        # Analyze and log database queries
        query_count = len(connection.queries)
        # print(connection.queries)
        db_time = sum(float(query['time']) for query in connection.queries)

        # Capture the executed queries
        for query in connection.queries:
            query_list.append({
                'sql': query['sql'],
                'time': query['time'],
            })

        # Log the query analysis
        print(f"API Request: {request.method} {request.path}")
        print(f"Query Count: {query_count}")
        print(f"Database Time: {db_time:.3f} ms")
        print(f"Total Time: {total_time:.3f} s")

        # Store the query analysis in the database
        QueryAnalyzer.objects.create(
            method=request.method,
            path=request.path,
            query_count=query_count,
            db_time=db_time,
            total_time=total_time,
            query_list=query_list
        )

        return response