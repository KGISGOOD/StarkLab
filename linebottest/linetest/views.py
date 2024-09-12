from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi,WebhookParser
from linebot.exceptions import InvalidSignatureError,LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META.get('HTTP_X_LINE_SIGNATURE', None)
        if signature is None:
            return HttpResponseBadRequest("Missing X-Line-Signature header")
        
        body = request.body.decode('utf-8')
        print(f"Request body: {body}")
        print(f"Signature: {signature}")

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            print("Invalid signature error")
            return HttpResponseForbidden()
        except LineBotApiError as e:
            print(f"LineBotApiError: {e}")
            return HttpResponseBadRequest()
        
        for event in events:
            if isinstance(event, MessageEvent):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=event.message.text)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

    


