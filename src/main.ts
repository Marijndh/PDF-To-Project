import {app, BrowserWindow, ipcMain, shell} from 'electron';
import path from 'node:path';
import started from 'electron-squirrel-startup';
import 'vuetify/styles';
import dotenv from "dotenv";
import fs from "fs";
import nodemailer from "nodemailer";
import {getDocument, GlobalWorkerOptions} from "pdfjs-dist";
import {pathToFileURL} from "url";
import { OAuth2Client } from 'google-auth-library';
import { gmail } from 'googleapis/build/src/apis/gmail';
import http from "http";
import express from "express";

// Convert the local path to a valid file:// URL
const workerPath = pathToFileURL(path.join(__dirname, '../../node_modules/pdfjs-dist/build/pdf.worker.mjs')).href;
GlobalWorkerOptions.workerSrc = workerPath;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

dotenv.config();

const oauth2Client = new OAuth2Client(
    import.meta.env.VITE_GOOGLE_CLIENT_ID,
    import.meta.env.VITE_GOOGLE_CLIENT_SECRET,
    import.meta.env.VITE_GOOGLE_REDIRECT_URI
);

let serverStarted = false; // Flag to track if the server is already started

// Start the express server only when needed
function startServer() {
  if (serverStarted) {
    return; // Don't start the server if it's already running
  }
  const server = express();
  const port = 3000; // Port to listen on for the callback

  const serverInstance = http.createServer(server);
  serverInstance.listen(port, () => {
    console.log(`Server started at http://localhost:${port}`);
    serverStarted = true; // Mark the server as started
  });

  // Set up the callback route
  server.get("/auth/google/callback", async (req, res) => {
    const { code } = req.query;

    if (code) {
      try {
        // Exchange the authorization code for tokens
        const { tokens } = await oauth2Client.getToken(code as string);
        oauth2Client.setCredentials(tokens);

        // Save tokens to tokens.json or your preferred storage
        saveTokens(tokens);

        // Respond to the browser that authentication was successful
        res.send("Authentication successful! You can now close this page.");
      } catch (error) {
        console.error("Error exchanging code for tokens:", error);
        res.send("Authentication failed. Please try again.");
      }
    } else {
      res.send("No authorization code received.");
    }
  });
}

// Fetch user's email address using the Google API
async function getUserEmail() {
  try {
    const oauth2ClientCredentials = oauth2Client.credentials;
    if (!oauth2ClientCredentials.access_token) {
      throw new Error('No access token found!');
    }

    const gmailSession = gmail({ version: 'v1', auth: oauth2Client });
    const res = await gmailSession.users.getProfile({ userId: 'me' });

    return res.data.emailAddress;
  } catch (error) {
    console.error('Error fetching user email:', error);
    throw error; // Re-throw error for handling in other parts of the code
  }
}

const fetchTokens = () => {
  const tokensPath = path.resolve(process.cwd(), "tokens.json");
  try {
    const tokenData = fs.readFileSync(tokensPath, "utf-8");
    const parsedTokens = JSON.parse(tokenData);
    oauth2Client.setCredentials(parsedTokens);
  } catch (error) {
    console.error("Error loading tokens:", error);
  }
}

const saveTokens = (tokens: any) => {
  const tokensPath = path.resolve(process.cwd(), "tokens.json");

  // Create an object to store the tokens
  const tokenData = {
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    expires_in: tokens.expires_in,
    scope: tokens.scope,
    token_type: tokens.token_type,
    expiry_date: tokens.expiry_date,
  };
  oauth2Client.setCredentials(tokenData);

  try {
    fs.writeFileSync(tokensPath, JSON.stringify(tokenData, null, 2));
  } catch (error) {
    console.error("Error saving tokens:", error);
  }
}

const getNewAccessToken = () => {
  startServer();
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: ["https://mail.google.com/"],
    prompt: "consent",
  });

  console.log(`Opening this URL in the default browser: ${authUrl}`);
  shell.openExternal(authUrl); // Open the URL automatically in the default browser
}

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

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
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

    dotenv.config();
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
  fetchTokens();

  if (!oauth2Client.credentials.access_token) {
    console.log("No access token found, requesting authentication...");
    getNewAccessToken();
    return;
  }

  const userEmail = await getUserEmail();

  const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      type: "OAuth2",
      user: userEmail,
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      clientSecret: import.meta.env.VITE_GOOGLE_CLIENT_SECRET,
      refreshToken: oauth2Client.credentials.refresh_token,
      accessToken: oauth2Client.credentials.access_token!,
    },
  });

  const files = fs.readdirSync(directory);
  const txtFiles = files.filter(file => file.endsWith('.txt'));
  const attachments = files.filter(file => !file.endsWith('.txt'));

  if (!files || files.length === 0) {
    console.error('No files found in the directory:', directory);
    return;
  }

  const mailOptions = {
    from: userEmail,
    to: import.meta.env.VITE_EMAIL_TO,
    subject: 'LogLine-File: ' + name,
    text: txtFiles.map(file => fs.readFileSync(path.join(directory, file), 'utf-8')).join('\n\n'),
    attachments: attachments.map(file => ({filename: file, path: path.join(directory, file)})),
  };

  console.log(mailOptions);

  transporter.sendMail(mailOptions, (error: any, info: any) => {
    if (error) {
      if (error.code === "EAUTH") {
        console.log("Access token expired, requesting new authentication...");
        console.log(error)
        getNewAccessToken();
      }
      else console.error('Error sending email:', error);
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
  const template = readFileContent(`src/templates/clients/${abbreviation}.json`, 'json');
  console.log(template)
  return template;
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