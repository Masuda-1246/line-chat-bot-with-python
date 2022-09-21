from http import client
from inspect import Attribute
import os
from urllib import response
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage,
)
import boto3

handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
client = boto3.client('rekognition')

def lambda_handler(event, context):
    headers = event["headers"]
    body = event["body"]

    # get X-Line-Signature header value
    signature = headers['x-line-signature']

    # handle webhook body
    handler.handle(body, signature)

    return {"statusCode": 200, "body": "OK"}


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    input_text = event.message.text

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=input_text))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = "/tmp/sent-message.png"
    with open(file_path, "wb") as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    with open(file_path, "rb") as fd:
        sent_image_binary = fd.read()
        response = client.detect_faces(
            Image={"Bytes":sent_image_binary},
            Attributes=['ALL','DEFAULT']
        )
    response = response['FaceDetails'][0]['Emotions'][0]
    emotion_confidence = round(float(response['Confidence']))
    emotion_type = response['Type']
    emotion = ""
    if emotion_type == 'HAPPY':
        emotion = '笑顔'
    elif emotion_type == 'SAD':
        emotion = '泣き顔'
    elif emotion_type == 'CALM':
        emotion = '落ち着き顔'
    elif emotion_type == 'DISGUSTED':
        emotion = 'うんざり顔'
    elif emotion_type == 'SURPRISED':
        emotion = '驚き顔'
    elif emotion_type == 'ANGRY':
        emotion = '落ち着き顔'
    text = "{}% {}".format(emotion_confidence, emotion)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text))
    os.remove(file_path)