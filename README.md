# .Chain()
.Chain()は、リモートユーザが気軽に質問ができて、答えが返ってくる、質問サイトです。
.Chain()を使ってユーザが質問をすれば、コンピュータが自動的に質問の宛先を決めて送ってくれるため、宛先に頭を悩ませることはありません。また、他の質問サイトとは違い、宛先は一人だけなので、どんな質問でも気軽に質問ができます。
一方、質問を受け取った回答者にはあなただけに質問が送られてきますので、制限時間に是非回答してあげましょう。もちろんパスも選択可能です。忙しくて質問が来ているかチェックできない場合も、自動的にパスになりますので、安心です。

さっそく使ってみましょう！（公式サイトリンク）

# 目次
* [ユーザー向け](#ユーザー向け)
* [デベロッパー向け](#デベロッパー向け)
* [今後の追加機能](#今後の追加機能)
* [バージョン情報](#バージョン情報)
* [ライセンス](#ライセンス)

#ユーザー向け

##対象ユーザ
* リモートワークで働いており、会社の同僚の顔が見えず質問がしにくい人
* 大組織で働いているが、他の部署とのつながりがほとんどない人

##利用シーン（イラスト）
* 分かる人ならば誰でもいいから答えて欲しいという質問をしたいとき
顔が見えないリモートワークにおいて、他の同僚の忙しさは気になりますよね。分かる人ならば誰でもいいから答えて欲しいという質問を会社の同僚にメールで送りつけるのは気がひけます。一方で、リモートワークでよく使われているチャットや社内SNSで質問しても誰からも反応なし、という経験はありませんか？.Chain()はあなたの質問の宛先をコンピュータが自動的に決めてくれます。
* 他の部署を含めた人間関係や専門分野を知りたいとき
組織が大きくなると、自分の部署の人のことはよくわかるのに他部署の人
はわからないことが多いものです。.Chain()はユーザによる質問のやりとりと、質問に付加されるタグによって、各ユーザの興味や人間関係を可視化して見ることができます。この情報により新しい人間関係が生まれるかもしれません。

##アプリイメージ
![アプリイメージ](https://github.com/koga-yatsushiro/one_month/wiki/images/app_image.png)

##特長
* 宛先の自動選別
![宛先の自動選別](https://github.com/koga-yatsushiro/one_month/wiki/images/dotchain_auto_select.png)
  
* パス
![パス](https://github.com/koga-yatsushiro/one_month/wiki/images/dotchain_pass.png)
  
* ネットワーク図
![ネットワーク図](https://github.com/koga-yatsushiro/one_month/wiki/images/dotchain_network.png)

* AIによる自動返信
![AIによる自動返信](https://github.com/koga-yatsushiro/one_month/wiki/images/dotchain_ai.png)

##はじめてみましょう

1. 公式サイトにアクセスしてください。アカウントを新規作成するか、Googleアカウントでのログインが可能です。
![ログイン](https://github.com/koga-yatsushiro/one_month/wiki/images/login.png)

2. トップページにははじめには何も質問がありませんが、自分で質問を投稿するか自分宛に来ると、以下のように一覧でされます。質問カードのの表示色の意味は「仕様詳細-質問カードの表示フロー」を参照してください。
![トップページ](https://github.com/koga-yatsushiro/one_month/wiki/images/top.png)
  
3. ログイン後、プロフィールページの情報を更新してください
![プロフィール](https://github.com/koga-yatsushiro/one_month/wiki/images/profile.png)
  
4. 質問しましょう
![質問作成](https://github.com/koga-yatsushiro/one_month/wiki/images/question_new.png)
  
5. 自分宛の質問に答えてみよう
![返信](https://github.com/koga-yatsushiro/one_month/wiki/images/reply_new.png)
  
6. ネットワーク図を見てみよう
    * プロフィールページ下部にアプリ利用者全体のネットワーク図が表示されます
    * 自分と同じ興味を持っている人やよく質問に答えている人がわかりますので、次はその人に直接聞いてみましょう！
![ネットワーク図](https://github.com/koga-yatsushiro/one_month/wiki/images/network.png)

##仕様詳細
* 動作フロー  
![動作フロー](https://github.com/koga-yatsushiro/one_month/wiki/images/action_flow.png)
  
* 質問カードの表示フロー  
[こちら](https://github.com/koga-yatsushiro/one_month/wiki/%E8%B3%AA%E5%95%8F%E3%82%AB%E3%83%BC%E3%83%89%E3%81%AE%E8%A1%A8%E7%A4%BA%E3%83%95%E3%83%AD%E3%83%BC)のwikiのページを参照してください
  
* コンピュータによる受信者の選択基準  
[こちら](https://github.com/koga-yatsushiro/one_month/wiki/%E3%82%B3%E3%83%B3%E3%83%94%E3%83%A5%E3%83%BC%E3%82%BF%E3%81%AB%E3%82%88%E3%82%8B%E5%8F%97%E4%BF%A1%E8%80%85%E3%81%AE%E9%81%B8%E6%8A%9E%E5%9F%BA%E6%BA%96)のwikiのページを参照してください
  
* コンピュータによる自動パス機能(非同期処理)  
[こちら](https://github.com/koga-yatsushiro/one_month/wiki/%E9%9D%9E%E5%90%8C%E6%9C%9F%E5%87%A6%E7%90%86)のwikiのページを参照してください
  
* タグの役割  
[こちら](https://github.com/koga-yatsushiro/one_month/wiki/%E3%82%BF%E3%82%B0%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6)のwikiのページを参照してください
  
#デベロッパー向け
## アーキテクチャ図
![アーキテクチャ図](https://github.com/koga-yatsushiro/one_month/wiki/images/architecture.png)

## ローカル開発環境の構築
* インストール
    * OS: Windows7
    * 言語: Python3.4
    * DB: PostgreSQL9.4 (windowsインストーラ使用を推奨)
    * 以下、Pythonモジュール。以下のコマンドでインストールしてください
    ※もし、requirements.txt内のpsycopg2==2.6.1の行でエラーが出た場合は、psycopg2==2.6.1の行は削除して、[ここ](http://initd.org/psycopg/)のwindowsインストーラを使ってインストールしてください

```bash
pip install -r requirements.txt
```

* ローカルで起動  
3つのターミナルを開き、以下のコマンドを入力し、起動してください。

```bash
python manage.py runserver
```

```bash
python manage.py celerybeat
```

```bash
python manage.py celeryd
```

その後、http://127.0.0.1:8000/dotchain
にアクセスして、トップページが表示されることを確認してください。


## 既知のバグ
[こちら](https://github.com/koga-yatsushiro/one_month/issues)のwikiのページを参照してください

#今後の追加機能
* 質問だけでなく、依頼や会議など機能拡張の開発
* 他ユーザのプロフィールの表示
* 質問文からのタグの抽出
* ネットワーク図に基づいた受信者選別
* ネットワークの抽出方法の改良


#バージョン情報
* 2015.07.08 v1.0 Release
    * 新規作成
* 2015.07.30 v1.1 Release
    * AIによる自動返信機能追加
    * UI（トップ画面、ログイン画面、ネットワーク図など）修正

#ライセンス
Apache License, Version 2.0  
http://www.apache.org/licenses/LICENSE-2.0
