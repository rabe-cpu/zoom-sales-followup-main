const { chromium } = require('playwright');
const { createInterface } = require('node:readline/promises');
const { stdin: input, stdout: output } = require('node:process');
const { mkdir } = require('node:fs/promises');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const screenshotDir = path.join(__dirname, 'assets', 'screenshots');
const profileDir = path.join(root, '.playwright-profile', 'setup-capture');

const steps = [
  {
    file: '01_zoom_admin_roles.png',
    title: 'Zoom 管理者権限 / ロール確認',
    url: 'https://zoom.us/signin',
    note: 'Zoom Web Portalでログインし、Admin > User Management > Roles または Users へ移動。対象者がS2S AppとRecordingを扱える状態を表示する。',
  },
  {
    file: '02_zoom_recording_settings.png',
    title: 'Zoom 録画・文字起こし設定',
    url: 'https://zoom.us/account/setting?tab=recording',
    note: 'Account Management > Account Settings > Recording & Transcript。Cloud Recording と Create audio transcript がONの状態を表示する。',
  },
  {
    file: '03_zoom_s2s_app_credentials.png',
    title: 'Zoom S2S OAuth App 基本情報',
    url: 'https://marketplace.zoom.us/develop/create',
    note: 'Server-to-Server OAuth AppのBasic InformationまたはApp Credentials。Client Secretの値は絶対に表示しない。',
  },
  {
    file: '04_zoom_s2s_scopes.png',
    title: 'Zoom S2S OAuth App スコープ',
    url: 'https://marketplace.zoom.us/user/build',
    note: 'Scopes画面。ユーザー一覧read系と録画read系のスコープが入っている状態を表示する。',
  },
  {
    file: '05_zoom_recording_management.png',
    title: 'Zoom 録画一覧 / VTT確認',
    url: 'https://zoom.us/recording/management',
    note: 'Recording and Transcript Management。テスト録画が見え、Audio transcriptが生成済みとわかる画面を表示する。',
  },
  {
    file: '06_google_drive_output_folder.png',
    title: 'Google Drive 保存先フォルダ',
    url: 'https://drive.google.com/drive/my-drive',
    note: 'Routine出力用フォルダを表示する。URLのfolders以降がGOOGLE_DRIVE_FOLDER_IDになる。',
  },
  {
    file: '07_chatwork_room.png',
    title: 'Chatwork 通知先ルーム',
    url: 'https://www.chatwork.com/',
    note: '通知先ルームを表示する。Room IDの確認だけで、API tokenの値は表示しない。',
  },
  {
    file: '08_claude_routine_basic.png',
    title: 'Claude Routine 基本設定',
    url: 'https://code.claude.com/',
    note: 'Routine作成画面でRepository / Branch / Promptを入れる場所を表示する。',
  },
  {
    file: '09_claude_routine_env.png',
    title: 'Claude Routine 環境変数',
    url: 'https://code.claude.com/',
    note: 'Environment variables画面。値はマスク表示にして、変数名だけ確認できる状態を表示する。',
  },
  {
    file: '10_claude_routine_run_now.png',
    title: 'Claude Routine Run now / 実行ログ',
    url: 'https://code.claude.com/',
    note: 'Run now後の実行ログ。Step1からStep4まで進んでいることがわかる画面を表示する。',
  },
];

function selectedSteps() {
  const raw = process.env.CAPTURE_STEPS;
  if (!raw) return steps;
  const selected = new Set(
    raw
      .split(',')
      .map((value) => Number.parseInt(value.trim(), 10))
      .filter((value) => Number.isInteger(value) && value >= 1 && value <= steps.length)
  );
  return steps.filter((_, index) => selected.has(index + 1));
}

async function main() {
  await mkdir(screenshotDir, { recursive: true });
  const rl = createInterface({ input, output });
  const context = await chromium.launchPersistentContext(profileDir, {
    headless: false,
    viewport: { width: 1440, height: 1100 },
  });
  const page = await context.newPage();

  console.log('\nRoutine導入スクショ取得を開始します。');
  console.log('ログインはブラウザ上で手動で行ってください。パスワードやClient Secretの値は撮らないでください。');
  console.log('一部だけ撮る場合: CAPTURE_STEPS="2,6,8" NODE_PATH="$(npm root -g)" node docs/setup/capture_setup_screenshots.cjs');
  console.log('Enter: 撮影 / s: スキップ / q: 終了\n');

  const targets = selectedSteps();
  for (const step of targets) {
    const originalIndex = steps.findIndex((candidate) => candidate.file === step.file) + 1;
    console.log(`\n[${originalIndex}/${steps.length}] ${step.title}`);
    console.log(`保存先: ${path.relative(root, path.join(screenshotDir, step.file))}`);
    console.log(`確認: ${step.note}`);
    await page.goto(step.url, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((error) => {
      console.log(`初期URLを開けませんでした。ブラウザで手動移動してください: ${error.message}`);
    });

    const answer = (await rl.question('対象画面まで移動したらEnter。スキップは s、終了は q: ')).trim().toLowerCase();
    if (answer === 'q') break;
    if (answer === 's') continue;

    await page.screenshot({
      path: path.join(screenshotDir, step.file),
      fullPage: true,
    });
    console.log(`保存しました: ${path.relative(root, path.join(screenshotDir, step.file))}`);
  }

  await context.close();
  rl.close();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
