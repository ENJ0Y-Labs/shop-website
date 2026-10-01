from flask import jsonify


class APIError(Exception):
    def __init__(self, message, status_code=400, code="bad_request"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({"error": {"code": error.code, "message": error.message}}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": {"code": "not_found", "message": "Resource not found"}}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": {"code": "method_not_allowed", "message": "Method not allowed"}}), 405

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error")
        return jsonify({"error": {"code": "internal_error", "message": "An unexpected error occurred"}}), 500
