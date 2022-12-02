
from django.shortcuts import render
from django.contrib.auth import authenticate, logout


from first.models import records, projects, accounts, contragents, accounts_permission, DEBIT, CREDIT, TRANSFER, rates

from django.shortcuts import redirect
import django_filters.rest_framework
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from fin.common import json_true, json_500false
from django.forms.models import model_to_dict
# Create your views here:.
from django.db.models import Sum
from decimal import Decimal
import uuid
from datetime import datetime, timedelta as dt
from fin.common import put2cache, get_fromcache
from django.contrib.auth.decorators import login_required


def account_index(req):
    return render(req, "start.html", {})

@login_required
def main(request):
    if not request.user.is_superuser:
        return redirect("/our_accounts/")

    incs = {}
    decs = {}

    calculate_accounts = request.GET.get("accounts", "yes")
    calculate_contragents = request.GET.get("contragents", "yes")

    nw = datetime.now()
    nw7 = nw - dt(days=7)
    nw90 = nw - dt(days=90)
    # return this {"result": {"info": accounts_dict, "recs": accounts_recs}}


    result_info_fist = {"base_currency": "UAH"}
    whole_balance_prj = balance_prj()
    whole_balance_acc = balance_acc()
    put2cache("balances", whole_balance_acc)


    acc_source = whole_balance_acc["result"]["source"]
    whole_balance_prj7 = balance_prj(nw7)
    whole_balance_acc7 = balance_acc(nw7)

    whole_balance_prj90 = balance_prj(nw90)
    whole_balance_acc90 = balance_acc(nw90)

    saldo = Decimal("0.0")
    saldo7 = Decimal("0.0")
    saldo90 = Decimal("0.0")
    accinfo = whole_balance_acc["result"]["info"]

    main_projects_recs = []
    main_accounts_recs = []

    for i in accinfo.keys():
        saldo += accinfo[i]
        main_accounts_recs.append({"balance": accinfo[i], "account": acc_source[i]})

    accinfo = whole_balance_acc7["result"]["info"]
    for i in accinfo.keys():
        saldo7 += accinfo[i]

    accinfo = whole_balance_acc90["result"]["info"]
    for i in accinfo.keys():
        saldo90 += accinfo[i]

    accinfo = whole_balance_prj["result"]["info"]
    for i in accinfo.keys():
        main_projects_recs.append({"name": i, "balance": accinfo[i]})

    result_info_fist["whole_balance"] = saldo
    result_info_fist["whole_saldo7"] = saldo7
    result_info_fist["whole_saldo90"] = saldo90
    result_info_fist["main_projects"] = main_projects_recs
    result_info_fist["main_accounts"] = main_accounts_recs
    print(result_info_fist["whole_balance"])


    projects_d = {}
    contragents_d = {}
    accounts_d = {}

    for i in projects.objects.all():
        projects_d[i.id] = i.name
        projects_d[i.name] = i.id

    for i in accounts.objects.all():
        accounts_d[i.id] = i.name
        accounts_d[i.name] = i.id

    for i in contragents.objects.all():
        contragents_d[i.id] = i.name
        contragents_d[i.name] = i.id

    total = {}
    decs = {}
    ins_acc = {}
    decs_acc = {}

    if calculate_contragents == "yes":
        for i in records.objects.filter(debit_credit_alt=DEBIT,
                                        currency="Гривна").values("project", "contragent").annotate(total=Sum("amnt")):

            nm = projects_d[i["project"]]
            nmc = contragents_d[i["contragent"]]

            if not nm in incs:
                incs[nm] = {}

            if not nmc in incs[nm]:
                incs[nm][nmc] = Decimal("0")

            if not nm in total:
                total[nm] = {}

            if not nmc in total[nm]:
                total[nm][nmc] = Decimal("0")

            total[nm][nmc] += i["total"]
            incs[nm][nmc] += i["total"]

        for i in records.objects.filter(debit_credit_alt=CREDIT,
                                        currency="Гривна").values("project", "contragent").annotate(total=Sum("amnt")):

            nm = projects_d[i["project"]]
            nmc = contragents_d[i["contragent"]]

            if not nm in decs:
                decs[nm] = {}

            if not nmc in decs[nm]:
                decs[nm][nmc] = Decimal("0")

            if not nm in total:
                total[nm] = {}

            if not nmc in total[nm]:
                total[nm][nmc] = Decimal("0")

            decs[nm][nmc] += i["total"]
            total[nm][nmc] += i["total"]

    if calculate_accounts == "yes":

        for i in records.objects.filter(debit_credit_alt=DEBIT,
                                        currency="Гривна").values("project", "account").annotate(total=Sum("amnt")):

            nm = projects_d[i["project"]]
            nmc = accounts_d[i["account"]]

            if not nm in ins_acc:
                ins_acc[nm] = {}

            if not nmc in ins_acc[nm]:
                ins_acc[nm][nmc] = Decimal("0")

            if not nm in total:
                total[nm] = {}

            if not nmc in total[nm]:
                total[nm][nmc] = Decimal("0")

            total[nm][nmc] += i["total"]
            ins_acc[nm][nmc] += i["total"]

        for i in records.objects.filter(debit_credit_alt=CREDIT,
                                        currency="Гривна").values("project", "account").annotate(total=Sum("amnt")):

            nm = projects_d[i["project"]]
            nmc = accounts_d[i["account"]]

            if not nm in decs_acc:
                decs_acc[nm] = {}

            if not nmc in decs_acc[nm]:
                decs_acc[nm][nmc] = Decimal("0")

            if not nm in total:
                total[nm] = {}

            if not nmc in total[nm]:
                total[nm][nmc] = Decimal("0")

            total[nm][nmc] += i["total"]
            decs_acc[nm][nmc] += i["total"]

    #TODO  recheck and analyze
    for i in records.objects.filter(debit_credit_alt=TRANSFER):
        if i.amnt and 1:
            pass

    total_arr = []
    for project in total.keys():
        total_circ = []
        for k in total[project].keys():
            v = total[project][k]
            total_circ.append(
                {"name": k, "value": v / 1000, "contragent": k in contragents_d, "account": k in accounts_d})

        total_arr.append({"project": project, "data": total_circ})

    result_info = {"incs": incs,
                  "decs": decs,
                  "total": total,
                  "projects": projects_d,
                  "accounts": accounts_d,
                  "accounts_included": calculate_accounts == "yes",
                  "contragents_included": calculate_contragents == "yes",
                  "contragents": contragents_d,
                  "total_arr": total_arr,
                  "decs_acc": decs_acc, "ins_acc": ins_acc}

    return render(request, "index.html", {**result_info, **result_info_fist})


