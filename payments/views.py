import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from .mpesa import stk_push

def normalize_phone(p):
    p = p.strip().replace("+", "").replace(" ", "")
    if p.startswith("0"):
        p = "254" + p[1:]
    return p

def home(request):
    if request.method == "POST":
        phone = normalize_phone(request.POST["phone"])
        amount = int(request.POST["amount"])
        payment = Payment.objects.create(phone=phone, amount=amount)
        try:
            res = stk_push(phone, amount)
            if res.get("ResponseCode") == "0":
                payment.checkout_request_id = res["CheckoutRequestID"]
            else:
                payment.status = "FAILED"
        except Exception:
            payment.status = "FAILED"
        payment.save()
        return redirect("status", pk=payment.pk)
    return render(request, "payments/home.html")

def status(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, "payments/status.html", {"payment": payment})

def status_json(request, pk):
    p = get_object_or_404(Payment, pk=pk)
    return JsonResponse({"status": p.status, "receipt": p.mpesa_receipt})

def history(request):
    return render(request, "payments/history.html",
                  {"payments": Payment.objects.order_by("-created_at")[:20]})

@csrf_exempt
def callback(request):
    data = json.loads(request.body)["Body"]["stkCallback"]
    try:
        payment = Payment.objects.get(checkout_request_id=data["CheckoutRequestID"])
    except Payment.DoesNotExist:
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
    if data["ResultCode"] == 0:
        items = {i["Name"]: i.get("Value") for i in data["CallbackMetadata"]["Item"]}
        payment.status = "SUCCESS"
        payment.mpesa_receipt = items.get("MpesaReceiptNumber", "")
    else:
        payment.status = "FAILED"
    payment.save()
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
