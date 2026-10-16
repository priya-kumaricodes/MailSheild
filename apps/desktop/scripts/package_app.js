/**
 * Packages MailShield into a standalone macOS Application Bundle (MailShield.app)
 * and creates a distributable zip archive.
 */

const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const desktopRoot = path.resolve(__dirname, '..');
const pkg = JSON.parse(fs.readFileSync(path.join(desktopRoot, 'package.json'), 'utf-8'));
const appVersion = pkg.version || '2.1.0';
const projectRoot = path.resolve(desktopRoot, '../..');
const electronApp = path.join(desktopRoot, 'node_modules/electron/dist/Electron.app');
const distDir = path.join(desktopRoot, 'dist');
const targetApp = path.join(distDir, 'MailShield.app');
const targetZip = path.join(distDir, `MailShield-${appVersion}-mac-arm64.zip`);

function run(cmd, args, opts = {}) {
  console.log(`> ${cmd} ${args.join(' ')}`);
  cp.execFileSync(cmd, args, { stdio: 'inherit', ...opts });
}

async function packageApp() {
  console.log('=== Building MailShield Desktop Standalone Distributable ===');

  if (!fs.existsSync(electronApp)) {
    throw new Error(`Electron prebuilt binary not found at ${electronApp}. Run node install.js first.`);
  }

  // 1. Remove previous build artifact if exists
  if (fs.existsSync(targetApp)) {
    console.log(`Removing previous build at ${targetApp}...`);
    fs.rmSync(targetApp, { recursive: true, force: true });
  }

  // 2. Copy base Electron.app to MailShield.app preserving symlinks and permissions
  console.log(`Copying base Electron.app to ${targetApp}...`);
  run('ditto', [electronApp, targetApp]);

  // 3. Prepare Contents/Resources/app
  const appResourceDir = path.join(targetApp, 'Contents/Resources/app');
  fs.mkdirSync(appResourceDir, { recursive: true });

  // Copy desktop package.json, dist/main.js, dist/preload.js
  fs.copyFileSync(path.join(desktopRoot, 'package.json'), path.join(appResourceDir, 'package.json'));
  
  const appDistDir = path.join(appResourceDir, 'dist');
  fs.mkdirSync(appDistDir, { recursive: true });
  fs.copyFileSync(path.join(distDir, 'main.js'), path.join(appDistDir, 'main.js'));
  fs.copyFileSync(path.join(distDir, 'preload.js'), path.join(appDistDir, 'preload.js'));

  // Copy web frontend bundle
  const webDist = path.join(projectRoot, 'apps/web/dist');
  if (fs.existsSync(webDist)) {
    console.log(`Bundling web frontend assets from ${webDist}...`);
    const appWebDist = path.join(appResourceDir, 'web/dist');
    fs.mkdirSync(appWebDist, { recursive: true });
    run('ditto', [webDist, appWebDist]);
  } else {
    console.warn(`Warning: Web dist not found at ${webDist}. Run npm --prefix apps/web run build first.`);
  }

  // Copy standalone native backend binary
  const distServer = path.join(projectRoot, 'dist/mailshield_server');
  const targetBackendBin = path.join(targetApp, 'Contents/Resources/backend_bin');
  if (fs.existsSync(distServer)) {
    console.log(`Bundling standalone native backend executable from ${distServer}...`);
    fs.mkdirSync(targetBackendBin, { recursive: true });
    run('ditto', [distServer, targetBackendBin]);
    const binFile = path.join(targetBackendBin, 'mailshield_server');
    if (fs.existsSync(binFile)) {
      fs.chmodSync(binFile, 0o755);
      console.log(`Set executable permissions on ${binFile}`);
    }
  } else {
    console.warn(`Warning: Standalone backend binary not found at ${distServer}!`);
  }

  // Also copy backend code and ML modules as secondary fallback
  const backendDir = path.join(projectRoot, 'backend');
  const appBackendDir = path.join(appResourceDir, 'backend');
  console.log(`Bundling fallback backend service from ${backendDir}...`);
  fs.mkdirSync(appBackendDir, { recursive: true });
  run('ditto', [backendDir, appBackendDir]);

  const mlDir = path.join(projectRoot, 'ml');
  const appMlDir = path.join(appResourceDir, 'ml');
  console.log(`Bundling fallback ML modules and model artifacts from ${mlDir}...`);
  fs.mkdirSync(path.join(appMlDir, 'src'), { recursive: true });
  run('ditto', [path.join(mlDir, 'src'), path.join(appMlDir, 'src')]);
  fs.mkdirSync(path.join(appMlDir, 'artifacts'), { recursive: true });
  run('ditto', [path.join(mlDir, 'artifacts'), path.join(appMlDir, 'artifacts')]);
  fs.mkdirSync(path.join(appMlDir, 'data'), { recursive: true });
  fs.copyFileSync(path.join(mlDir, 'data/seed_corpus.json'), path.join(appMlDir, 'data/seed_corpus.json'));
  if (fs.existsSync(path.join(mlDir, 'data/multilingual_corpus.json'))) {
    fs.copyFileSync(path.join(mlDir, 'data/multilingual_corpus.json'), path.join(appMlDir, 'data/multilingual_corpus.json'));
  }

  // 4. Update Info.plist and rename executable to MailShield
  const oldExec = path.join(targetApp, 'Contents/MacOS/Electron');
  const newExec = path.join(targetApp, 'Contents/MacOS/MailShield');
  if (fs.existsSync(oldExec)) {
    fs.renameSync(oldExec, newExec);
    console.log('Renamed Contents/MacOS/Electron -> MailShield.');
  }

  const plistPath = path.join(targetApp, 'Contents/Info.plist');
  if (fs.existsSync(plistPath)) {
    let plistContent = fs.readFileSync(plistPath, 'utf-8');
    plistContent = plistContent.replace(/<key>CFBundleDisplayName<\/key>\s*<string>[^<]*<\/string>/, '<key>CFBundleDisplayName</key>\n\t<string>MailShield</string>');
    plistContent = plistContent.replace(/<key>CFBundleName<\/key>\s*<string>[^<]*<\/string>/, '<key>CFBundleName</key>\n\t<string>MailShield</string>');
    plistContent = plistContent.replace(/<key>CFBundleIdentifier<\/key>\s*<string>[^<]*<\/string>/, '<key>CFBundleIdentifier</key>\n\t<string>com.mailshield.desktop</string>');
    plistContent = plistContent.replace(/<key>CFBundleExecutable<\/key>\s*<string>[^<]*<\/string>/, '<key>CFBundleExecutable</key>\n\t<string>MailShield</string>');
    plistContent = plistContent.replace(/<key>CFBundleShortVersionString<\/key>\s*<string>[^<]*<\/string>/, `<key>CFBundleShortVersionString</key>\n\t<string>${appVersion}</string>`);
    plistContent = plistContent.replace(/<key>CFBundleVersion<\/key>\s*<string>[^<]*<\/string>/, `<key>CFBundleVersion</key>\n\t<string>${appVersion}</string>`);
    fs.writeFileSync(plistPath, plistContent);
    console.log(`Updated Info.plist bundle metadata to v${appVersion}.`);
  }

  // 5. Re-sign bundle ad-hoc
  console.log('Signing MailShield.app bundle ad-hoc...');
  run('codesign', ['--force', '--deep', '--sign', '-', targetApp]);

  // 6. Verify signature
  console.log('Verifying code signature...');
  run('codesign', ['-v', targetApp]);

  // 7. Create compressed distributable zip archive
  console.log(`Creating distributable archive ${targetZip}...`);
  if (fs.existsSync(targetZip)) {
    fs.unlinkSync(targetZip);
  }
  run('ditto', ['-c', '-k', '--sequesterRsrc', '--keepParent', targetApp, targetZip]);

  const stats = fs.statSync(targetZip);
  console.log(`\nSUCCESS: MailShield Desktop standalone distributable created!`);
  console.log(`- Application Bundle: ${targetApp}`);
  console.log(`- Distributable Archive: ${targetZip} (${(stats.size / (1024 * 1024)).toFixed(2)} MB)`);
}

packageApp().catch((err) => {
  console.error('Packaging failed:', err.message);
  process.exit(1);
});

