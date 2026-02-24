from __future__ import annotations

import typer

from chatboteval.api import get_version

app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Print the installed chatboteval version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        typer.echo(get_version())
        raise typer.Exit(code=0)