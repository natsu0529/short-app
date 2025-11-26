# short-app

## Testing

このプロジェクトでは API サーバー用コンテナとは別に、テスト専用コンテナ（`api_tests`）で `pytest` を実行します。

1. 先に DB を起動します。
   ```bash
   docker compose up -d db
   ```
2. テスト専用コンテナをワンショットで起動し、`pytest` を実行します。
   ```bash
   docker compose run --rm api_tests
   ```

API サーバー内で直接テストを回す必要は無く、常に `api_tests` サービスを経由してテストを実行してください。
