import logging
import time

logger = logging.getLogger(__name__)


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start the timer when a request is received
        start_time = time.time()

        # Process the request and get the response
        response = self.get_response(request)

        # Calculate the time taken to process the request
        duration = time.time() - start_time

        # Log the time taken
        logger.info(f"Request to {request.path} took {duration:.2f} seconds.")

        return response
