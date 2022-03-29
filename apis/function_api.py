"""
A module for common functions used in multiple API definitions.
"""

from typing import Tuple
from flask import (
    Response,
    jsonify
)

def error_response(errors: list[str], status_code=422) -> Tuple[Response, int]:
    return jsonify(errors=errors, count=len(errors)), status_code