def record_edit(req, record_id, name):
    pr = None
    try:
        pr = records.objects.get(id=record_id)
        pr.__dict__[name] = req.POST.get("data", "")
        pr.save(update_fields=[name])
    except records.DoesNotExist:
        return json_500false(req, {"msg": "records is not exist"})

    return json_true(req, {"msg": "record has been edited"})


def trans(req):

    dd = req.POST.get("date", None)
    category = req.POST.get("category", None)
    context = req.POST.get("context", None)
    q = None

    if context == "account":
        q = Q(Q(account__name=category)|Q(to_accounts__name=category))

    if context == "project":
        q = Q(project__name=category)

    if context == "contragent":
        q = Q(Q(contragent__name=category)|Q(to_contragent__name=category))

    if dd is not None and q is not None:
        q = q & Q(date__gte=dd)
    elif dd is not None and q is None:
        q = Q(date__gte=dd)

    if q is None:
        return json_500false(req, {"msg": "can't list all"})

    query = records.objects.filter(q)
    arr = []
    for i in query:
        item = local_model_to_dict(i)
        arr.append(item)

    arr1 = sorted(arr, key=lambda a: a["date"])
    return json_true(req, {"data": arr1})


def trans_context(req):
    project = req.POST.get("project", "")
    category = req.POST.get("category", "")
    context = req.POST.get("context", "")
    pr = None
    (q, q1, q2) = (None, None, None)
    try:
        pr = projects.objects.get(name=project)
    except projects.DoesNotExist:
        return json_500false(req, {"msg": "project does not exist"})

    if context == "account":
        try:
            # acc = accounts.objects.get(name=category)
            q = records.objects.filter(project=pr, account__name=category, debit_credit_alt__in=[DEBIT, CREDIT])
            q1 = records.objects.filter(project=pr, account__name=category, debit_credit_alt__in=[TRANSFER])
            q2 = records.objects.filter(project=pr, to_accounts__name=category, debit_credit_alt__in=[TRANSFER])
        except accounts.DoesNotExist:
            return json_500false(req, {"msg": "accounts does not exist"})

    if context == "contragent":
        try:
            # acc = contragents.objects.get(name=category)
            q = records.objects.filter(project=pr, contragent__name=category, debit_credit_alt__in=[DEBIT, CREDIT])
            q1 = records.objects.filter(project=pr, contragent__name=category, debit_credit_alt=TRANSFER)
            q2 = records.objects.filter(project=pr, to_contragent__name=category, debit_credit_alt=TRANSFER)
        except accounts.DoesNotExist:
            return json_500false(req, {"msg": "accounts does not exist"})

    arr = []
    for i in q1:
        item = local_model_to_dict(i)
        arr.append(item)

    for i in q2:
        item = local_model_to_dict(i)
        arr.append(item)

    for i in q:
        item = local_model_to_dict(i)
        arr.append(item)

    arr1 = sorted(arr, key=lambda a: a["date"])

    return json_true(req, {"data": arr1})


