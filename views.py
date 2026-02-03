from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import razorpay
import qrcode
import base64
from io import BytesIO

def payment_page(request):
    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        amount = 50000  # ₹500

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        payment_url = f"https://rzp.io/i/{order['id']}"

        qr = qrcode.make(payment_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render(request, "payment.html", {
            "qr_code": qr_base64,
            "order_id": order["id"],
            "amount": amount,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        # 💡 Is line se error hamesha browser me dikhega
        return HttpResponse(f"ERROR: {e}")


def success(request):
    return HttpResponse("Payment Success")


def failed(request):
    return HttpResponse("Payment Failed")
def payment(request):
    ...

