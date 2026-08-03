import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { google } from 'googleapis';
import { z } from 'zod';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TOKEN_PATH = path.join(__dirname, 'token.json');
const CREDENTIALS_PATH = path.join(__dirname, 'credentials.json');

async function getAuth() {
  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH));
  const { client_secret, client_id, redirect_uris } = credentials.installed;
  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

  if (fs.existsSync(TOKEN_PATH)) {
    oAuth2Client.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH)));
    return oAuth2Client;
  }

  const authUrl = oAuth2Client.generateAuthUrl({ access_type: 'offline', scope: [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly'
  ] });
  console.error('Open in your browser:', authUrl);

  const readline = await import('readline');
  const rl = readline.createInterface({ input: process.stdin, output: process.stderr });

  return new Promise((resolve) => {
    rl.question('Paste the code from the browser: ', async (code) => {
      rl.close();
      const { tokens } = await oAuth2Client.getToken(code);
      oAuth2Client.setCredentials(tokens);
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens));
      resolve(oAuth2Client);
    });
  });
}

const server = new McpServer({ name: 'google-sheets-mcp', version: '1.0.0' });

server.tool('read_sheet', 'Reads data from Google Sheets', {
  spreadsheetId: z.string().describe('Spreadsheet ID from the URL'),
  range: z.string().describe('Range, e.g. A1:D10'),
  valueRenderOption: z
    .enum(['FORMATTED_VALUE', 'FORMULA', 'UNFORMATTED_VALUE'])
    .optional()
    .describe('FORMATTED_VALUE (default) - computed value as shown in the UI; FORMULA - formula text instead of the result; UNFORMATTED_VALUE - raw value without formatting')
}, async ({ spreadsheetId, range, valueRenderOption }) => {
  const auth = await getAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId, range,
    valueRenderOption: valueRenderOption ?? 'FORMATTED_VALUE'
  });
  return { content: [{ type: 'text', text: JSON.stringify(res.data.values ?? [], null, 2) }] };
});

server.tool('write_sheet', 'Writes data to Google Sheets', {
  spreadsheetId: z.string(),
  range: z.string(),
  values: z.array(z.array(z.string())).describe('2-D array of row data')
}, async ({ spreadsheetId, range, values }) => {
  const auth = await getAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  await sheets.spreadsheets.values.update({
    spreadsheetId, range,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values }
  });
  return { content: [{ type: 'text', text: 'Data written successfully' }] };
});

server.tool('add_sheet', 'Adds a new sheet (tab) to a spreadsheet', {
  spreadsheetId: z.string(),
  sheetName: z.string()
}, async ({ spreadsheetId, sheetName }) => {
  const auth = await getAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  await sheets.spreadsheets.batchUpdate({
    spreadsheetId,
    requestBody: { requests: [{ addSheet: { properties: { title: sheetName } } }] }
  });
  return { content: [{ type: 'text', text: `Sheet \"${sheetName}\" created` }] };
});

server.tool('list_drive_folder', 'Lists files in a Google Drive folder', {
  folderId: z.string().describe('Folder ID from the Google Drive URL')
}, async ({ folderId }) => {
  const auth = await getAuth();
  const drive = google.drive({ version: 'v3', auth });
  const res = await drive.files.list({
    q: `'${folderId}' in parents and trashed = false`,
    fields: 'files(id, name, mimeType)',
    pageSize: 100,
    includeItemsFromAllDrives: true,
    supportsAllDrives: true
  });
  const files = res.data.files ?? [];
  return { content: [{ type: 'text', text: JSON.stringify(files, null, 2) }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);