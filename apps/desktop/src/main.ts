import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import * as net from 'net';
import { ChildProcess, spawn } from 'child_process';
import * as http from 'http';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;
let backendPort = 8000;

function getAvailablePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (!address || typeof address === 'string') {
        server.close(() => reject(new Error('Failed to obtain server address')));
        return;
      }
      const port = address.port;
      server.close((err) => {
        if (err) reject(err);
        else resolve(port);
      });
    });
  });
}

function checkBackendHealth(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${port}/api/v1/health`, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1200, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForBackend(port: number, maxAttempts = 60, intervalMs = 500): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    const isHealthy = await checkBackendHealth(port);
    if (isHealthy) return true;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}

function findProjectRoot(): string {
  if (process.env.MAILSHIELD_ROOT_DIR && fs.existsSync(process.env.MAILSHIELD_ROOT_DIR)) {
    return process.env.MAILSHIELD_ROOT_DIR;
  }
  let currentDir = __dirname;
  for (let i = 0; i < 10; i++) {
    if (fs.existsSync(path.join(currentDir, 'backend/app/main.py'))) {
      return currentDir;
    }
    const parent = path.dirname(currentDir);
    if (parent === currentDir) break;
    currentDir = parent;
  }
  return path.resolve(__dirname, '../../..');
}

function getBackendExecutable(rootDir: string): { type: 'binary' | 'python'; execPath: string } {
  // 1. Packaged location inside Electron app bundle: Contents/Resources/backend_bin/mailshield_server
  if (process.resourcesPath) {
    const bundledBin = path.join(process.resourcesPath, 'backend_bin', 'mailshield_server');
    if (fs.existsSync(bundledBin)) {
      return { type: 'binary', execPath: bundledBin };
    }
  }

  // 2. Relative to repo dist/mailshield_server/mailshield_server (during dev or after pyinstaller)
  const localDistBin = path.resolve(__dirname, '../../../dist/mailshield_server/mailshield_server');
  if (fs.existsSync(localDistBin)) {
    return { type: 'binary', execPath: localDistBin };
  }
  const rootDistBin = path.resolve(rootDir, 'dist/mailshield_server/mailshield_server');
  if (fs.existsSync(rootDistBin)) {
    return { type: 'binary', execPath: rootDistBin };
  }

  // 3. Fallback to python for dev/test environments
  if (process.env.MAILSHIELD_PYTHON_PATH && fs.existsSync(process.env.MAILSHIELD_PYTHON_PATH)) {
    return { type: 'python', execPath: process.env.MAILSHIELD_PYTHON_PATH };
  }
  const bundledVenv = path.join(rootDir, '.venv/bin/python');
  if (fs.existsSync(bundledVenv)) {
    return { type: 'python', execPath: bundledVenv };
  }
  const repoVenv = path.resolve(__dirname, '../../../../../../.venv/bin/python');
  if (fs.existsSync(repoVenv)) {
    return { type: 'python', execPath: repoVenv };
  }
  return { type: 'python', execPath: 'python3' };
}

function startBackendService(port: number): void {
  backendPort = port;
  const rootDir = findProjectRoot();
  const backendTarget = getBackendExecutable(rootDir);

  const userDataPath = app.getPath('userData');
  if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
  }
  const dbPath = path.join(userDataPath, 'mailshield_desktop.db');

  console.log(`Starting local backend service [${backendTarget.type}] from ${backendTarget.execPath} on 127.0.0.1:${port}...`);
  console.log(`Database target: ${dbPath}`);

  if (backendTarget.type === 'binary') {
    const bundledArtifacts = process.resourcesPath
      ? path.join(process.resourcesPath, 'backend_bin', '_internal', 'ml', 'artifacts')
      : path.join(rootDir, 'ml/artifacts');

    const args = [
      '--host', '127.0.0.1',
      '--port', String(port),
      '--database-url', `sqlite:///${dbPath}`,
    ];
    if (fs.existsSync(bundledArtifacts)) {
      args.push('--artifacts-dir', bundledArtifacts);
    }

    backendProcess = spawn(backendTarget.execPath, args, {
      cwd: path.dirname(backendTarget.execPath),
      env: {
        ...process.env,
        DATABASE_URL: `sqlite:///${dbPath}`,
        MAILSHIELD_MODE: 'desktop',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } else {
    // Python fallback
    const env = {
      ...process.env,
      PYTHONPATH: `${rootDir}:${rootDir}/ml/src`,
      MAILSHIELD_MODE: 'desktop',
      DATABASE_URL: `sqlite:///${dbPath}`,
      ARTIFACTS_DIR: path.join(rootDir, 'ml/artifacts'),
      PORT: String(port),
    };

    backendProcess = spawn(
      backendTarget.execPath,
      ['-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', String(port)],
      {
        cwd: rootDir,
        env,
        stdio: ['ignore', 'pipe', 'pipe'],
      }
    );
  }

  backendProcess.stdout?.on('data', (d) => {
    console.log(`[Backend]: ${d.toString().trim()}`);
  });

  backendProcess.stderr?.on('data', (d) => {
    console.error(`[Backend ERR]: ${d.toString().trim()}`);
  });

  backendProcess.on('exit', (code, signal) => {
    console.log(`Backend process terminated with code ${code}, signal ${signal}`);
  });
}

function isProcessAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function stopBackendService(): void {
  if (backendProcess && !backendProcess.killed) {
    console.log('Terminating local backend process...');
    try {
      const pid = backendProcess.pid;
      backendProcess.kill('SIGTERM');
      if (pid) {
        setTimeout(() => {
          if (isProcessAlive(pid)) {
            console.warn('Backend process still alive after SIGTERM, sending SIGKILL...');
            try {
              process.kill(pid, 'SIGKILL');
            } catch {}
          }
        }, 2000);
      }
    } catch (e) {
      console.error('Error stopping backend process:', e);
    }
    backendProcess = null;
  }
}

async function createWindow(): Promise<void> {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#080c14',
    title: 'MailShield — Explainable Spam Classification (Offline)',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      additionalArguments: [`--backend-port=${backendPort}`],
    },
  });

  // Restrict navigation
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));

  // Load the web app
  let distHtml = path.resolve(__dirname, '../../web/dist/index.html');
  if (!fs.existsSync(distHtml)) {
    distHtml = path.resolve(__dirname, '../web/dist/index.html');
  }
  if (!fs.existsSync(distHtml)) {
    distHtml = path.resolve(process.resourcesPath || '', 'app/web/dist/index.html');
  }

  if (process.env.NODE_ENV === 'development') {
    await mainWindow.loadURL('http://localhost:5173');
  } else {
    await mainWindow.loadFile(distHtml);
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.handle('get-app-version', () => app.getVersion());
ipcMain.handle('get-backend-port', () => backendPort);
ipcMain.handle('get-api-base', () => `http://127.0.0.1:${backendPort}/api/v1`);
ipcMain.handle('check-backend-health', async () => checkBackendHealth(backendPort));
ipcMain.handle('open-external', async (_, url: string) => {
  if (url && (url.startsWith('https://') || url.startsWith('http://'))) {
    await shell.openExternal(url);
  }
});

app.whenReady().then(async () => {
  const port = await getAvailablePort().catch(() => 8000);
  backendPort = port;

  startBackendService(backendPort);
  const ready = await waitForBackend(backendPort, 60, 500);
  if (!ready) {
    console.warn('Backend service did not start in time. Launching window in degraded state.');
    dialog.showErrorBox(
      'MailShield Backend Service Offline',
      `The local inference service could not be started on port ${backendPort}.\n\n` +
      'MailShield Desktop will run in degraded mode. Features requiring live inference will be disabled until the backend service is available.'
    );
  }

  await createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('before-quit', () => {
  stopBackendService();
});

app.on('window-all-closed', () => {
  stopBackendService();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
