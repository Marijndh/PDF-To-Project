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
    return [];
  }


  const allDirs = fs.readdirSync(logDir)
      .filter(file => fs.statSync(path.join(logDir, file)).isDirectory())
      .sort((a, b) => fs.statSync(path.join(logDir, b)).mtime.getTime() - fs.statSync(path.join(logDir, a)).mtime.getTime());

  const slicedDirs = allDirs.slice(0, amount).map(dir => ({name: dir, path: path.join(logDir, dir)}));
  const remainingDirs = allDirs.slice(amount).map(dir => ({name: dir, path: path.join(logDir, dir)}));

  remainingDirs.forEach(dir => {
    fs.rmSync(dir.path, { recursive: true, force: true });
  });
  return slicedDirs;
});

ipcMain.handle('open-file', async (_event, path) => {
  await shell.openPath(path);
});

ipcMain.handle('send-email', async (_event,directory, name) => {
  const from: string = import.meta.env.VITE_EMAIL_FROM;
  const to: string = import.meta.env.VITE_EMAIL_TO;
  const client_id: string = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const client_secret: string = import.meta.env.VITE_GOOGLE_CLIENT_SECRET;
  const refresh_token: string = import.meta.env.VITE_GOOGLE_REFRESH_TOKEN;
  const access_token: string = import.meta.env.VITE_GOOGLE_ACCESS_TOKEN;

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

  const files = fs.readdirSync(directory);
  const txtFiles = files.filter(file => file.endsWith('.txt'));
  const attachments = files.filter(file => !file.endsWith('.txt'));

  if (!files || files.length === 0) {
    console.error('No files found in the directory:', directory);
    return;
  }

  const mailOptions = {
    from: from,
    to: to,
    subject: 'Log-File: ' + name,
    text: txtFiles.map(file => fs.readFileSync(path.join(directory, file), 'utf-8')).join('\n\n'),
    attachments: attachments.map(file => ({filename: file, path: path.join(directory, file)})),
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

ipcMain.handle('get-clients', async () => {
  const templatesDir = path.resolve(process.cwd(), 'src/templates/mapping');
  const files = fs.readdirSync(templatesDir);
  const clients = [];

  for (const file of files) {
    if (path.extname(file) === '.yaml') {
      const filePath = path.join(templatesDir, file);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const yaml = require('js-yaml');
      const yamlContent = yaml.load(fileContent);
      if (yamlContent.name && yamlContent.abbreviation && yamlContent.identifier && yamlContent.projectAttributes) {
        clients.push({
          name: yamlContent.name,
          abbreviation: yamlContent.abbreviation,
          identifier: yamlContent.identifier,
          attributeIdentifiers: yamlContent.projectAttributes,
        });
      }
    }
  }
  return clients;
});

ipcMain.handle('get-test-file', async () => {
  return readFileContent('src/test-files/BW.pdf', 'buffer');
});

ipcMain.handle('get-template', async (_event, abbreviation) => {
  return readFileContent(`src/templates/clients/${abbreviation}.json`, 'json');
});

ipcMain.handle('get-log-messages', async () => {
  return readFileContent('src/templates/logMessages.yaml', 'yaml');
});

const readFileContent = (relativePath: string, type: 'buffer' | 'json' | 'yaml'): any => {
  const filePath = path.resolve(process.cwd(), relativePath);
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const fileContent = fs.readFileSync(filePath, type === 'buffer' ? null : 'utf-8');
  if (type === 'json') {
    return JSON.parse(fileContent);
  } else if (type === 'yaml') {
    const yaml = require('js-yaml');
    return yaml.load(fileContent);
  }
  return Buffer.from(fileContent);
};

ipcMain.handle('create-log', async (_event, messages, text, projectData, fileBuffer) => {
  try {
    const logDir = path.resolve(process.cwd(), 'logs', new Date().toISOString().replace(/[:.]/g, '-'));
    fs.mkdirSync(logDir, { recursive: true });

    const pdfPath = path.join(logDir, 'file.pdf');
    fs.writeFileSync(pdfPath, Buffer.from(fileBuffer));

    const jsonPath = path.join(logDir, 'data.json');
    fs.writeFileSync(jsonPath, JSON.stringify(projectData, null, 2));

    const messagesPath = path.join(logDir, 'messages.txt');
    fs.writeFileSync(messagesPath, messages.join('\n'));

    return true;
  } catch (error) {
    console.error('Error creating log:', error);
    return false;
  }
});