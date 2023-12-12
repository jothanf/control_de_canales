from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import ProviderModel, AnimalModel, OtherExpensesModel
from .forms import ProviderModelForm, AnimalForm
from datetime import datetime, timedelta

# Create your views here.
def main(request):
    return render(request, 'main.html')

def canales_home(request):
    return render(request, 'canales_home.html')

def providers_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        credit_balance = request.POST.get('credit_balance')

        new_provider = ProviderModel(
            name = name,
            phone = phone,
            address = address,
            credit_balance = credit_balance
        )

        new_provider.save()
        return redirect('providers_create_success', provider_id=new_provider.id)
    return render(request, 'providers_create.html')

def providers_create_success(request, provider_id):
    provider = get_object_or_404(ProviderModel, id=provider_id)
    return render(request, 'providers_create_success.html', {'provider': provider})
        
def providers_read(request):
    all_providers = ProviderModel.objects.all()
    return render(request, 'providers_read.html', {'all_providers':all_providers})

def providers_detail(request, provider_id):
    provider = get_object_or_404(ProviderModel, id=provider_id)
    pending_cows = AnimalModel.objects.filter(provider = provider, payment_state = 'pending')

    counter = 0
    for cow in pending_cows:
        counter += cow.balance_due

    cows_provider = AnimalModel.objects.filter(provider = provider)

    paid_counter = 0

    for cow in cows_provider:
        paid_counter += cow.payments

    provider.pending_balance = counter
    provider.total_paid = paid_counter
    provider.save()


    if request.method == 'POST':

        init_date = request.POST.get('init_date')
        end_date = request.POST.get('end_date')  
        
        cows_by_date = AnimalModel.objects.filter(purchase_dates__range=(init_date, end_date), provider = provider).order_by('purchase_dates')

        animal_counter = 0
        total_live_price_counter = 0
        cow_counter = 0
        pigg_counter = 0
        cow_alive_counter = 0
        cow_processed_counter = 0
        pigg_alive_counter = 0
        pigg_processed_counter = 0

        for cow in cows_by_date:
            animal_counter += 1

            if cow.live_price is not None:
                total_live_price_counter += cow.live_price

            if cow.animal_type == 'vacuno':
                cow_counter += 1
            
            else:
                pigg_counter +=1

            if cow.state == 'alive' and cow.animal_type == 'vacuno':
                cow_alive_counter += 1

            if cow.state == 'processed' and cow.animal_type == 'vacuno':
                cow_processed_counter += 1

            if cow.state == 'alive' and cow.animal_type == 'porcino':
                pigg_alive_counter += 1

            if cow.state == 'processed' and cow.animal_type == 'porcino':
                pigg_processed_counter += 1
        
        return render(request, 'providers_detail.html', {
            'provider':provider,
            'cows_by_date':cows_by_date,
            'init_date': init_date,
            'end_date': end_date,
            'total_live_price_counter': total_live_price_counter,
            'animal_counter': animal_counter,
            'cow_counter': cow_counter,
            'pigg_counter': pigg_counter,
            'cow_alive_counter': cow_alive_counter,
            'cow_processed_counter': cow_processed_counter,
            'pigg_alive_counter': pigg_alive_counter,
            'pigg_processed_counter': pigg_processed_counter})
    
    return render(request, 'providers_detail.html', {'provider':provider})

def provider_update(request, provider_id):
    provider = get_object_or_404(ProviderModel, id=provider_id)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        new_phone = request.POST.get('phone')
        new_address = request.POST.get('address')
        new_credit_balance = request.POST.get('credit_balance')

        provider.name = new_name
        provider.phone = new_phone
        provider.address = new_address
        provider.credit_balance = new_credit_balance

        provider.save()

        return redirect('provider_update_success', provider.id)
    return render(request, 'provider_update.html', {'provider': provider})

def provider_update_success(request, provider_id):
    provider = get_object_or_404(ProviderModel, id=provider_id)
    return render(request, 'provider_update_success.html', {'provider': provider})

def providers_delete(request, provider_id):
    provider = get_object_or_404(ProviderModel, id=provider_id)
    if request.method == 'POST':
        provider.delete()
        return redirect('providers_read')
    return render(request, 'providers_delete.html', {'provider': provider})

