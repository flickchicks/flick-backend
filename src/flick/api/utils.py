from rest_framework import status
from rest_framework.response import Response


def success_response(data, status=status.HTTP_200_OK):
    return Response({"success": True, "data": data}, status=status)


def failure_response(message, status=status.HTTP_404_NOT_FOUND):
    return Response({"success": False, "error": message}, status=status)