def project_info(req):
    pr = req.POST.get("project", None)
    uid_q = str(uuid.uuid4())
    try:
        pr = projects.objects.get(name=pr)
        q = records.objects.filter(project=pr, debit_credit_alt__in=[DEBIT, CREDIT, TRANSFER])
        put2cache(q, uid_q)
    except accounts.DoesNotExist:
        return json_500false(req, {"msg": "project does not exist"})

    arr = []
    common_income = {"debit": Decimal("0.0"), "debits": [],
                     "credit": Decimal("0.0"), "credits": [],
                     "debit_q_id": uid_q,
                     "credit_q_id": uid_q
                     }
    common_income_debit = {}
    common_income_credit = {}
    common_income_debit_acc = {}
    common_income_credit_acc = {}

    for i in q:
        item = local_model_to_dict(i)
        arr.append(item)

        if i.debit_credit_alt in (CREDIT, TRANSFER):
            common_income["credit"] += i.amnt
            common_income["credits"].append(item)

            tmp = common_income_credit
            tmp1 = common_income_credit_acc
            if not i.account.name in tmp1:
                tmp1[i.account.name] = {"amnt": Decimal("0.0"), "recs": []}
                tmp1[i.account.name]["amnt"] += i.amnt
                tmp1[i.account.name]["recs"].append(item)

            if not i.contragent.name in tmp:
                tmp[i.contragent.name] = {"amnt": Decimal("0.0"), "recs": []}

            tmp[i.contragent.name]["amnt"] += i.amnt
            tmp[i.contragent.name]["recs"].append(item)

        if i.debit_credit_alt == DEBIT:
            common_income["debit"] += i.amnt
            common_income["debits"].append(item)

            tmp = common_income_debit
            tmp1 = common_income_debit_acc

            if not i.account.name in tmp1:
                tmp1[i.account.name] = {"amnt": Decimal("0.0"), "recs": []}
                tmp1[i.account.name]["amnt"] += i.amnt
                tmp1[i.account.name]["recs"].append(item)

            if not i.contragent.name in tmp:
                tmp[i.contragent.name] = {"amnt": Decimal("0.0"), "recs": []}

            tmp[i.contragent.name]["amnt"] += i.amnt
            tmp[i.contragent.name]["recs"].append(item)

    common_income["account_debit"] = common_income_debit_acc
    common_income["account_credit"] = common_income_credit_acc
    common_income["contragent_debit"] = common_income_debit
    common_income["contragent_credit"] = common_income_credit

    return json_true(req, common_income)


