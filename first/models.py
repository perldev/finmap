from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


from dateutil.parser import parse
from decimal import Decimal
import pandas as pd
import hashlib 
# Create your models here.


DEBIT_CREDIT = [
       ("Доход", u"Доход"),
       ("Расход", u"Расход"),
       ("Перевод", u"Перевод"),

        ]

TRANSFER = u"Перевод"
DEBIT = "Доход"
CREDIT = "Расход"


DEBIT_CREDIT_KEYS = []
for i in DEBIT_CREDIT:
    (k, v) = i
    DEBIT_CREDIT_KEYS.append(v)



#TODO do not editable
class sources(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    upload  = models.FileField(upload_to='uploads/%Y/%m/%d/')
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="User")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    read_sheet = models.CharField(default=1, verbose_name="sheet", max_length=255)
   
    def __str__(self):
        return str(self.date) + " by " + str(self.creator)

    class Meta:
        verbose_name_plural = u"Загрузки"
        verbose_name = u"Загрузка"


def generate_key_from2(Val):
    m = hashlib.sha256()
    d = Val 
    d = d.encode('utf-8')
    m.update(d)
    return m.hexdigest()



def format_numbers_strong(D, trailing=False):
    s = "%.12f" % ( D )
    s = s[:-2]
    if trailing:
        return s.rstrip("0")
    return s

def process_transfer(obj, record):
    mapDict = {
     "date":1,
     "debit_credit":2,
     "amnt": 3, 
     "currency" :4, 
     "rate":5,
     "account":6,
     "contragent": 7,
     "to_accounts": 8,
     "to_contragent": 9,
     "project":11,
     "category":10,
     "tags":12,
     "comments":13,
    }

    recordDict = mapDict.copy()
    for i in recordDict:
        index = recordDict[i]
        if pd.isna(record[index]):
           recordDict[i] = None
        else:
           recordDict[i]= str(record[index])   

    l = [] 
    if recordDict["to_accounts"] is None:
        print(" to account is empty !!!")
        return False

    for i in ('date', 'debit_credit', 'amnt', 'currency', "account", 'contragent', 'project', "to_accounts", "to_contragent"):

       val = recordDict[i]
       if i in ('amnt', ):
          l.append(val)
       else:
          l.append(str(val))
    
    checkSum = ",".join(l)
    checkSum = generate_key_from2(checkSum)
    try:
        checkr = records.objects.get(chcksum_str=checkSum)
        print("the record is already exist")
        return False
    except records.DoesNotExist:
        pass

        #TODO add getting rate from api
    if recordDict["rate"] is None and recordDict["currency"] == u"Доллар":
       recordDict["rate"] = Decimal("28.2")

    recordDict["chcksum_str"] = checkSum
    recordDict["source"] = obj
    recordDict["creator"] = obj.creator

    project, created = projects.objects.get_or_create(name=recordDict["project"])
    if created:       
        project.creator = obj.creator
        project.save()
    recordDict["project"] = project
    
    if recordDict["contragent"]:
      contragent, created = contragents.objects.get_or_create(name=recordDict["contragent"])
      if created:       
          contragent.creator = obj.creator
          contragent.save()
      recordDict["contragent"] = contragent

    account, created = accounts.objects.get_or_create(name= recordDict["account"], currency=recordDict["currency"] )
    if created:       
        account.creator = obj.creator
        account.save()
    
    recordDict["account"] = account
    
    if recordDict["to_contragent"]:
      to_contragent, created = contragents.objects.get_or_create(name=recordDict["to_contragent"])
      if created:       
           to_contragent.creator = obj.creator
           to_contragent.save()

      recordDict["to_contragent"] = to_contragent

    
    to_account, created = accounts.objects.get_or_create(name= recordDict["to_accounts"], currency=recordDict["currency"] )
    if created:       
        to_account.creator = obj.creator
        to_account.save()

    recordDict["to_accounts"] = to_account

    result = parse(recordDict["date" ], fuzzy_with_tokens=True)
    recordDict["date"] =  result[0]
    newrecord = records(**recordDict)
    newrecord.save()
    return True


#TODO add fields checking 
@receiver(post_save, sender=sources)
def parse_excel(sender, **kwargs):
    obj = kwargs["instance"]
    path = obj.upload.path
    d = obj.read_sheet
    try:
        # try convert to int
        d = int(obj.read_sheet)
    except:
        print("ok im reading %s" % d)

    D = pd.read_excel(open(path, 'rb'),
                          sheet_name=d)  
    
    D1 = D.to_records()
    #             Дата                      Тип операции    Сумма   Валюта  Курс    Счет    Контрагент  На счет Контрагент (на счет)    Категория   Проект  Теги    Комментарий Плановая    Повторяемая
    ## ignore first on account 
    #(12088, '2022-06-02T12:10:53.003000000', 'Перевод', 2918.13, 'Гривна', nan, 'ГРН Клиенты', 'Я.Мудрого,30/Логистик Трейд Компани/Луна Трейд', 'Карта Мокрый И.', nan, 'Аренда', 'Я.Мудрого30/Аренда', nan, '06/2022', nan, nan)
    #(12089, '2022-06-02T12:12:03.997000000', 'Перевод', 2918.13, 'Гривна', nan, 'Карта Мокрый И.', nan, 'Карта Клевцова О.М.', nan, nan, 'Без проекта', nan, 'перевод аренды 06/2022 Луна Трейд', nan, nan)
    #(12090, '2022-06-02T12:12:41.003000000', 'Перевод', 2918.13, 'Гривна', nan, 'Карта Клевцова О.М.', nan, 'Карта Чайка О.Ю. КредоБанк', nan, nan, 'Без проекта', nan, 'перевод аренды 06/2022 Луна Трейд', nan, nan)
    #(12091, 'NaT', nan, 96471265.61000028, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan, nan)
     
    mapDict = {
     "date":1,
     "debit_credit":2,
     "amnt": 3, 
     "currency" :4, 
     "rate":5,
     "account":6,
     "contragent": 7,
     "project":11,
     "category":10,
     "tags":12,
     "comments":13,
    }

    #TODO add transfers
    ##TODO add messages of mistakes in excel to admin

    for record in D1:
       if pd.isna(record[mapDict["date"]]):
           print("i can process this:")
           print(record)
           continue

       if not record[mapDict["debit_credit"]] in DEBIT_CREDIT_KEYS:
           print("i can process this may be it is  transfer")
           print(record)
           if record[mapDict["debit_credit"]] == TRANSFER:
               print("seems yes")
               process_transfer(obj, record)

           continue

       recordDict = mapDict.copy()
       for i in recordDict:
           index = recordDict[i]
           if pd.isna(record[index]):
              recordDict[i] = None
           else:
              recordDict[i]= str(record[index])   

       l = [] 

       for i in ('date', 'debit_credit', 'amnt', 'currency', "account", 'contragent', 'project'):

           val = recordDict[i]
           if i in ('amnt'):
                l.append(val)
           else:
                l.append(str(val))
       
       checkSum = ",".join(l)
       checkSum = generate_key_from2(checkSum)
       try:
           checkr = records.objects.get(chcksum_str=checkSum)
           print("the record is already exist")
           continue
       except records.DoesNotExist:
           pass

       recordDict["chcksum_str"] = checkSum
       recordDict["source"] = obj
       recordDict["creator"] = obj.creator
       recordDict["debit_credit_alt"] = recordDict["debit_credit"]

       project, created = projects.objects.get_or_create(name=recordDict["project"])
       if created:       
           project.creator = obj.creator
           project.save()
       recordDict["project"] = project
       
       contragent, created = contragents.objects.get_or_create(name=recordDict["contragent"])
       if created:       
           contragent.creator = obj.creator
           contragent.save()
       recordDict["contragent"] = contragent

       account, created = accounts.objects.get_or_create(name= recordDict["account"], currency=recordDict["currency"] )
       if created:       
          account.creator = obj.creator
          account.save()
       recordDict["account"] = account
 
       result = parse(recordDict["date" ], fuzzy_with_tokens=True)
       recordDict["date"] =  result[0]
       newrecord = records(**recordDict)
       newrecord.save()


class projects_permission(models.Model):
    accounter = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ведущий проекта")
    account = models.ForeignKey('projects', on_delete=models.PROTECT, verbose_name="проект")

    class Meta:
        verbose_name_plural = u"Права на проекты"
        verbose_name = u"Право на проект"

    def __str__(self):
        return str(self.accounter) + " - " + str(self.account)


class contragents_permission(models.Model):
    accounter = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ведущий контрагент")
    account = models.ForeignKey('contragents', on_delete=models.PROTECT, verbose_name="контрагент")

    class Meta:
        verbose_name_plural = u"Права на котрагент"
        verbose_name = u"Право на контрагент"

    def __str__(self):
        return str(self.accounter) + " - " + str(self.account)


class accounts_permission(models.Model):
    accounter = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ведущий счета")
    account = models.ForeignKey('accounts', on_delete=models.PROTECT, verbose_name="cчет")

    class Meta:
        verbose_name_plural = u"Права на счета"
        verbose_name = u"Право на счет"
    
    def __str__(self):
        return str(self.accounter) + " - " + str(self.account)

#TODO calculate the balance 
class accounts(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="User", blank=True, null=True)
    currency = models.CharField(max_length=20)
    is_own = models.BooleanField(verbose_name="Наш?", default=False)

    class Meta:
        verbose_name_plural = u"Счета"
        verbose_name = u"Счет"
    
    def __str__(self):
        return str(self.name) + " by " + str(self.creator)


class contragents(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="User", blank=True, null=True)
    is_own = models.BooleanField(verbose_name="Наш?", default=False)
    
    class Meta:
        verbose_name_plural = u"Контрагент"
        verbose_name = u"Контрагенты"
    
    def __str__(self):
        return self.name


class projects(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="User", blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = u"Проекты"
        verbose_name = u"Проект"


class rates(models.Model):

    from_currency = models.CharField(max_length=255, verbose_name="из валюта")
    to_currency = models.CharField(max_length=255, verbose_name="в валюта")
    rate = models.DecimalField(max_length=255, decimal_places=10, max_digits=20, verbose_name="курс")
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name="Дата")

    @property
    def __str__(self):
        return self.from_currency + ' ' + self.to_currency + ' ' + self.rate + ' ' + self.date

    class Meta:
        verbose_name_plural = u"Курс"
        verbose_name = u"Курсы"


#TODO add normal adming
class records(models.Model):
    creator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="User")
    source = models.ForeignKey(sources, on_delete=models.PROTECT, verbose_name="Источник",
                               null=True, blank=True)
    date = models.DateField(auto_now=False, auto_now_add=False, verbose_name="Дата")
    debit_credit = models.CharField(max_length=20, choices=DEBIT_CREDIT, verbose_name="тип операции",)
    amnt = models.DecimalField(max_digits=20, decimal_places=6, verbose_name="сумма")
    currency = models.CharField(max_length=255, verbose_name="валюта")
    rate = models.DecimalField(max_digits=20, verbose_name="Курс", decimal_places=10, blank=True, null=True)
    account = models.ForeignKey(accounts, blank=False, verbose_name="Счет", on_delete=models.PROTECT )
    contragent = models.ForeignKey(contragents, blank=False, null=True , verbose_name=" Контрагент" , on_delete=models.PROTECT )
    to_accounts = models.ForeignKey("accounts", blank=True, null=True, related_name="to_accounts",  verbose_name="На Счет", on_delete=models.PROTECT )
    to_contragent = models.ForeignKey("contragents", blank=True, null=True, related_name="to_contragent", verbose_name="На Контрагент" , on_delete=models.PROTECT )
    project = models.ForeignKey(projects, blank=False, verbose_name="проект", on_delete=models.PROTECT )
    category = models.CharField(max_length=255, verbose_name="Категория", null=True, blank=True)
    tags = models.CharField(max_length=255, verbose_name="tags", null=True, blank=True)
    comments = models.CharField(max_length=255, verbose_name="Комментарий", null=True, blank=True)
    chcksum_str = models.CharField(max_length=255, verbose_name="checksum", default="", unique=True)
    last_edit = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="User", related_name="last_editor", null=True, blank=True)
    debit_credit_alt= models.CharField(max_length=20, choices=DEBIT_CREDIT, verbose_name="интерпретация операции",null=True, blank=True )

    def __str__(self):
        return self.amnt

    def get_absolute_url(self):
        return self.id
        # return reverse('name-of-view', kwargs={'pk': self.pk})

    class Meta:
        verbose_name_plural = u"Операции"
        verbose_name = u"Операция"


