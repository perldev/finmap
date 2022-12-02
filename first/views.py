
from collections import OrderedDict
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import renderers
from rest_framework import views
from rest_framework.reverse import NoReverseMatch, reverse

import django_filters.rest_framework


from rest_framework.response import Response
from rest_framework.views import APIView
from first.models import projects, accounts, contragents, records,\
                         accounts_permission, contragents_permission, \
                         projects_permission

from fin.common import put2cache, get_fromcache

from decimal import Decimal

from my_dashboard.views import balance_acc
from fin.common import json_true, json_500false


class APIRootView(LoginRequiredMixin, views.APIView):
    template_name = "rest_framework/start_admin.html"

    _ignore_model_permissions = True
    exclude_from_schema = True
    renderer_classes = [renderers.TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        whole_balance_acc = get_fromcache("balances")
        if whole_balance_acc is None:
            whole_balance_acc = balance_acc()
            put2cache("balances", whole_balance_acc)

        accs = []
        if self.request.user.is_superuser:
            accs = accounts.objects.all()
        else:
            accs = [i.account for i in accounts_permission.objects.filter(accounter_id=self.request.user.id)]

        accs_res = []

        for i in accs:
            accs_res.append({"account": i, "balance": whole_balance_acc["result"]["info"][i.name]})

        return Response({"accounts": accs_res})


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = projects
        fields = ["name"]


class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = accounts
        fields = ["name"]


class ContragentSerializer(serializers.ModelSerializer):
    class Meta:
        model = contragents
        fields = ["name"]


#TODO hierartical permission on account with cache
class PermissionRelatedField(serializers.RelatedField):

    def __init__(self, *arg, **kwargs):
        self.model4looking = kwargs.pop("model")
        self.model4permission = kwargs.pop("permission_model")
        super().__init__(*arg, **kwargs)

    def get_queryset(self, *args, **kwargs):
        model_permission = self.model4permission
        model = self.model4looking
        usr = self.context["request"].user

        if not usr.is_superuser:
            ids_for = [i.account_id for i in
                       model_permission.objects.filter(accounter_id=usr.id)]
            return model.objects.filter(id__in=ids_for)
        else:
            return model.objects.all()

    def to_representation(self, value):
        return str(value)


class RecordSerializer(serializers.ModelSerializer):

    account = PermissionRelatedField(many=False,
                                     label="Счет",
                                     model=accounts,
                                     permission_model=accounts_permission)

    project = PermissionRelatedField(many=False,
                                     label="Проект",
                                     model=projects,
                                     permission_model=projects_permission)

    contragent = PermissionRelatedField(many=False,
                                        label="Контрагент",
                                        model=contragents,
                                        permission_model=contragents_permission)

    class Meta:
        model = records
        fields = ["date", "project", "debit_credit", "amnt", "currency", "rate", "account", "contragent",
                  "to_accounts", "to_contragent", "category", "tags", "comments", "debit_credit_alt"]


"""
    project = serializers.RelatedField(
        many=False,
        queryset=projects.objects.all(), label="Проект", )

    account = serializers.RelatedField(
        many=False,
        queryset=accounts.objects.all(),
        label="счет", )

    contragent = serializers.RelatedField(
        many=False,
        queryset=contragents.objects.all(),
        label="контрагент", )

    to_accounts = serializers.RelatedField(
        many=False,
        queryset=accounts.objects.all(),
        label="на счет", allow_null=True)

    to_contragent = serializers.RelatedField(
        many=False,
        queryset=contragents.objects.all(),
        label="на контрагента", allow_null=True)
"""


class RecordDetail(LoginRequiredMixin, APIView):

    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'record_detail.html'

    def get(self, request, pk):
        print("here")
        record = get_object_or_404(records, pk=pk)
        serializer = RecordSerializer(record)
        return Response({'serializer': serializer, 'record': record})

    def post(self, request, pk):
        record = get_object_or_404(records, pk=pk)
        serializer = RecordSerializer(record, data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'record': record})
        serializer.save()
        return json_true(request, {})


class RecordSerializerOperator(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(
         many=False,
         queryset=projects.objects.all(),
         slug_field='name',
        label="Проект", )

    account = serializers.SlugRelatedField(
        many=False,
        queryset=accounts.objects.all(),
        slug_field='name',
        label="счет", )

    contragent = serializers.SlugRelatedField(
        many=False,
        queryset=contragents.objects.all(),
        slug_field='name',
        label="контрагент", )

    to_accounts = serializers.SlugRelatedField(
        many=False,
        queryset=accounts.objects.all(),
        slug_field='name',
        label="на счет",
        allow_null=True)

    to_contragent = serializers.SlugRelatedField(
        many=False,
        queryset=contragents.objects.all(),
        slug_field='name',
        label="на контрагента",
        allow_null=True)

    class Meta:
        model = records
        fields = ["date", "project", "debit_credit", "amnt", "currency", "rate", "account", "contragent",
                  "to_accounts", "to_contragent", "category", "tags", "comments", "debit_credit_alt", "url"]


class ContragentsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):

    """
       Контрагенты
    """
    serializer_class = ContragentSerializer
    renderer_classes = [renderers.AdminRenderer]

    def perform_create(self, serializer):
        instance = serializer.save()
        perm = contragents_permission(accounter=self.request.user, account_id=instance.id)
        perm.save()
        perm.save()

    def get_queryset(self):
        accounts_for = [i.account_id for i in contragents_permission.objects.filter(accounter=self.request.user)]
        queryset = contragents.objects.filter(id__in=accounts_for)
        return queryset

    queryset = contragents.objects.all()

    permission_classes = [permissions.IsAuthenticated]


class RecordViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        Операции со счетами
    """
    serializer_class = RecordSerializer

    #TODO add caching for this operation
    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        res_q = self.filter_queryset(query)
        print(res_q.query)
        serdata = RecordSerializerOperator(res_q, many=True, context={'request': request})
        return Response(serdata.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def retrieve(self, request, pk=None):
        accounts_for = [i.account.id for i in accounts_permission.objects.filter(accounter=self.request.user)]
        queryset = records.objects.filter(Q(Q(account__in=accounts_for) | Q(to_accounts__in=accounts_for)))
        item = get_object_or_404(queryset, pk=pk)
        serializer = RecordSerializerOperator(item)
        return Response(serializer.data)

    renderer_classes = [renderers.AdminRenderer]
    #filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["date", "project", "debit_credit",
                        "amnt", "currency", "rate",
                        "account", "contragent",
                        "to_accounts", "to_contragent",
                        "category", "tags",
                        "comments", "debit_credit_alt"]

    queryset = records.objects.all().order_by('-date')
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        instance = serializer.save(last_edit=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, last_edit=self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return records.objects.all().order_by("-date")

        else:
            accounts_for = [i.account.id for i in accounts_permission.objects.filter(accounter=self.request.user)]
            return records.objects.filter(Q(Q(account__in=accounts_for)|Q(to_accounts__in=accounts_for))).order_by("-date")

    def get_permissions(self):
        """
           Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]


