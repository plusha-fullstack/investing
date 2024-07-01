from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.utils import timezone
from .models import Portfolio, Stock, Crypto, Bond, Fund, History
from .forms import PortfolioForm
import json

@login_required
def home(request):
    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio_item = form.save(commit=False)
            portfolio_item.user = request.user
            day_of_deal = form.cleaned_data.get('day_of_deal')
            # Fetch the name from the appropriate model based on the type
            try:
                if portfolio_item.type == 'stock':
                    stock = Stock.objects.get(ticker=portfolio_item.ticker)
                    portfolio_item.name = stock.name
                elif portfolio_item.type == 'crypto':
                    crypto = Crypto.objects.get(symbol=portfolio_item.ticker)
                    portfolio_item.name = crypto.name
                elif portfolio_item.type == 'bond':
                    bond = Bond.objects.get(ticker=portfolio_item.ticker)
                    portfolio_item.name = bond.name
                elif portfolio_item.type == 'fund':
                    fund = Fund.objects.get(ticker=portfolio_item.ticker)
                    portfolio_item.name = fund.name
            except (Stock.DoesNotExist, Crypto.DoesNotExist, Bond.DoesNotExist, Fund.DoesNotExist):
                form.add_error('ticker', 'Invalid ticker for selected type.')
                return render(request, "home.html", {"form": form})

            existing_item = Portfolio.objects.filter(user=request.user, type=portfolio_item.type, ticker=portfolio_item.ticker).first()
            if existing_item:
                total_amount = existing_item.amount + portfolio_item.amount
                total_cost = (existing_item.amount * existing_item.buy_price) + (portfolio_item.amount * portfolio_item.buy_price)
                new_buy_price = total_cost / total_amount

                existing_item.amount = total_amount
                existing_item.buy_price = new_buy_price
                existing_item.purchase_date = portfolio_item.purchase_date
                existing_item.save()
            else:
                portfolio_item.save()

            History.objects.create(
                user=request.user,
                ticker_or_symbol=portfolio_item.ticker,
                type=portfolio_item.type,
                action='buy',
                amount=portfolio_item.amount,
                price=portfolio_item.buy_price,
                purchase_date=day_of_deal
            )

            return redirect("base:home")
    else:
        form = PortfolioForm()

    # Fetch user's portfolio
    portfolio_items = Portfolio.objects.filter(user=request.user)
    portfolio_data = []

    for item in portfolio_items:
        data = {
            "pk": item.pk,
            "type": item.type,
            "ticker": item.ticker,
            "name": item.name,
            "buy_price": item.buy_price,
            "amount": item.amount,
            "current_price": 0,
            "volume_24h": 0,
            "market_cap_or_issue_size": 0,
            "change": 0
        }
        if item.type == 'stock':
            stock = Stock.objects.get(ticker=item.ticker)
            data["current_price"] = stock.price
            data["volume_24h"] = stock.volume_24h
            data["market_cap_or_issue_size"] = stock.market_cap
        elif item.type == 'crypto':
            crypto = Crypto.objects.get(symbol=item.ticker)
            data["current_price"] = crypto.price
            data["volume_24h"] = crypto.volume_24h
            data["market_cap_or_issue_size"] = crypto.market_cap
        elif item.type == 'bond':
            bond = Bond.objects.get(ticker=item.ticker)
            data["current_price"] = bond.price
            data["volume_24h"] = bond.volume_24h
            data["market_cap_or_issue_size"] = bond.issue_size
        elif item.type == 'fund':
            fund = Fund.objects.get(ticker=item.ticker)
            data["current_price"] = fund.price
            data["volume_24h"] = fund.volume_24h
            data["market_cap_or_issue_size"] = fund.market_cap

        data["change"] = ((data["current_price"] - item.buy_price) / item.buy_price) * 100
        portfolio_data.append(data)

    return render(request, "home.html", {"form": form, "portfolio_data": portfolio_data})

