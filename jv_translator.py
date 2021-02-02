import requests
import unicodedata
import json
import base64
import os
import hashlib
import hmac


def is_japanese(string):
    """簡易日本語判定"""
    for ch in string:
        try:
            name = unicodedata.name(ch)
            if "CJK UNIFIED" in name or "HIRAGANA" in name or "KATAKANA" in name:
                return True
        except Exception as e:
            print(e)
            continue

    return False


def lambda_handler(event, context):
    """cwから渡された文字列をGoogle翻訳に通し、結果をcwに返す"""
    #  cw署名検証
    secret_key = base64.b64decode(os.environ['CW_HOOK_TOKEN'])
    digest = hmac.new(secret_key, event['body'].encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    if signature != event['headers']['X-ChatWorkWebhookSignature'].encode():
        return {
            'statusCode': 403,
            'body': 'forbidden'
        }

    # cwから渡された値を取り出す
    cw_event = json.loads(event['body'])
    account_id = cw_event['webhook_event']['from_account_id']
    room_id = cw_event['webhook_event']['room_id']
    content = cw_event['webhook_event']['body']
    if os.environ['CW_BOT_TO'] not in content:
        return{
            'statusCode': 200,
            'body': 'not reply'
        }
    content = content.replace(os.environ['CW_BOT_TO'] + '\n', '')
    content = content.replace(os.environ['CW_BOT_TO'], '')
    # 日本の人にtoを送ると日本語判定されてしまうので、toの部分を消す
    while content.find('[To:') > -1:
        # cwでToを送ると"[To:{userId}]名字 名前さん"がデフォで入る
        content = content[content.find('さん')+2:]
        if content[0] == '\n':
            content = content[1:]

    # Google Apps Scriptに作った自分用の翻訳APIを呼ぶための認証
    api_url = os.environ['API_URL']
    headers = {"Authorization": f"Bearer {os.environ['GOOGLE_APP_OAUTH_TOKEN']}"}

    # 何語から何語へ変換するのか指定
    # 参考: https://cloud.google.com/translate/docs/languages?hl=ja
    jp_flag = is_japanese(content)
    params = {
        'text': content,
        'source': 'ja' if jp_flag else 'en',
        'target': 'en' if jp_flag else 'ja'
    }

    r_post = requests.post(api_url, headers=headers, data=params)
    txt = json.loads(r_post.text)['text']
    cw_api_token = os.environ['CW_API_TOKEN']

    url = f'https://api.chatwork.com/v2/rooms/{room_id}/messages'
    headers = {'X-ChatWorkToken': cw_api_token}
    params = {'body': f'[piconname:{account_id}]:\n{txt}'}
    res = requests.post(url, headers=headers, data=params)

    return {
        'statusCode': res.status_code,
        'body': 'end'
    }
