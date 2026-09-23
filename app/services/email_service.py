"""Serviço de e-mail (stub)."""


def send_email(to: str, subject: str, body: str) -> None:
    # TODO: integrar com SMTP / SendGrid / SES
    print(f"[email] to={to} subject={subject}")
