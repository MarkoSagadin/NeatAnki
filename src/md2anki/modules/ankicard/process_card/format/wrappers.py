import logging

logger = logging.getLogger(__name__)


def wrap_tab_group(
    tab_content: str,
) -> str:
    return f'<section class="tab_group">{tab_content}</section>'


def wrap_tab(tab_label: str, tab_body: str) -> str:
    return f'<section class="tab">{tab_label}{tab_body}</section>'


def wrap_tab_label(label: str) -> str:
    return f'<button class="tab__label"><span>{label.strip()}</span></button>'


def wrap_tab_body(body: str) -> str:
    return f'<div class="tab__body"><div class="tab__body__content">{body}</div></div>'


def wrap_card_body(body: str) -> str:
    return f'<div class="card-body"><div class="card-body__content">{body}</div></div>'