def make_payment_provider(request, cow_id):
    cow = get_object_or_404(AnimalModel, id=cow_id)
    provider_id = cow.provider.id
    provider = get_object_or_404(ProviderModel, id=provider_id)
    success = None
    error_message = None

    if request.method == 'POST':
        deposit = request.POST.get('deposit')

        if deposit is not None and deposit.strip():
            deposit = int(deposit)
            cow.payments = cow.payments or 0
            new_balance = cow.live_price - (cow.payments + deposit)

            if new_balance < 0:
                error_message = 'El abono supera el saldo pendiente'
            else:
                cow.payments += deposit
                cow.balance_due = new_balance
                cow.save()
                success = 'Abono realizado'

                if cow.payments >= cow.live_price:
                    cow.payment_state = 'paid'
                    cow.save()
        else:
            error_message = 'El campo de depósito no se ha proporcionado o es inválido'

    return render(request, 'make_payment_provider.html', {'cow': cow, 'provider': provider, 'success': success, 'error_message': error_message})

def cow_create(request):
    form = AnimalForm()
    providers = ProviderModel.objects.all()
    message = None

    if request.method == 'POST':
        identification = request.POST.get('identification')
        live_price = request.POST.get('live_price')
        live_weight = request.POST.get('live_weight')
        purchase_dates = request.POST.get('purchase_dates')
        payment_terms = request.POST.get('payment_terms')
        provider_id = request.POST.get('provider')  # Obtener el ID del proveedor

        if not identification:
            message = 'Debes proporcionar una identificación.'
        elif not provider_id:
            message = 'Debes seleccionar un proveedor.'
        elif not purchase_dates:  # Verifica si la fecha está vacía
            message = 'Debes proporcionar una fecha de compra.'
        else:
            if not payment_terms:
                message = 'Debes proporcionar un valor válido para los términos de pago.'
            else:
                try:
                    payment_terms = int(payment_terms)
                except ValueError:
                    message = 'Los términos de pago deben ser un número entero.'
                    payment_terms = None

        if message is None:
            if purchase_dates:
                try:
                    purchase_date = datetime.strptime(purchase_dates, '%Y-%m-%d')
                except ValueError:
                    message = 'El formato de fecha es incorrecto. Debe ser YYYY-MM-DD.'
                else:
                    payment_date = purchase_date + timedelta(days=payment_terms)
                    animal = AnimalModel(
                        identification=identification,
                        live_price=live_price,
                        live_weight=live_weight,
                        purchase_dates=purchase_dates,
                        payment_terms=payment_terms,
                        payment_date=payment_date
                    )
                    animal.save()

                    # Asignar el proveedor
                    provider = ProviderModel.objects.get(id=provider_id)
                    if provider.pending_balance is None:
                        provider.pending_balance = 0
                    provider.pending_balance += int(animal.live_price)
                    animal.provider = provider
                    provider.save()

                    animal.save()

                    return redirect('canales_home')

    return render(request, 'cow_create.html', {'form': form, 'providers': providers, 'message': message})

def cow_create_y(request):
    providers = ProviderModel.objects.all()
    animal_type_choices = AnimalModel.ANIMAL_TYPE_CHOICES
    if request.method == 'POST':
        identification = request.POST.get('identification')
        kg_price = request.POST.get('kg_price')
        live_weight = request.POST.get('live_weight')
        total_price = int(kg_price) * int(live_weight)
        provider_id = request.POST.get('provider')
        provider = ProviderModel.objects.get(id=provider_id)
        payment_terms = int(request.POST.get('payment_terms'))
        purchase_date = datetime.strptime(request.POST.get('purchase_dates'), '%Y-%m-%d')
        payment_date = purchase_date + timedelta(days=payment_terms)
        animal_type = request.POST.get('animal_type')

        new_animal = AnimalModel.objects.create(
            identification=identification,
            live_price=total_price,
            live_weight=live_weight,
            payment_terms=payment_terms,
            purchase_dates=purchase_date,
            payment_date=payment_date,
            provider=provider,
            animal_type=animal_type,
            balance_due=total_price,
        )
        new_animal.save()

        return redirect('cow_create_y_succes', animal_id = new_animal.id, kg_price = kg_price)
    return render(request, 'cow_create_y.html', {'providers': providers, 'animal_type_choices': animal_type_choices})

def cow_create_y_succes(request, animal_id, kg_price):
    new_animal = get_object_or_404(AnimalModel, id=animal_id)
    return render(request, 'cow_create_y_succes.html', {'new_animal': new_animal, 'kg_price': kg_price})

