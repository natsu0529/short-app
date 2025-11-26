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

## Ranking metrics & counters

- `post.like_count` は投稿に付いたいいね数を表し、いいね/いいね解除時に API 層で増減させます。
- `accounts_userstats` テーブルは各ユーザの集計値を保持します（経験値、総獲得いいね、獲得/送信済みいいね数、フォロワー/フォロー数、投稿数など）。
- 経験値は投稿作成 (`+10`)、いいねを受け取る (`+5` × 件数)、いいねを送る (`+2` × 件数) のイベントで `UserStats` 経由で付与し、100XP ごとに `CustomUser.user_level` が 1 ずつ上がる仕様です。
- フォロー/アンフォロー時には `UserStats.update_follow_counts()` を使って `follower_count` と `following_count` を同期させます。
- これらの値はランキング API（最新・人気・フォロー中タイムラインやランキング 4 タブ）で並び替えやフィルタリングに使用してください。

## Timeline API

- エンドポイント: `GET /api/timeline/`
- クエリパラメータ
  - `tab`: `latest` (既定) / `popular` / `following`
  - `page`: `1` から始まるページ番号
  - `page_size`: 1〜100（既定 20）
- レスポンスは DRF のページネーション形式（`count`, `next`, `previous`, `results`）。`results` は `PostSerializer` なので `like_count` や投稿者情報が含まれます。
- `tab=latest`: 全投稿を作成日時の降順で返却。
- `tab=popular`: 直近24時間 (`created_at >= now - 24h`) の投稿を `like_count` → `time` の優先順位で返却。
- `tab=following`: 認証ユーザがフォローしているユーザの投稿のみを `-time` で返却。未ログインなら空配列。
