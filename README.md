# hatebu-importer

[はてなブックマーク](https://b.hatena.ne.jp/)はインポート機能を作る気がなさそうなので、ブックマーク形式でエクスポートした HTML ファイルから、API を使用して一気にインポートすることにしました。

## Requirements

- Python 3.11
- Pipenv

## Usage

### 1. ブックマークをエクスポートする

インポート元のアカウントでログインし、[はてなブックマークのエクスポート](https://b.hatena.ne.jp/-/my/config/data_management)から、ブックマークをエクスポートします。
エクスポートしたファイルをプロジェクトのルートに配置します。

### 2. OAuth アクセスを有効にする

インポート先のアカウントでログインし、[はてなブックマークのアプリケーション設定](https://www.hatena.ne.jp/oauth/develop)から、OAuth アクセスを有効にします。アクセスを有効にすると、OAuth Consumer Key と OAuth Consumer Secret が発行されます。

### 3. 環境変数を設定する

`.env` ファイルを作成し環境変数を設定します。`.env.example`を参考にしてください。

### 4. スクリプトを実行する

```bash
$ pipenv install
$ pipenv shell
$ python src/main.py
```

### 5. 認証画面から verifier を取得する

ターミナルに表示されるリンクをクリックして、認証画面に移動します。認証画面で「許可する」をクリックすると、verifier が表示されます。verifier をコピーしてターミナルに貼り付けてください。認証に問題がなければ、インポートを開始します。

## Note

インポート先のアカウントでブックマークを非公開にしていた場合は追加の設定が必要になります。

- アプリケーション設定で`write_private`にチェックを入れる
- `src/main.py`の`scope`を`write_private`に変更する

## Reference

- https://developer.hatena.ne.jp/ja/documents/auth/apis/oauth/consumer
- https://developer.hatena.ne.jp/ja/documents/nano/apis/oauth
