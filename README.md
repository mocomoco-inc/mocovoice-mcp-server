# mocoVoice MCP Server

mocoVoice MCP Server は Claude Desktop と連携して [mocoVoice](https://products.mocomoco.ai/mocoVoice) への書き起こしを実施、また書き起こし結果を確認することができる MCP Serverです。

## デモ動画

[![mocoVoice MCP Server Demo](https://img.youtube.com/vi/ES6Nc61Aefs/0.jpg)](https://www.youtube.com/watch?v=ES6Nc61Aefs)

> [!NOTE]
> mocoVoice MCP Serverはβ版として提供されているため、全ての機能が実装されていないことに注意してください。


## Tools

* **SHOW_USAGE**
    * mocoVoice MCP server の機能一覧を表示します

* **SHOW_AVAILABLE_FORMATS**
    * mocoVoice MCP server が対応している音声・動画ファイル形式を返却します

* **SHOW_AVAILABLE_FILES**
    * mocoVoice MCP server が利用できる音声・動画ファイル一覧を返却します
    * 利用できる音声・動画ファイル一覧は指定されたディレクトリ（フォルダー）配下のみです

* **START_TRANSCRIPTION_JOB**
    * 指定されたファイルで書き起こしジョブを起動します
    * ファイルの指定は絶対パスで行う必要があります
    * **書き起こしジョブが正常に開始された場合、利用枠が消費されます**

* **SHOW_TRANSCRIPTION_RESULT**
    * 書き起こしIDを指定して、書き起こし結果を取得して表示します

* **CHECK_TRANSCRIPTION_STATUSES**
    * 今までの書き起こし一覧を取得します


## 利用開始条件

- Docker
- Claude Desktop
- mocoVoice API KEY (READ / WRITE 権限が必要です)

Claude DesktopでのMCPサーバーの設定方法については、[MCP Quickstart Guide](https://modelcontextprotocol.io/quickstart/user)をご参照ください。

Claude Desktop の設定ファイル `claude_desktop_config.json` を開き、設定を記載します
- `<YOUR_DIR_PATH>` には書き起こしたい音声ファイルの入ったディレクトリを絶対パスで指定します
- `<YOUR_API_KEY>` には mocoVoice API KEY を設定します

```json
{
  "mcpServers": {
    "mocoVoice MCP Server": {
      "command": "docker",
      "args": [
        "run",
        "--pull", "always",
        "-i",
        "--rm",
        "--mount", "type=bind,src=<YOUR_DIR_PATH>,dst=/workspace",
        "-e", "MOCOVOICE_API_KEY",
        "-e", "MOCOVOICE_API_URL",
        "ghcr.io/mocomoco-inc/mocovoice-mcp-server"
      ],
      "env": {
        "MOCOVOICE_API_KEY": "<YOUR_API_KEY>",
        "MOCOVOICE_API_URL": "https://api.mocomoco.ai/api/v1"
      }
    }
  }
}
```


## 利用可能なファイル形式一覧

最大3GBまでのファイルアップロードに対応しています

- 音声
  * ".wav", ".mp3", ".m4a", ".caf", ".aiff", ".wma", ".flac", ".ogg", ".aac"

- 動画
  * ".avi", ".mp4", ".rmvb", ".flv", ".mov", ".wm"


## 料金について

本MCPサーバーの利用料金は、mocoVoice APIの利用料金として課金されます。書き起こしジョブの実行時にAPI利用料金が発生します。

無料枠を含めた詳細な料金情報については、[mocoVoice API 料金ページ](https://products.mocomoco.ai/mocoVoice-api)をご確認ください。

## 免責事項

> [!WARNING]
> 本ツールはMITライセンスに基づき、いかなる保証や公式のサポートを約束するものではありません。
> 機能をご確認の上、ご使用の際は自己責任でご利用ください。
