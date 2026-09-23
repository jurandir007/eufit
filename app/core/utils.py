"""Funções utilitárias genéricas."""


def slugify(text: str) -> str:
    return (
        text.lower()
        .strip()
        .replace(" ", "-")
        .replace("_", "-")
    )