def cow_create_2(request, cow_id):
    if request.method == 'POST':
        slaughter_dates = request.POST.get('slaughter_dates')
        canal_weight = request.POST.get('canal_weight')
        
        # Procesar los datos de 'otros_gastos' para construir una lista de instancias de OtherExpensesModel
        other_expenses = []
        descripciones = request.POST.getlist('descripcion')
        precios = request.POST.getlist('precio')
        
        for descripcion, precio in zip(descripciones, precios):
            if descripcion and precio:
                expense = OtherExpensesModel(description=descripcion, price=precio)
                other_expenses.append(expense)

        # Obtener la vaca (AnimalModel) basada en su ID
        cow = AnimalModel.objects.get(id=cow_id)

        # Eliminar los gastos existentes asociados a la vaca
        cow.expenses.all().delete()

        # Asignar los datos capturados a la instancia de la vaca
        cow.slaughter_dates = slaughter_dates
        cow.canal_weight = canal_weight
        cow.state = 'processed'

        # Guardar la instancia de la vaca en la base de datos
        cow.save()

        # Asignar los nuevos gastos adicionales a la vaca
        with transaction.atomic():
            for expense in other_expenses:
                expense.animal = cow
                expense.save()

        # Redirigir o realizar otras acciones según tus necesidades
        return redirect('cow_create_3', cow_id)

    elif request.method == 'GET':
        cow = AnimalModel.objects.get(id=cow_id)
        return render(request, 'cow_create_2.html', {'cow_id': cow_id, 'cow': cow})
   
def cow_create_3(request, cow_id):
    cow = get_object_or_404(AnimalModel, id=cow_id)
    contador = 0
    expenses = OtherExpensesModel.objects.filter(animal=cow)

    for expense in expenses:
        contador += expense.price
    
    
    cow.other_expenses = contador
    cow.total_price_purchase = cow.live_price + cow.other_expenses
    cow.canal_price = cow.total_price_purchase / cow.canal_weight
    cow.save()

    return render(request, 'cow_create_3.html', {'cow':cow, 'contador':contador})

def proccess_animal(request):
    live_animals = AnimalModel.objects.filter(state='alive')
    return render(request, 'proccess_animal.html', {'live_animals': live_animals})

def cow_read(request):
    if request.method == 'POST':
        init_date = request.POST.get('init_date')
        end_date = request.POST.get('end_date')  
        
        cows_by_date = AnimalModel.objects.filter(purchase_dates__range=(init_date, end_date)).order_by('purchase_dates')
        
        return render(request, 'cow_read.html', {'cows_by_date': cows_by_date})
   
    return render(request, 'cow_read.html')

def cow_detail(request, cow_id):
    counter = 0
    cow = get_object_or_404(AnimalModel, id=cow_id)
    brut_price = int(cow.live_price)/ int(cow.live_weight)
    expenses = OtherExpensesModel.objects.filter(animal=cow)

    for expense in expenses:
        counter += expense.price

    return render(request, 'cow_detail.html', {'cow': cow, 'expenses': expenses, 'brut_price': brut_price})

def cow_update(request, cow_id):
    cow = get_object_or_404(AnimalModel, id=cow_id)
    providers = ProviderModel.objects.all()
    animal_type_choices = AnimalModel.ANIMAL_TYPE_CHOICES
    if request.method == 'POST':
        identification = request.POST.get('identification')
        kg_price = request.POST.get('kg_price')
        live_weight = request.POST.get('live_weight')
        total_price = int(kg_price) * int(live_weight)
        provider_id = request.POST.get('provider')
        provider = ProviderModel.objects.get(id=provider_id)
        payment_terms = int(request.POST.get('payment_terms'))
        purchase_date = datetime.strptime(request.POST.get('purchase_dates'), '%Y-%m-%d')
        payment_date = purchase_date + timedelta(days=payment_terms)
        animal_type = request.POST.get('animal_type')

        cow.delete()

        cow_update = AnimalModel.objects.create(
            identification=identification,
            live_price=total_price,
            live_weight=live_weight,
            payment_terms=payment_terms,
            purchase_dates=purchase_date,
            payment_date=payment_date,
            provider=provider,
            animal_type=animal_type,
            balance_due=total_price,
        )
        cow_update.save()
        return redirect('cow_detail', cow_update.id)

    return render(request, 'cow_update.html', {'cow': cow, 'providers': providers, 'animal_type_choices': animal_type_choices})

