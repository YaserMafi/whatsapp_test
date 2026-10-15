const express = require('express');
const cors = require('cors');
const path = require('path');
const https = require('https');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));

app.post('/api/telegram', async (req, res) => {
  const { chat_id, text, parse_mode } = req.body;
  if (!chat_id || !text) return res.status(400).json({ error: 'chat_id and text required' });

  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const postData = JSON.stringify({ chat_id, text, parse_mode: parse_mode || 'Markdown' });

  const options = {
    hostname: 'api.telegram.org',
    path: `/bot${botToken}/sendMessage`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
  };

  const tgReq = https.request(options, (tgRes) => {
    let data = '';
    tgRes.on('data', (chunk) => { data += chunk; });
    tgRes.on('end', () => { try { res.json(JSON.parse(data)); } catch(e) { res.json({raw: data}); } });
  });
  tgReq.on('error', (e) => res.status(500).json({ error: e.message }));
  tgReq.write(postData);
  tgReq.end();
});

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.listen(PORT, '0.0.0.0', () => console.log(`Server running on port ${PORT}`));
