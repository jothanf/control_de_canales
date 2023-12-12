from django.shortcuts import render, redirect, get_object_or_404
from .models import PurchaserModel, PurchaseHistory, acounts_history
from datetime import datetime, timedelta
from django.db.models import Q

# Create your views here.
def accounting_home(request):
    return render(request, 'accounting_home.html')

def purchaser_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        total_credit_limit = request.POST.get('total_credit_limit')
        new_purchaser = PurchaserModel(
            name=name,
            phone=phone,
            address=address,
            total_credit_limit=total_credit_limit
        )
        new_purchaser.save()
        success = f'Se ha creado el usuario {name}'
        return render(request, 'purchaser_create.html', {'succes': success})
    return render(request, 'purchaser_create.html')

def purchaser_read(request):
    all_purchasers = PurchaserModel.objects.all()
    return render(request, 'purchaser_read.html', {'all_purchasers': all_purchasers})

def purchaser_detail(request, purchaser_id):
    purchaser = get_object_or_404(PurchaserModel, id=purchaser_id)
    contador_1 = 0
    contador_2 = 0
    all_purchases = PurchaseHistory.objects.filter(purchaser=purchaser)

    for purchase in all_purchases:
        contador_2 += purchase.payment
    purchaser.total_payments = contador_2
    purchaser.save()

    pending_purchases = PurchaseHistory.objects.filter(purchaser=purchaser, status='pending')
    for purchase in pending_purchases:
        contador_1 += purchase.price
        contador_1 -= purchase.payment
    purchaser.outstanding_balance = contador_1
    purchaser.save()
    return render(request, 'purchaser_detail.html', {'purchaser': purchaser,'all_purchases': all_purchases})

def purchaser_delete(request, purchaser_id):
    purchaser = get_object_or_404(PurchaserModel, id=purchaser_id)
    if request.method == 'POST':
        purchaser.delete()
        return redirect('purchaser_read')

    return render(request, 'purchaser_delete.html', {'purchaser': purchaser})

def new_purchase(request):
    all_purchasers = PurchaserModel.objects.all()
    payment_method_choices = PurchaseHistory.PAYMENT_METHOD_CHOICES
    if request.method == 'POST':
        purchaser_id = request.POST.get('purchaser')
        purchaser = get_object_or_404(PurchaserModel, id=purchaser_id)
        price = request.POST.get('price_sale')
        payment_method = request.POST.get('payment_method')
        weight = request.POST.get('weight')
        description = request.POST.get('description')
        status = 'pending'
        date = datetime.now()
        if payment_method == 'cash':
            status = 'paid'
            payment = price
        else:
            payment = 0
        new_purchase = PurchaseHistory(
            purchaser=purchaser,
            price=price,
            payment_method=payment_method,
            status=status,
            purchase_date=date,
            weight=weight,
            description=description,
            payment = payment
        )
        new_purchase.save()
        succes = 'Compra realizada'
        return render(request, 'new_purchase.html', {'all_purchasers': all_purchasers, 'payment_method_choices': payment_method_choices, 'succes': succes})
    return render(request, 'new_purchase.html', {'all_purchasers': all_purchasers, 'payment_method_choices': payment_method_choices})

def purchases_read(request):
    all_purchases = PurchaseHistory.objects.all()
    return render( request, 'purchases_read.html', {'all_purchases': all_purchases})

def make_payment(request, purchase_id):
    purchase = get_object_or_404(PurchaseHistory, id=purchase_id)
    purchaser = purchase.purchaser
    if request.method == 'POST':
        payment=request.POST.get('payment')
        controler = int(payment) + purchase.payment
        if controler > purchase.price:
            error = 'El pago supera la deuda'
            return render(request, 'make_payment.html', {'purchase': purchase, 'purchaser': purchaser, 'error': error})
        purchase.payment += int(payment)
        if purchase.payment == purchase.price:
            purchase.status = 'paid'
        purchase.save()
        succes = f'Se realizo un abono por ${payment}'
        return render(request, 'make_payment.html', {'purchase': purchase, 'purchaser': purchaser, 'succes': succes})
    return render(request, 'make_payment.html', {'purchase': purchase, 'purchaser': purchaser})

def day_purchase(request):
    all_records = acounts_history.objects.all().order_by('-date_day')[:10] 
    if request.method == 'POST':

        date_day = datetime.now()
        sale_day_cash = request.POST.get('sale_day_cash')
        sale_day_credit = request.POST.get('sale_day_credit')
        credit_day_payment = request.POST.get('credit_day_payment')

        total_income = int(sale_day_cash) + int(credit_day_payment)
        

        new_record = acounts_history(
            date_day = date_day,
            sale_day_cash = sale_day_cash,
            sale_day_credit = sale_day_credit,
            credit_day_payment = credit_day_payment,
            total_income = total_income,
        )
        new_record.save()
        all_records = acounts_history.objects.all().order_by('-date_day')[:10] 
        return redirect('day_purchase_aux')
    return render(request, 'day_purchase.html', {'all_records': all_records})