def cow_delete(request, cow_id):
    cow = get_object_or_404(AnimalModel, id= cow_id)
    if request.method == 'POST':
        cow.delete()
        return redirect('cow_read')
    return render(request, 'cow_delete.html', {'cow': cow})

def expenses_read(request):
    all_expenses = OtherExpensesModel.objects.all()
    return render(request, 'expenses_read.html', {'expenses': all_expenses})

def pending_counts(request):
    pendig_cows = AnimalModel.objects.filter(payment_state='pending').order_by('payment_date')
    pending_counter = 0
    for cow in pendig_cows:
        pending_counter += 1
    return render(request, 'pending_counts.html', {'pending_cows': pendig_cows, 'pending_counter': pending_counter})

def moviments_by_date(request):
    all_cows = AnimalModel.objects.all()
    
    if request.method == 'POST':
        init_date = request.POST.get('init_date')
        end_date = request.POST.get('end_date')  # Asegúrate de agregar un campo de fecha de fin en tu formulario
        # Filtrar los objetos entre las fechas de inicio y fin
        cows_by_date = AnimalModel.objects.filter(purchase_dates__range=(init_date, end_date))
        return render(request, 'moviments_by_date.html', {'init_date': init_date, 'end_date': end_date, 'all_cows': all_cows, 'cows_by_date': cows_by_date})
    
    return render(request, 'moviments_by_date.html')


from django.shortcuts import render
from .models import AnimalModel
import matplotlib.pyplot as plt
import io
import urllib
import base64

def purchases_by_date(request):
    if request.method == 'POST':
        init_date = request.POST.get('init_date')
        end_date = request.POST.get('end_date')

        cows_by_date = AnimalModel.objects.filter(purchase_dates__range=(init_date, end_date)).order_by('purchase_dates')

        context = {
            'init_date': init_date,
            'end_date': end_date,
            'all_cows': AnimalModel.objects.all(),
            'cows_by_date': cows_by_date,
            'total_live_price_counter': 0,
            'animal_counter': 0,
            'cow_counter': 0,
            'pigg_counter': 0,
            'cow_alive_counter': 0,
            'cow_processed_counter': 0,
            'pigg_alive_counter': 0,
            'pigg_processed_counter': 0,
            'average_cow_price': 0,
            'average_pigg_price': 0,
        }

        cow_prices = 0  # Lista para almacenar los precios de las vacas
        pigg_prices = 0

        for cow in cows_by_date:
            context['animal_counter'] += 1

            if cow.animal_type == 'vacuno':
                context['cow_counter'] += 1
                context['total_live_price_counter'] += cow.live_price
                cow_prices += cow.live_price
            
            if cow.animal_type == 'porcino':
                context['pigg_counter'] += 1
            
                pigg_prices += cow.live_price
                

            if cow.state == 'alive' and cow.animal_type == 'vacuno':
                context['cow_alive_counter'] += 1

            if cow.state == 'processed' and cow.animal_type == 'vacuno':
                context['cow_processed_counter'] += 1

            if cow.state == 'alive' and cow.animal_type == 'porcino':
                context['pigg_alive_counter'] += 1

            if cow.state == 'processed' and cow.animal_type == 'porcino':
                context['pigg_processed_counter'] += 1
        
        context['total_live_price_counter'] = int(cow_prices) + int(pigg_prices)

        context['average_cow_price'] = int(cow_prices / context['cow_counter'])
        context['average_pigg_price'] = int(pigg_prices / context['pigg_counter'])

        # Crear la gráfica de barras
        animal_type_counts = {
            'Vacuno': context['cow_counter'],
            'Porcino': context['pigg_counter'],
        }
        
        # Crear la gráfica de barras con precios
        
        plt.figure(figsize=(8, 6))
        ax1 = plt.subplot(121)
        ax1.bar(animal_type_counts.keys(), animal_type_counts.values())
        ax1.set_title('Cantidad de Animales por Tipo')
        ax1.set_xlabel('Tipo de Animal')
        ax1.set_ylabel('Cantidad')

        ax2 = plt.subplot(122)
        bars = ax2.bar(['Vacas', 'Cerdos'], [cow_prices, pigg_prices])
        ax2.set_title('Precio Total por Tipo')
        ax2.set_xlabel('Tipo de Animal')
        ax2.set_ylabel('Precio Total')

        # Agregar etiquetas con los valores numéricos en la parte superior de las barras
        for bar, price in zip(bars, [cow_prices, pigg_prices]):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(price), ha='center', va='bottom')

        plt.tight_layout()

        # Guardar la gráfica en un archivo o mostrarla en la respuesta HTTP
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_url = base64.b64encode(buffer.read()).decode()
        buffer.close()

        # Agregar la URL de la gráfica al contexto
        context['chart_url'] = f'data:image/png;base64,{chart_url}'

        return render(request, 'purchases_by_date.html', context)

    return render(request, 'purchases_by_date.html')


