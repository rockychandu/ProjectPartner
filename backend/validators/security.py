import os
import re

class SecurityValidator:
    @staticmethod
    def sanitize_string(input_str):
        if not input_str:
            return ""
        # Strip dangerous HTML script tags
        clean = re.sub(r'<script.*?>.*?</script>', '', str(input_str), flags=re.DOTALL | re.IGNORECASE)
        return clean.strip()

    @staticmethod
    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, str(email or '').strip()))

    @staticmethod
    def validate_path_traversal(base_path, target_path):
        """
        Ensures target path stays strictly inside base path (prevents path traversal attacks).
        """
        try:
            abs_base = os.path.abspath(base_path)
            abs_target = os.path.abspath(target_path)
            return abs_target.startswith(abs_base)
        except Exception:
            return False
