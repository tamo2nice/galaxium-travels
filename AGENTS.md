# AGENTS.md

このファイルは、このリポジトリでコードを扱う際のエージェント向けガイダンスを提供します。

## 重要な非標準パターン

### バックエンド (booking_system_backend/)
- **MCP サーバーは FastAPI アプリの前に作成必須**: `server.py` で MCP インスタンスを FastAPI より先に作成しないとライフサイクルの結合が失敗する
- **テストは monkeypatch で SessionLocal を上書き**: `conftest.py` で `db_module.SessionLocal` と `server.SessionLocal` の両方をパッチする必要がある
- **booking.book_flight() は name パラメータで検証**: user_id だけでなく name も必須で、DB の name と一致しない場合は NAME_MISMATCH エラーを返す
- **ErrorResponse は Union 型で返却**: サービス層の関数は `BookingOut | ErrorResponse` を返すため、呼び出し側で型チェックが必要
- **datetime は ISO 文字列として保存**: `booking_time` は `datetime.utcnow().isoformat()` で文字列として保存（SQLite の制約）

### フロントエンド (booking_system_frontend/)
- **API エラーは interceptor で ErrorResponse に変換**: axios interceptor がネットワークエラーを `ErrorResponse` 型に統一する
- **isErrorResponse() でレスポンス判定**: API レスポンスが成功かエラーかを `success === false` で判定するヘルパー関数を使用
- **型定義は snake_case**: バックエンドの Python スキーマに合わせて `flight_id`, `user_id` など snake_case を使用（TypeScript の慣例に反する）

## テスト実行

### バックエンド単体テスト
```bash
cd booking_system_backend
pytest                    # 全テスト実行
pytest tests/test_services.py  # サービス層のみ
pytest tests/test_rest.py      # REST API のみ
```

### フロントエンドビルド検証
```bash
cd booking_system_frontend
npm run build            # TypeScript コンパイル + Vite ビルド