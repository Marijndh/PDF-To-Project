import {app, BrowserWindow, ipcMain, shell} from 'electron';
import path from 'node:path';
import started from 'electron-squirrel-startup';
import 'vuetify/styles';
import dotenv from "dotenv";
import fs from "fs";
import nodemailer from "nodemailer";
import {getDocument, GlobalWorkerOptions} from "pdfjs-dist";
import {pathToFileURL} from "url";

// Convert the local path to a valid file:// URL
const workerPath = pathToFileURL(path.join(__dirname, '../../node_modules/pdfjs-dist/build/pdf.worker.mjs')).href;
GlobalWorkerOptions.workerSrc = workerPath;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

dotenv.config();

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: true,
    },
    title: app.name,
    autoHideMenuBar: true,
    minHeight: 600,
    minWidth: 900,
    maxHeight: 600,
    maxWidth: 900,
    maximizable: false,
  });

  // and load the index.html of the app.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
  }

  mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

ipcMain.on("update-token", (event, token) => {
  try {
    const envPath = path.resolve(process.cwd(), ".env");
    const envContent = fs.readFileSync(envPath, "utf-8");

    const updatedEnvContent = envContent.replace(/API_TOKEN=.*/g, `API_TOKEN=${token}`);
    fs.writeFileSync(envPath, updatedEnvContent);

    dotenv.config(); // Reload environment variables
    console.log("Token updated successfully!");
  } catch (error) {
    console.error("Failed to update token:", error);
  }
});

ipcMain.handle('open-external', async (_event, url) => {
  await shell.openExternal(url);
});

ipcMain.handle('get-logs', async (_event, amount: number) => {
  const logDir = path.resolve(process.cwd(), "logs");

  if (!fs.existsSync(logDir)) {
    console.error(`Directory not found: ${logDir}`);
    return []; // Return an empty array instead of throwing an error
  }

  const files = fs.readdirSync(logDir).slice(0, amount);
  return { dir: logDir, files };
});

ipcMain.handle('open-file', async (_event, path) => {
  await shell.openPath(path);
});

ipcMain.handle('send-email', async (_event, from, to, path, name, client_id, client_secret, refresh_token, access_token) => {
  console.log(refresh_token);
  const transporter = nodemailer.createTransport({
    host: "smtp.gmail.com",
    port: 465,
    secure: true,
    auth: {
      type: "OAuth2",
      user: from,
      clientId: client_id,
      clientSecret: client_secret,
      refreshToken: refresh_token,
      accessToken: access_token,
      expires: 0,
    }
  });

  const mailOptions = {
    from: from,
    to: to,
    subject: 'Log-File: ' + name,
    text: fs.readFileSync(path, 'utf-8')
  };

  transporter.sendMail(mailOptions, (error: any, info: any) => {
    if (error) {
      console.error('Error sending email:', error);
    } else {
      console.log('Email sent:', info.response);
    }
  });
});

ipcMain.handle('text-from-pdf', async (_event, buffer) => {
    const pdf = getDocument(buffer);
    return pdf.promise.then(async (pdf) => {
      const totalPageCount = pdf.numPages;
      const textPromises = [];

      for (let currentPage = 1; currentPage <= totalPageCount; currentPage++) {
        const page = await pdf.getPage(currentPage);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map((item: any) => item.str).join(' ');
        textPromises.push(pageText);
      }

      const allText = textPromises.join(' ');
      return allText.split(/\s+/);
    });
});