@login_required
def history(request):
    if request.method == "POST" and 'delete_history' in request.POST:
        History.objects.filter(user=request.user).delete()
        return redirect('base:history')

    history_items = History.objects.filter(user=request.user)
    return render(request, "history.html", {"history_items": history_items})

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect("base:login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def delete_portfolio_item(request, pk):
    item = Portfolio.objects.get(pk=pk, user=request.user)

    # Get the current price from the appropriate model based on the type
    current_price = 0
    if item.type == 'stock':
        stock = Stock.objects.get(ticker=item.ticker)
        current_price = stock.price
    elif item.type == 'crypto':
        crypto = Crypto.objects.get(symbol=item.ticker)
        current_price = crypto.price
    elif item.type == 'bond':
        bond = Bond.objects.get(ticker=item.ticker)
        current_price = bond.price
    elif item.type == 'fund':
        fund = Fund.objects.get(ticker=item.ticker)
        current_price = fund.price

    # Add history record
    History.objects.create(
        user=request.user,
        ticker_or_symbol=item.ticker,
        type=item.type,
        action='sell',
        amount=item.amount,
        price=current_price,
        purchase_date=timezone.now()
    )

    item.delete()
    return redirect("base:home")

@login_required
def delete_history(request):
    History.objects.filter(user=request.user).delete()
    return redirect('base:history')


@login_required
def analyze(request):
    user = request.user
    portfolios = Portfolio.objects.filter(user=user)

    total_value = 0
    asset_allocation = {'Stock': 0, 'Cryptocurrency': 0, 'Bond': 0, 'Fund': 0}
    portfolio_data = []
    stock_data = {}
    crypto_data = {}
    bond_data = {}
    fund_data = {}
    stock_allocation = 0
    crypto_allocation = 0
    bond_allocation = 0
    fund_allocation = 0

    for portfolio in portfolios:
        if portfolio.type == 'stock':
            asset = Stock.objects.get(ticker=portfolio.ticker)
        elif portfolio.type == 'crypto':
            asset = Crypto.objects.get(symbol=portfolio.ticker)
        elif portfolio.type == 'bond':
            asset = Bond.objects.get(ticker=portfolio.ticker)
        else:
            asset = Fund.objects.get(ticker=portfolio.ticker)

        current_price = asset.price
        value = current_price * portfolio.amount
        profit_loss = value - (portfolio.buy_price * portfolio.amount)
        change_percentage = (profit_loss / (portfolio.buy_price * portfolio.amount)) * 100

        total_value += value
        asset_allocation[portfolio.get_type_display()] += float(value) 

        if portfolio.type == 'stock':
            stock_allocation += float(value)
            stock_data[portfolio.ticker] = float(value)
        elif portfolio.type == 'crypto':
            crypto_allocation += float(value)
            crypto_data[portfolio.ticker] = float(value)
        elif portfolio.type == 'bond':
            bond_allocation += float(value)
            bond_data[portfolio.ticker] = float(value)
        elif portfolio.type == 'fund':
            fund_allocation += float(value)
            fund_data[portfolio.ticker] = float(value)

        portfolio_data.append({
            'type': portfolio.get_type_display(),
            'ticker': portfolio.ticker,
            'name': portfolio.name,
            'amount': float(portfolio.amount), 
            'buy_price': float(portfolio.buy_price), 
            'current_price': float(current_price),
            'value': float(value),  
            'profit_loss': float(profit_loss),  
            'change': float(change_percentage),  #
        })

    asset_allocation_json = json.dumps(asset_allocation)
    stock_allocation_json = json.dumps(stock_data)
    crypto_allocation_json = json.dumps(crypto_data)
    bond_allocation_json = json.dumps(bond_data)
    fund_allocation_json = json.dumps(fund_data)


    performance_labels = [item['ticker'] for item in portfolio_data]
    performance_data = [item['change'] for item in portfolio_data]

    context = {
        'total_value': total_value,
        'asset_allocation': asset_allocation_json,
        'portfolio_data': portfolio_data,
        'performance_labels': json.dumps(performance_labels),
        'performance_data': json.dumps(performance_data), 
        'stock_allocation': stock_allocation,
        'crypto_allocation': crypto_allocation,
        'bond_allocation': bond_allocation,
        'fund_allocation': fund_allocation,
        'stock_allocation_json': stock_allocation_json,
        'crypto_allocation_json': crypto_allocation_json,
        'bond_allocation_json': bond_allocation_json,
        'fund_allocation_json': fund_allocation_json
    }

    return render(request, 'analyze.html', context)
# def delete_portfolio_item(request, pk):
#     portfolio_item = get_object_or_404(Portfolio, pk=pk, user=request.user)
#     if request.method == "POST":
#         # Fetch the current price from the appropriate model based on the type
#         current_price = 0
#         try:
#             if portfolio_item.type == 'stock':
#                 current_price = Stock.objects.get(ticker=portfolio_item.ticker).price
#             elif portfolio_item.type == 'crypto':
#                 current_price = Crypto.objects.get(symbol=portfolio_item.ticker).price
#             elif portfolio_item.type == 'bond':
#                 current_price = Bond.objects.get(ticker=portfolio_item.ticker).price
#             elif portfolio_item.type == 'fund':
#                 current_price = Fund.objects.get(ticker=portfolio_item.ticker).price
#         except (Stock.DoesNotExist, Crypto.DoesNotExist, Bond.DoesNotExist, Fund.DoesNotExist):
#             pass  # Handle the case where the current price cannot be found

#         # Insert into History
#         History.objects.create(
#             user=request.user,
#             ticker_or_symbol=portfolio_item.ticker,
#             type=portfolio_item.type,
#             action='sell',
#             amount=portfolio_item.amount,
#             price=current_price,
#             purchase_date=timezone.now()
#         )
#         portfolio_item.delete()
#         return redirect("base:home")
#     return render(request, "delete_confirmation.html", {"portfolio_item": portfolio_item})

