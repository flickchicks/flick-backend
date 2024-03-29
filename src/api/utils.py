from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, status=status.HTTP_200_OK):
    if data is None:
        return Response({"success": True}, status=status)
    return Response({"success": True, "data": data}, status=status)


def failure_response(message=None, status=status.HTTP_404_NOT_FOUND):
    if message is None:
        return Response({"success": False}, status=status)
    return Response({"success": False, "error": message}, status=status)


def success_response_with_query(query, data, status=status.HTTP_200_OK):
    return Response({"success": True, "query": query, "data": data}, status=status)


def failure_response_with_query(query, message, status=status.HTTP_404_NOT_FOUND):
    return Response({"success": False, "query": query, "error": message}, status=status)
