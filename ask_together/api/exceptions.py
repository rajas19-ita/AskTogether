import logging
from rest_framework.views import exception_handler
from rest_framework import status 
from rest_framework.response import Response

logger = logging.getLogger(__name__)    

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response(
            {
                "success": False,
                "error": response.data
            },
            status=response.status_code
        )

    logger.exception("Unhandled API error")
    return Response(
        {
            "success": False,
            "message": "Something went wrong. Please try again."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )