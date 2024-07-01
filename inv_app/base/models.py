from django.db import models
from django.contrib.auth.models import User

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    TYPE_CHOICES = (
        ('stock', 'Stock'),
        ('crypto', 'Cryptocurrency'),
        ('bond', 'Bond'),
        ('fund', 'Fund')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,default='stock')
    ticker = models.CharField(max_length=20,default='')
    name = models.CharField(max_length=15,default='')
    amount = models.DecimalField(max_digits=20, decimal_places=8,default=0)
    buy_price = models.DecimalField(max_digits=20, decimal_places=8,default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.ticker}"

class Crypto(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=15)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=100, decimal_places=50)
    volume_24h = models.DecimalField(max_digits=100, decimal_places=50)
    market_cap = models.DecimalField(max_digits=100, decimal_places=50)

class Stock(models.Model):
    ticker= models.CharField(primary_key=True,max_length=20,default='')
    name = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=100, decimal_places=50)
    volume_24h = models.DecimalField(max_digits=100, decimal_places=50)
    market_cap = models.DecimalField(max_digits=100, decimal_places=50)

class Bond(models.Model):
    ticker= models.CharField(primary_key=True,max_length=20,default='')
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=100, decimal_places=50)
    volume_24h = models.DecimalField(max_digits=100, decimal_places=50)
    issue_size = models.DecimalField(max_digits=100, decimal_places=50)

class Fund(models.Model):
    ticker= models.CharField(primary_key=True,max_length=20,default='')
    name = models.CharField(max_length=25)
    price = models.DecimalField(max_digits=100, decimal_places=50)
    volume_24h = models.DecimalField(max_digits=100, decimal_places=50)
    market_cap = models.DecimalField(max_digits=100, decimal_places=50)

class History(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=30,default='')
    price = models.DecimalField(max_digits=100, decimal_places=50,default=0)
    ticker_or_symbol= models.CharField(max_length=10,default='')
    TYPE_CHOICES = (
        ('stock', 'Stock'),
        ('crypto', 'Cryptocurrency'),
        ('bond', 'Bond'),
        ('fund', 'Fund')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,default='stock')
    Buy_sell = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )
    action = models.CharField(max_length=10, choices=Buy_sell,default='buy')
    amount = models.DecimalField(max_digits=20, decimal_places=8,default=0)
    purchase_date = models.DateTimeField()