import { contextBridge, ipcRenderer } from 'electron';

// Parse dynamic backend port from command-line arguments passed via additionalArguments
const portArg = process.argv.find((arg) => arg.startsWith('--backend-port='));
const backendPort = portArg ? parseInt(portArg.split('=')[1], 10) : 8000;
const apiBase = `http://127.0.0.1:${backendPort}/api/v1`;

contextBridge.exposeInMainWorld('mailshieldDesktop', {
  platform: process.platform,
  backendPort,
  apiBase,
  isOffline: () => !navigator.onLine,
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getBackendHealth: () => ipcRenderer.invoke('check-backend-health'),
  getApiBase: () => apiBase,
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
});