def purchases_by_date_stats(request):
    return render(request, 'purchases_by_date_stats.html')




def purchases_by_date_(request):
    all_cows = AnimalModel.objects.all()
    
    if request.method == 'POST':
        init_date = request.POST.get('init_date')
        end_date = request.POST.get('end_date')  
        
        cows_by_date = AnimalModel.objects.filter(purchase_dates__range=(init_date, end_date)).order_by('purchase_dates')
        
        total_live_price_counter = 0
        animal_counter = 0
        cow_counter = 0
        pigg_counter = 0
        cow_alive_counter = 0
        cow_processed_counter = 0
        pigg_alive_counter = 0
        pigg_processed_counter = 0
        for cow in cows_by_date:
            animal_counter += 1
            if cow.live_price is not None:
                total_live_price_counter += cow.live_price

            if cow.animal_type == 'vacuno':
                cow_counter += 1
            else:
                pigg_counter +=1

            if cow.state == 'alive' and cow.animal_type == 'vacuno':
                cow_alive_counter += 1

            if cow.state == 'processed' and cow.animal_type == 'vacuno':
                cow_processed_counter += 1

            if cow.state == 'alive' and cow.animal_type == 'porcino':
                pigg_alive_counter += 1

            if cow.state == 'processed' and cow.animal_type == 'porcino':
                pigg_processed_counter += 1

        
        
        return render(request, 'purchases_by_date.html', {'init_date': init_date, 'end_date': end_date, 'all_cows': all_cows, 'cows_by_date': cows_by_date, 'total_live_price_counter': total_live_price_counter, 'animal_counter': animal_counter, 'cow_counter': cow_counter, 'pigg_counter': pigg_counter, 'cow_alive_counter': cow_alive_counter, 'cow_processed_counter': cow_processed_counter , 'pigg_alive_counter': pigg_alive_counter, 'pigg_processed_counter': pigg_processed_counter})

    return render(request, 'purchases_by_date.html')

def processed_by_date(request):
    all_cows = AnimalModel.objects.all()
    
    if request.method == 'POST':
        init_date = request.POST.get('init_date')
        end_date = request.POST.get('end_date')  
        
        cows_by_date = AnimalModel.objects.filter(state='processed', purchase_dates__range=(init_date, end_date)).order_by('slaughter_dates')  

        return render(request, 'processed_by_date.html', {'init_date': init_date, 'end_date': end_date, 'all_cows': all_cows, 'cows_by_date': cows_by_date})
    
    return render(request, 'processed_by_date.html')

def cow_create_by_lote(request):
    providers = ProviderModel.objects.all()
    animal_type_choices = AnimalModel.ANIMAL_TYPE_CHOICES
    
    if request.method == 'POST':
        live_price = int(request.POST.get('live_price'))
        live_weight = int(request.POST.get('live_weight'))
        quantity = int(request.POST.get('animal_quantity'))
        purchase_date = datetime.strptime(request.POST.get('purchase_dates'), '%Y-%m-%d').date()
        payment_terms = int(request.POST.get('payment_terms'))
        total_price = live_price * live_weight
        partial_price = total_price / quantity
        partial_weight = live_weight / quantity
        animal_type = request.POST.get('animal_type')
        
        with transaction.atomic():
            for i in range(1, quantity + 1):
                description = request.POST.get('identification') + f' ({i}/{quantity})'
                animal = AnimalModel.objects.create(
                    identification=description,
                    live_price=partial_price,
                    live_weight=partial_weight,
                    provider=ProviderModel.objects.get(pk=request.POST.get('provider')),
                    purchase_dates=purchase_date,
                    payment_terms=payment_terms,
                    payment_date=purchase_date + timedelta(days=payment_terms),
                    animal_type=animal_type,
                    balance_due=partial_price,
                )
                animal.save()
        
        return redirect('cow_create_by_batches_succes')

    return render(request, 'cow_create_by_lote.html', {'providers': providers, 'animal_type_choices': animal_type_choices})

def cow_create_by_batches_succes(request):
    return render(request, 'cow_create_by_batches_succes.html')
