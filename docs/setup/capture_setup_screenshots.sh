#!/usr/bin/env bash
set -euo pipefail

SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$SETUP_DIR/assets/screenshots"
mkdir -p "$OUT_DIR"

if [[ $# -gt 0 ]]; then
  STEPS="$*"
else
  STEPS="${CAPTURE_STEPS:-6 7 8 9 10}"
fi

step_title() {
  case "$1" in
    1) echo "Zoom 管理者権限 / ロール確認" ;;
    2) echo "Zoom 録画・文字起こし設定" ;;
    3) echo "Zoom S2S OAuth App 基本情報" ;;
    4) echo "Zoom S2S OAuth App スコープ" ;;
    5) echo "Zoom 録画一覧 / VTT確認" ;;
    6) echo "Google Drive 保存先フォルダ" ;;
    7) echo "Chatwork 通知先ルーム" ;;
    8) echo "Claude Routine 基本設定" ;;
    9) echo "Claude Routine 環境変数" ;;
    10) echo "Claude Routine Run now / 実行ログ" ;;
    *) echo "Unknown" ;;
  esac
}

step_file() {
  case "$1" in
    1) echo "01_zoom_admin_roles.png" ;;
    2) echo "02_zoom_recording_settings.png" ;;
    3) echo "03_zoom_s2s_app_credentials.png" ;;
    4) echo "04_zoom_s2s_scopes.png" ;;
    5) echo "05_zoom_recording_management.png" ;;
    6) echo "06_google_drive_output_folder.png" ;;
    7) echo "07_chatwork_room.png" ;;
    8) echo "08_claude_routine_basic.png" ;;
    9) echo "09_claude_routine_env.png" ;;
    10) echo "10_claude_routine_run_now.png" ;;
    *) echo "" ;;
  esac
}

echo
echo "通常ブラウザ用スクショ取得を開始します。"
echo "Chromeなどログイン済みのブラウザで対象画面を開き、対象ウィンドウだけをクリックして撮影します。"
echo "パスワード、Client Secret、API token、refresh tokenは画面に出さないでください。"
echo

for step in $STEPS; do
  file="$(step_file "$step")"
  if [[ -z "$file" ]]; then
    echo "skip: unknown step $step"
    continue
  fi
  path="$OUT_DIR/$file"
  echo "[$step] $(step_title "$step")"
  echo "保存先: docs/setup/assets/screenshots/$file"
  read -r -p "対象画面を通常ブラウザで開いたらEnter。スキップは s、終了は q: " answer
  case "$answer" in
    q|Q) exit 0 ;;
    s|S) echo "skipped"; echo; continue ;;
  esac
  echo "撮影したいブラウザウィンドウをクリックしてください。Escでキャンセルできます。"
  screencapture -i -w "$path"
  if [[ -f "$path" ]]; then
    echo "保存しました: docs/setup/assets/screenshots/$file"
  else
    echo "保存されませんでした。"
  fi
  echo
done

echo "完了しました。"
