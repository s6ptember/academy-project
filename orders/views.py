from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassa import Payment, Configuration
from django.conf import settings
from .models import Order
from main.models import Course
from decimal import Decimal
import json
import logging
from uuid import uuid4 

logger = logging.getLogger(__name__)

# Настройка ЮKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Проверка, оплачен ли курс
    if Order.objects.filter(user=request.user, course=course, status='completed').exists():
        messages.info(request, "Вы уже приобрели этот курс!")
        return redirect('main:course_detail', course_id=course.id)

    # Цена курса из модели Course (в RUB)
    course_price = course.price

    if request.method == 'POST':
        try:
            order = Order.objects.create(
                user=request.user,
                course=course,
                total_price=course_price,
                status='pending'
            )

            # Создание платежа в ЮKassa
            payment = create_yookassa_payment(order, request)
            return redirect(payment.confirmation.confirmation_url)

        except Exception as e:
            logger.error(f"Ошибка создания платежа: {str(e)}")
            order.delete()
            messages.error(request, f"Ошибка обработки платежа: {str(e)}")
            return render(request, 'orders/checkout.html', {'course': course, 'total_price': course_price})

    return render(request, 'orders/checkout.html', {'course': course, 'total_price': course_price})


def create_yookassa_payment(order, request):
    receipt_items = [{
        "description": f"Курс: {order.course.title}",
        "quantity": "1",
        "amount": {
            "value": f"{order.total_price:.2f}",
            "currency": "RUB"
        },
        "vat_code": getattr(settings, 'YOOKASSA_VAT_CODE', 1),
        "payment_mode": "full_payment",
        "payment_subject": "commodity"
    }]

    customer = {
        "email": order.user.email
    }

    discounted_total_rub = order.get_discounted_total()

    try:
        # Генерируем уникальный ключ идемпотентности
        idempotence_key = str(uuid4())
        payment = Payment.create({
            "amount": {
                "value": f"{discounted_total_rub:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": request.build_absolute_uri('/orders/yookassa/success/') + f'?order_id={order.id}'
            },
            "capture": True,
            "description": f"Заказ #{order.id}",
            "metadata": {
                "order_id": order.id,
                "user_id": order.user.id
            },
            "receipt": {
                "customer": customer,
                "items": receipt_items
            }
        }, idempotence_key)  # Используем уникальный ключ

        order.yookassa_payment_id = payment.id
        order.save()
        return payment
    except Exception as e:
        logger.error(f"Ошибка создания платежа ЮKassa: {str(e)}")
        raise

@csrf_exempt
@require_POST
def yookassa_webhook(request):
    if request.method != 'POST':
        logger.warning(f"Недопустимый метод запроса: {request.method}")
        return HttpResponseNotAllowed(['POST'])

    logger.info(f"ЮKassa webhook получен | IP: {request.META.get('REMOTE_ADDR')} | User-Agent: {request.META.get('HTTP_USER_AGENT')}")

    try:
        raw_body = request.body.decode('utf-8')
        event_json = json.loads(raw_body)
        event_type = event_json.get('event')
        payment = event_json.get('object', {})
        payment_id = payment.get('id')

        logger.info(f"Обработка события ЮKassa: {event_type} | Payment ID: {payment_id}")

        metadata = payment.get('metadata', {})
        order_id = metadata.get('order_id')
        user_id = metadata.get('user_id')

        if not all([order_id, user_id]):
            logger.error(f"Отсутствуют метаданные: order_id={order_id}, user_id={user_id}")
            return HttpResponseBadRequest("Отсутствуют необходимые метаданные")

        order = Order.objects.select_for_update().get(id=order_id, user_id=user_id)

        if event_type == 'payment.succeeded':
            if payment.get('status') == 'succeeded':
                if order.status == 'completed':
                    logger.info(f"Заказ {order_id} уже обработан, пропускаем")
                    return HttpResponse(status=200)
                
                order.status = 'completed'
                order.yookassa_payment_id = payment_id
                order.save()
                logger.info(f"Заказ {order_id} успешно обработан")

        elif event_type == 'payment.canceled':
            if payment.get('status') == 'canceled':
                if order.status == 'cancelled':
                    logger.info(f"Заказ {order_id} уже отменен, пропускаем")
                    return HttpResponse(status=200)
                
                order.status = 'cancelled'
                order.save()
                logger.info(f"Заказ {order_id} помечен как отменен")

        return HttpResponse(status=200)

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {str(e)}")
        return HttpResponseBadRequest("Неверный JSON")
    except Order.DoesNotExist:
        logger.error(f"Заказ не найден: order_id={order_id}, user_id={user_id}")
        return HttpResponseBadRequest("Заказ не найден")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return HttpResponse(status=500)

def yookassa_success(request):
    order_id = request.GET.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'completed':
            messages.success(request, "Оплата прошла успешно! Доступ к курсу открыт.")
            return render(request, 'orders/yookassa_success.html', {'order': order})
        elif order.status == 'cancelled':
            return redirect('orders:yookassa_cancel')
        if order.yookassa_payment_id:
            try:
                payment = Payment.find_one(order.yookassa_payment_id)
                if payment.status == 'succeeded':
                    order.status = 'completed'
                    order.save()
                    messages.success(request, "Оплата прошла успешно! Доступ к курсу открыт.")
                    return render(request, 'orders/yookassa_success.html', {'order': order})
                elif payment.status in ['canceled', 'failed']:
                    order.status = 'cancelled'
                    order.save()
                    return redirect('orders:yookassa_cancel')
            except Exception as e:
                logger.error(f"Ошибка проверки платежа ЮKassa: {str(e)}")
        return render(request, 'orders/yookassa_pending.html', {'order': order})
    return redirect('main:home')

def yookassa_cancel(request):
    order_id = request.GET.get('order_id')
    if order_id:
        order = get_object_or_404(Order, id=order_id)
        order.status = 'cancelled'
        order.save()
        messages.error(request, "Платеж был отменен.")
        return render(request, 'orders/yookassa_cancel.html', {'order': order})
    return redirect('orders:checkout')