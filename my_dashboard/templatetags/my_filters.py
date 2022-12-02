from django import template
register = template.Library()


def get_label(value):
    labels = {
        "date": "Дата",
        "project": "Проект",
        "debit_credit": "Тип",
        "amnt": "сумма",
        "currency": "валюта",
        "rate": "курс",
        "account": "счет",
        "contragent": "контрагент",
        "to_accounts": "на счет",
        "to_contragent": "на контрагента",
        "category": "категория",
        "tags": "теги",
        "comments": "комментарии",
        "debit_credit_alt": "интерпритация"
    }

    if value in labels:
        return labels[value]
    else:
        return value


register.filter('get_label', get_label)


