# 外国語と日本語を翻訳してチャットに投げるやつ

海外拠点のメンバーとお互いの母国語で会話するために作成。

以下自分用メモ。

## デプロイ手順

### 1.ChatWorkのアカウント準備

- ChatWorkアカウントを1つ準備。
- アカウントの[API利用を許可](https://developer.chatwork.com/ja/)

### 2.Googleの翻訳API準備

<details><summary>
Google cloud APIを使う場合
</summary>

https://cloud.google.com/translate/?hl=ja

安定して動かす場合はこっちを使う予定。</details>

<details><summary>出来るだけ無料で使う場合</summary>

https://qiita.com/satto_sann/items/be4177360a0bc3691fdf  
https://qiita.com/kimisyo/items/ff0ae2aae97e4d8e3f65  
あたりを参考にapps scriptを作っておく

デイリー5000件までの制限あり</details>


### 3.Lambda作成

AWS Lambdaでpythonのrequestsを使えるよう準備する。  
新規に関数を作成し、リポジトリ内のjv_translator.pyの内容をコピペ。  
トリガーはAPI GatewayでPOSTリクエストを受けられるようにする。

#### 環境変数

|  名前  |  内容  |
| ---- | ---- |
|  CW_HOOK_TOKEN  |  ChatWorkのWebhook設定から取得したtoken  |
|  CW_BOT_TO  |  ChatWorkでbotとして動かす予定のアカウントへtoした際の文字列(rx:[To:111111]テストアカウントさん)  |
|  API_URL  |  Googleの翻訳APIとして作成したapps scriptのURL  |
|  GOOGLE_APP_OAUTH_TOKEN  |  Googleの翻訳APIとして作成したapps scriptのOAuth token  |
|  CW_API_TOKEN  |  ChatWorkで発言するためのAPI token  |

### 4.ChatworkのWebhook

容易したアカウントのWebhookを設定する。hook先は先程作ったLambdaのAPI Gateway。  
かなり端折ってるがこれで最低限の準備は終わり。

## 使い方
用意したアカウントにtoで翻訳したい文章を送るだけ。  