def logout_context(request):
    logout(request)
    return redirect("/")


def rate(date, amnt, currency, base, source=None):
    if currency == base:
        return amnt

    if source and source.rate is not None:
        return amnt*source.rate

    try:
        obj = rates.objects.get(from_currency=currency,
                                to_currency=base,
                                date=date)
        return amnt * obj.rate

    except rates.DoesNotExist:
        obj = rates.objects.filter(from_currency=currency,
                                   to_currency=base,
                                   date__lt=date).first()

        return amnt * obj.rate


def trans_q(req, **kwargs):
    kwargs["q_id"]
    pass


def balance_acc(dd=None, base_currency=u"Гривна"):
    q = None
    if dd is None:
        q = records.objects.all()
    else:
        q = records.objects.filter(date__gte=dd)

    accounts_dict = {}
    accounts_recs = {}
    accounts_source = {}

    for i in q:
        if i.account.name not in accounts_dict:
            accounts_dict[i.account.name] = Decimal("0.0")
            accounts_recs[i.account.name] = []
            accounts_source[i.account.name] = i.account

        if i.debit_credit in (DEBIT, ):
            accounts_dict[i.account.name] += rate(i.date, i.amnt, i.currency, base_currency, i)
            accounts_recs[i.account.name].append(model_to_dict(i))

        if i.debit_credit in (CREDIT, ):
            accounts_dict[i.account.name] -= rate(i.date, i.amnt, i.currency, base_currency, i)
            accounts_recs[i.account.name].append(model_to_dict(i))

        if i.debit_credit in (TRANSFER, ):
            accounts_dict[i.account.name] -= rate(i.date, i.amnt, i.currency, base_currency, i)
            accounts_recs[i.account.name].append(model_to_dict(i))

            if i.to_accounts.name not in accounts_dict:
                accounts_dict[i.to_accounts.name] = Decimal("0.0")
                accounts_recs[i.to_accounts.name] = []
                accounts_source[i.to_accounts.name] = i.to_accounts

            accounts_recs[i.to_accounts.name].append(model_to_dict(i))
            accounts_dict[i.to_accounts.name] += rate(i.date, i.amnt, i.currency, base_currency, i)

    result = {"result": {"info": accounts_dict, "recs": accounts_recs, "source": accounts_source}}
    return result


def balance_prj(dd=None, base_currency=u"Гривна"):
    q = None
    if dd is None:
        q = records.objects.all()
    else:
        q = records.objects.filter(date__gte=dd)

    projects_dict = {}
    projects_recs = {}
    for i in q:
        if i.project.name not in projects_dict:
            projects_dict[i.project.name] = Decimal("0.0")
            projects_recs[i.project.name] = []

        if i.debit_credit in (DEBIT, ):
            projects_dict[i.project.name] += rate(i.date, i.amnt, i.currency, base_currency, i)
            projects_recs[i.project.name].append(model_to_dict(i))

        if i.debit_credit in (CREDIT, ):
            projects_dict[i.project.name] -= rate(i.date, i.amnt, i.currency, base_currency, i)
            projects_recs[i.project.name].append(model_to_dict(i))

        if i.debit_credit in (TRANSFER, ):
            projects_dict[i.project.name] -= rate(i.date, i.amnt, i.currency, base_currency, i)
            projects_recs[i.project.name].append(model_to_dict(i))

    return {"result": {"info": projects_dict, "recs": projects_recs}}


