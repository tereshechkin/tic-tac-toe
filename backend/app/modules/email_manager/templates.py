def get_verification_code_template(code: str) -> str:
    return f"""
    <html>
    <body>
        <h1>Verification Code</h1>
        <p>Your verification code is: <strong>{code}</strong></p>
        <p>This code expires in 5 minutes.</p>
    </body>
    </html>
    """
