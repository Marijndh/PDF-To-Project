import {app, BrowserWindow, ipcMain, shell} from 'electron';
import path from 'node:path';
import started from 'electron-squirrel-startup';
import 'vuetify/styles';
import dotenv from "dotenv";
import fs from "fs";
import nodemailer from "nodemailer";
import {getDocument, GlobalWorkerOptions} from "pdfjs-dist";
import {pathToFileURL} from "url";
import {OAuth2Client} from 'google-auth-library';
import {gmail} from 'googleapis/build/src/apis/gmail';
import http from "http";
import express from "express";
import yaml from 'js-yaml';
import { updateElectronApp, UpdateSourceType } from 'update-electron-app'
import logger from 'electron-log'

updateElectronApp({
  updateSource: {
    type: UpdateSourceType.ElectronPublicUpdateService,
    repo: 'Marijndh/PDF-To-Project'
  },
  updateInterval: '1 hour',
  logger: logger
})
// Convert the local path to a valid file:// URL
const workerPath = pathToFileURL(path.join(__dirname, '../../node_modules/pdfjs-dist/build/pdf.worker.mjs')).href;
GlobalWorkerOptions.workerSrc = workerPath;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

// Define paths
const envPath = path.join(app.getPath("userData"), ".env"); // Writable location
const envExamplePath = path.join(app.getAppPath(), ".env.example"); // Inside asar

// Ensure .env exists, creating it from .env.example if needed
if (!fs.existsSync(envPath)) {
  try {
    const exampleExists = fs.existsSync(envExamplePath);
    if (exampleExists) {
      fs.copyFileSync(envExamplePath, envPath);
      console.log(".env file created from .env.example");
    } else {
      console.warn(".env.example not found, creating an empty .env file.");
      fs.writeFileSync(envPath, "");
    }
  } catch (error) {
    console.error("Error creating .env file:", error);
  }
}
// Load environment variables
dotenv.config({ path: envPath });

// Use userData path for logs
const logDir = path.join(app.getPath("userData"), "logs");

// Ensure log folder exists
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
  console.log("Log directory created:", logDir);
}


const oauth2Client = new OAuth2Client(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI
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
      console.error('No access token found!');
    }

    const gmailSession = gmail({ version: 'v1', auth: oauth2Client });
    const res = await gmailSession.users.getProfile({ userId: 'me' });

    return res.data.emailAddress;
  } catch (error) {
    console.error('Error fetching user email:', error);
    throw error; // Re-throw error for handling in other parts of the code
  }
}

const tokenPath = path.join(app.getPath("userData"), "tokens.json");

// Function to read tokens
function fetchTokens() {
  if (fs.existsSync(tokenPath)) {
    const tokens = JSON.parse(fs.readFileSync(tokenPath, "utf-8"));
    oauth2Client.setCredentials(tokens);
    console.log("Tokens loaded successfully");
  } else {
    console.log("No existing tokens found");
  }
}
const saveTokens = (tokens: any) => {

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
    fs.writeFileSync(tokenPath, JSON.stringify(tokenData, null, 2));
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

const readFileContent = (relativePath: string, type: 'buffer' | 'json' | 'yaml'): any => {
  const filePath = path.resolve(app.getAppPath(), relativePath);
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const fileContent = fs.readFileSync(filePath, type === 'buffer' ? null : 'utf-8');
  if (type === 'json') {
    return JSON.parse(fileContent);
  } else if (type === 'yaml') {
    return yaml.load(fileContent);
  }
  return Buffer.from(fileContent);
};

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
};

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
ipcMain.handle('get-env-variable', async(_event, variable) => {
  return process.env[variable];
});


ipcMain.handle('open-external', async (_event, url) => {
  await shell.openExternal(url);
});

ipcMain.handle('get-logs', async (_event, amount: number) => {
  if (!fs.existsSync(logDir)) {
    console.error(`Logdirectory not found: ${logDir}`);
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

ipcMain.handle("update-token", (_event, token) => {
  try {
    if (!fs.existsSync(envPath)) {
      fs.writeFileSync(envPath, "API_TOKEN=\n");
    }

    let envContent = fs.readFileSync(envPath, "utf-8");

    // Replace API_TOKEN dynamically
    if (envContent.includes("API_TOKEN=")) {
      envContent = envContent.replace(/API_TOKEN=.*/g, `API_TOKEN=${token}`);
    } else {
      envContent += `\nAPI_TOKEN=${token}`;
    }

    fs.writeFileSync(envPath, envContent);
    dotenv.config({ path: envPath });

    console.log("Updated API_TOKEN in .env");
  } catch (error) {
    console.error("Failed to update token:", error);
  }
});

ipcMain.handle('send-email', async (_event,directory, name, message) => {
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
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
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
    to: process.env.EMAIL_TO,
    subject: 'LogLine-File: ' + name,
    text: message + '\n\n' + txtFiles.map(file => fs.readFileSync(path.join(directory, file), 'utf-8')).join('\n\n'),
    attachments: attachments.map(file => ({filename: file, path: path.join(directory, file)})),
  };

  transporter.sendMail(mailOptions, (error: any, info: any) => {
    if (error) {
      if (error.code === "EAUTH") {
        console.log("Access token expired, requesting new authentication...");
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
  const templatesDir = path.resolve(app.getAppPath(), 'src/templates/mapping');
  const files = fs.readdirSync(templatesDir);
  const clients = [];

  for (const file of files) {
    if (path.extname(file) === '.yaml') {
      const filePath = path.join(templatesDir, file);
      const fileContent = fs.readFileSync(filePath, 'utf-8');
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

ipcMain.handle('get-test-file', async() => {
  return readFileContent('src/test-files/BW.pdf', 'buffer');
});

ipcMain.handle('get-template', async(_event, abbreviation) => {
  return readFileContent(`src/templates/clients/${abbreviation}.json`, 'json');
});

ipcMain.handle('get-log-messages', async() => {
  return readFileContent('src/templates/logMessages.yaml', 'yaml');
});

ipcMain.handle('create-log', async (_event, messages, text, projectData, fileBuffer) => {
  try {

    if (!fs.existsSync(logDir)) {
      console.error(`Logdirectory not found: ${logDir}`);
      return [];
    }
    const log = path.resolve(logDir, new Date().toISOString().replace(/[:.]/g, '-'));

    fs.mkdirSync(log, { recursive: true });

    const pdfPath = path.join(log, 'file.pdf');
    fs.writeFileSync(pdfPath, Buffer.from(fileBuffer));

    const jsonPath = path.join(log, 'data.json');
    fs.writeFileSync(jsonPath, JSON.stringify(projectData, null, 2));

    const messagesPath = path.join(log, 'messages.txt');
    fs.writeFileSync(messagesPath, text + '\n\n' + messages.join('\n'));

    return true;
  } catch (error) {
    console.error('Error creating log:', error);
    return false;
  }
});

app.on('ready', createWindow);