def day_purchase_aux(request):
    all_records = acounts_history.objects.all().order_by('-date_day')[:10] 
    return render(request, 'day_purchase_aux.html', {'all_records': all_records})

def sale_history(request):
    if request.method == 'POST':
        init_date = request.POST.get('init_date')
        finish_date = request.POST.get('finish_date')

        init_date = datetime.strptime(init_date, '%Y-%m-%d')
        finish_date = datetime.strptime(finish_date, '%Y-%m-%d')

        finish_date += timedelta(days=1)

        records = acounts_history.objects.filter(
            Q(date_day__gte=init_date) & Q(date_day__lt=finish_date)
        )

        summary = {
            'counter': 0,
            'cash_counter': 0,
            'credit_counter': 0,
            'credit_day_counter': 0,
            'total_income_counter': 0,
            'pending_credit_counter': 0,
        }

        for record in records:
            summary['counter'] += 1
            summary['cash_counter'] += record.sale_day_cash
            summary['credit_counter'] += record.sale_day_credit
            summary['credit_day_counter'] += record.credit_day_payment
            summary['total_income_counter'] += record.total_income
            summary['pending_credit_counter'] = summary['credit_counter'] - summary['credit_day_counter']

        return render(request, 'sale_history.html', {'records': records, 'summary': summary, 'init_date': init_date, 'finish_date': finish_date})

    return render(request, 'sale_history.html')

def records_delete(request, record_id):
    record = get_object_or_404(acounts_history, id=record_id)
    if request.method == 'POST':
        record.delete()
        return redirect('sale_history')
    return render(request, 'records_delete.html', {'record': record})

import random
import matplotlib.pyplot as plt
import io
import base64
import statistics  # Importar el módulo de estadísticas

def payment_stats(request):
    # Genera datos aleatorios para emular un mes completo de ventas
    import datetime
    from dateutil.relativedelta import relativedelta

    # Fecha de inicio del mes
    start_date = datetime.date.today().replace(day=1)

    # Crea una lista de fechas para el mes completo
    fechas = [start_date + relativedelta(days=i) for i in range(7)]

    # Genera datos aleatorios para ventas en efectivo y ventas a crédito
    peso_canal = [random.randint(300, 350) for _ in range(7)]
    Peso_desperdicio = [random.randint(250, 285) for _ in range(7)]

    # Calcular el valor total para cada tipo de pago
    total_peso_canal = sum(peso_canal)
    total_peso_desperdicio = sum(Peso_desperdicio)

    # Calcular la mediana para cada tipo de pago
    mediana_efectivo = statistics.median(peso_canal)
    mediana_credito = statistics.median(Peso_desperdicio)

    # Calcular la moda para cada tipo de pago (puedes personalizarlo para tu contexto)
    moda_efectivo = statistics.mode(peso_canal)
    moda_credito = statistics.mode(Peso_desperdicio)

    # Calcular el rango para cada tipo de pago
    rango_efectivo = max(peso_canal) - min(peso_canal)
    rango_credito = max(Peso_desperdicio) - min(Peso_desperdicio)

    # Calcular la desviación estándar para cada tipo de pago
    desviacion_efectivo = statistics.stdev(peso_canal)
    desviacion_credito = statistics.stdev(Peso_desperdicio)

    # Crear un gráfico de barras
    plt.figure(figsize=(10, 6))
    x = range(len(fechas))
    width = 0.4  # Ancho de las barras
    plt.bar(x, peso_canal, width=width, label='Peso de canal')
    plt.bar([i + width for i in x], Peso_desperdicio, width=width, label='Peso desperdicio')

    # Agrega etiquetas de valor en la parte superior de cada columna
    for i, valor_efectivo in enumerate(peso_canal):
        plt.text(i, valor_efectivo, str(valor_efectivo), ha='center', va='bottom')
    for i, valor_credito in enumerate(Peso_desperdicio):
        plt.text(i + width, valor_credito, str(valor_credito), ha='center', va='bottom')

    plt.xlabel('Fechas')
    plt.ylabel('Pesos en kilos')
    plt.legend()
    plt.xticks([i + width / 2 for i in x], [str(fecha) for fecha in fechas], rotation=45)

    # Guardar la imagen del gráfico
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Convierte la imagen en base64 para incrustarla en la plantilla HTML
    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'payment_stats.html', {
        'graphic': graphic,
        'total_peso_canal': total_peso_canal,
        'total_peso_desperdicio': total_peso_desperdicio,
        'mediana_efectivo': mediana_efectivo,
        'mediana_credito': mediana_credito,
        'moda_efectivo': moda_efectivo,
        'moda_credito': moda_credito,
        'rango_efectivo': rango_efectivo,
        'rango_credito': rango_credito,
        'desviacion_efectivo': desviacion_efectivo,
        'desviacion_credito': desviacion_credito,
    })