# showing the whole context of
# TODO add filtering by project
def show_account_map(req):
    ##TODO calculte balance
    category = req.POST.get("category", "")
    project = req.POST.get("project", "")
    context = req.POST.get("context", "contragent")
    exclude = req.POST.get("exclude", [])
    q = records.objects.filter(Q(Q(account__name=category) | Q(to_accounts__name=category)) & Q(project__name=project))

    q_u_d = str(uuid.uuid4())
    q_u_c = str(uuid.uuid4())

    put2cache(q, q_u_c)
    put2cache(q, q_u_d)

    common_income = {"debit": Decimal("0.0"),
                     "credit": Decimal("0.0"),
                     "credits": {},
                     "credit_q_id": q_u_c,
                     "debit_q_id": q_u_d, "debits": {}}

    for item in q:
        i = local_model_to_dict(item)
        name = None

        if item.contragent:
            name = item.contragent.name

        #TODO add exception when the contragent is empty
        if item.debit_credit in [TRANSFER]:
            if not item.to_contragent:
                if not item.to_accounts:
                    print("unrecognized data ")
                    print(i)
                    continue
                else:
                    name = item.to_accounts.name
            else:
                name = item.to_contragent.name

        if item.debit_credit in [DEBIT]:
            if name not in common_income["debits"]:
                common_income["debits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["debits"][name]["amnt"] += item.amnt
            common_income["debits"][name]["recs"].append(i)

        if item.debit_credit in [CREDIT]:
            if name not in common_income["credits"]:
                common_income["credits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["credits"][name]["amnt"] += item.amnt
            common_income["credits"][name]["recs"].append(i)

        if item.debit_credit in [TRANSFER] and item.account.name == category:
            if name not in common_income["credits"]:
                common_income["credits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["credits"][name]["amnt"] += item.amnt
            common_income["credits"][name]["recs"].append(i)

        if item.debit_credit in [TRANSFER] and item.to_accounts.name == category:
            name = item.contragent.name
            if name not in common_income["debits"]:
                common_income["debits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["debits"][name]["amnt"] += item.amnt
            common_income["debits"][name]["recs"].append(i)

    common_income["categories"] = list(
        set(list(common_income["debits"].keys()) + list(common_income["credits"].keys())))

    return json_true(req, common_income)

#TODO
def show_contragent_map(req):
    category = req.POST.get("category", "")
    context = req.POST.get("context", "contragent")
    project = req.POST.get("project", "")

    exclude = req.POST.get("exclude", [])
    q = records.objects.filter(Q(Q(to_contragent__name=category) | Q(contragent__name=category))&Q(project__name=project))
    common_income = {"debit": Decimal("0.0"), "debits": [], "credit": Decimal("0.0"), "credits": {}, "debits": {}}

    for item in q:
        i = local_model_to_dict(item)
        name = None
        #TODO add exception when the account is empty
        if item.account and item.contragent.name == category:
            name = item.account.name

        if item.debit_credit in [DEBIT]:
            if name not in common_income["debits"]:
                common_income["debits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["debits"][name]["amnt"] += item.amnt
            common_income["debits"][name]["recs"].append(i)

        if item.debit_credit in [CREDIT]:
            if name not in common_income["credits"]:
                common_income["credits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["credits"][name]["amnt"] += item.amnt
            common_income["credits"][name]["recs"].append(i)

        if item.debit_credit in [TRANSFER] and item.contragent.name == category:
            if name not in common_income["credits"]:
                common_income["credits"][name] = {"amnt": Decimal("0.0"), "recs": []}

            common_income["credits"][name]["amnt"] += item.amnt
            common_income["credits"][name]["recs"].append(i)

        if item.debit_credit in [TRANSFER] and item.to_contragent == category:
            name = item.to_accounts.name
            if name not in common_income["debits"]:
                common_income["debits"][name] = {"amnt": Decimal("0.0"),
                                                 "recs": []}

            common_income["debits"][name]["amnt"] += item.amnt
            common_income["debits"][name]["recs"].append(i)

    common_income["categories"] = list(
        set(list(common_income["debits"].keys()) + list(common_income["credits"].keys())))
    return json_true(req, common_income)


# TODO estimating  the size of project
def common_info(req):
    project = req.POST.get("project", "")
    category = req.POST.get("category", "")
    context = req.POST.get("context", "")
    pr = None
    (q, q1, q2) = (None, None, None)

    try:
        pr = projects.objects.get(name=project)
    except projects.DoesNotExist:
        return json_500false(req, {"msg": "project does not exist"})

    if context == "account":
        try:
            # acc = accounts.objects.get(name=category)
            q = records.objects.filter(project=pr, account__name=category, debit_credit_alt__in=[DEBIT,
                                                                                                 CREDIT, TRANSFER])
        except accounts.DoesNotExist:
            return json_500false(req, {"msg": "accounts does not exist"})

    if context == "contragent":
        try:
            # acc = contragents.objects.get(name=category)
            q = records.objects.filter(project=pr, contragent__name=category, debit_credit_alt__in=[DEBIT,
                                                                                                    CREDIT, TRANSFER])
        except accounts.DoesNotExist:
            return json_500false(req, {"msg": "accounts does not exist"})

    arr = []
    common_income = {"debit": Decimal("0.0"), "debits": [], "credit": Decimal("0.0"), "credits": []}
    common_income_debit = {}
    common_income_credit = {}

    for i in q:
        item = local_model_to_dict(i)
        arr.append(item)

        if i.debit_credit_alt in (CREDIT, TRANSFER):

            common_income["credit"] += i.amnt
            common_income["credits"].append(item)

            tmp = common_income_credit
            if context == "contragent":
                if not i.account.name in tmp:
                    tmp[i.account.name] = {"amnt": Decimal("0.0"), "recs": []}

                tmp[i.account.name]["amnt"] += i.amnt
                tmp[i.account.name]["recs"].append(item)

            else:
                if not i.contragent.name in tmp:
                    tmp[i.contragent.name] = {"amnt": Decimal("0.0"), "recs": []}

                tmp[i.contragent.name]["amnt"] += i.amnt
                tmp[i.contragent.name]["recs"].append(item)

        if i.debit_credit_alt == DEBIT:

            common_income["debit"] += i.amnt
            common_income["debits"].append(item)

            tmp = common_income_debit
            if context == "contragent":
                if not i.account.name in tmp:
                    tmp[i.account.name] = {"amnt": Decimal("0.0"), "recs": []}

                tmp[i.account.name]["amnt"] += i.amnt
                tmp[i.account.name]["recs"].append(item)

            else:
                if not i.contragent.name in tmp:
                    tmp[i.contragent.name] = {"amnt": Decimal("0.0"), "recs": []}

                tmp[i.contragent.name]["amnt"] += i.amnt
                tmp[i.contragent.name]["recs"].append(item)

    if context == "contragent":
        common_income["context"] = "account"
    else:
        common_income["context"] = "contragent"

    common_income["common_income_debit"] = common_income_debit
    common_income["common_income_credit"] = common_income_credit
    common_income["records"] = arr
    return json_true(req, common_income)


def local_model_to_dict(i):
    item = model_to_dict(i)
    if i.account:
        item["account"] = i.account.name

    if i.to_accounts:
        item["to_accounts"] = i.to_accounts.name

    if i.contragent:
        item["contragent"] = i.contragent.name

    if i.to_contragent:
        item["to_contragent"] = i.to_contragent.name

    if i.project:
        item["project"] = i.project.name

    if i.last_edit:
        item["last_edit"] = i.last_edit.username

    if i.creator:
        item["creator"] = i.creator.username

    return item
