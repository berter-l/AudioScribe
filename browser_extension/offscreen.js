// offscreen.js

let mediaRecorder = null;
let activeStream = null;
let chunks = [];
let meta = null;
let currentTabId = null;
let uploadUrl = null;

let audioContext = null;
let sourceNode = null;
let silentGain = null;          // узел с нулевой громкостью
let keepAliveTimer = null;

/* ---------- Роутинг ---------- */

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.target !== 'offscreen') return false;

  if (msg.type === 'START') {
    startRecording(msg.streamId, msg.tabId, msg.uploadUrl)
      .then(() => sendResponse({ ok: true }))
      .catch((e) => sendResponse({ ok: false, error: e.message }));
    return true;
  }

  if (msg.type === 'STOP') {
    // Передаем customFileName, полученный из background.js
    stopRecording(msg.customFileName)
      .then((r) => sendResponse(r))
      .catch((e) => sendResponse({ ok: false, error: e.message }));
    return true;
  }

  return false;
});

/* ---------- Метаданные и имя файла ---------- */

function buildFileName(customName) {
  const now = new Date();
  now.setSeconds(0, 0);
  const p = (n) => String(n).padStart(2, '0');
  const stamp =
    `${now.getFullYear()}-${p(now.getMonth() + 1)}-${p(now.getDate())}` +
    `_${p(now.getHours())}-${p(now.getMinutes())}`;

  // Используем кастомное имя, если оно передано. Иначе — заголовок вкладки или дефолтное 'Запись'
  const title = (customName || meta?.title || 'Запись')
    .replace(/[\\/:*?"<>|]/g, '_')
    .slice(0, 100);
  const host = (meta?.host || 'tab')
    .replace(/[\\/:*?"<>|]/g, '_')
    .slice(0, 60);

  return `${title}__${host}__${stamp}.webm`;
}

/* ---------- Старт записи ---------- */

async function startRecording(streamId, tabId, url) {
  if (mediaRecorder) return;

  currentTabId = tabId;
  uploadUrl = url;

  try {
    const info = await chrome.tabs.get(tabId);
    meta = {
      title: info.title || 'Запись',
      host: (() => {
        try { return new URL(info.url).hostname; }
        catch { return 'tab'; }
      })()
    };
  } catch {
    meta = { title: 'Запись', host: 'tab' };
  }

  try {
    activeStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        mandatory: {
          chromeMediaSource: 'tab',
          chromeMediaSourceId: streamId
        }
      },
      video: false
    });
  } catch (e) {
    throw new Error('Не удалось захватить аудио: ' + e.message);
  }

  const audioTracks = activeStream.getAudioTracks();
  console.log('[Offscreen] audio tracks =', audioTracks.length);
  if (audioTracks.length === 0) {
    throw new Error('В захваченном потоке нет аудиотрека');
  }
  audioTracks.forEach((t) => {
    console.log('[Offscreen] track:', t.label, 'enabled =', t.enabled,
                'muted =', t.muted, 'readyState =', t.readyState);
  });

  audioContext = new AudioContext();
  sourceNode = audioContext.createMediaStreamSource(activeStream);

  silentGain = audioContext.createGain();
  silentGain.gain.value = 0;
  sourceNode.connect(silentGain);

  if (audioContext.state === 'suspended') {
    try { await audioContext.resume(); } catch {}
  }

  chunks = [];

  const preferred = 'audio/webm;codecs=opus';
  const mimeType = MediaRecorder.isTypeSupported(preferred)
    ? preferred
    : 'audio/webm';

  mediaRecorder = new MediaRecorder(activeStream, { mimeType });

  mediaRecorder.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) chunks.push(e.data);
  };

  mediaRecorder.onerror = (e) => {
    console.error('[Offscreen] MediaRecorder error:', e);
  };

  mediaRecorder.start(5000);

  keepAliveTimer = setInterval(() => {
    chrome.runtime.sendMessage({ type: 'PING' }).catch(() => {});
  }, 20_000);

  console.log('[Offscreen] Запись начата (звук в динамики не идёт):', buildFileName());
}

/* ---------- Стоп записи + отправка ---------- */

function stopRecording(customFileName) {
  return new Promise((resolve) => {
    if (!mediaRecorder) {
      resolve({ ok: false, error: 'not recording' });
      return;
    }

    clearInterval(keepAliveTimer);
    keepAliveTimer = null;

    const recorder = mediaRecorder;
    const stream = activeStream;
    // Генерируем имя файла на основе переданного пользователем текста
    const fileName = buildFileName(customFileName);
    const url = uploadUrl;

    recorder.onstop = async () => {
      let uploaded = false;
      let uploadError = null;

      try {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        console.log('[Offscreen] blob size =', blob.size, 'chunks =', chunks.length);

        if (blob.size === 0) {
          throw new Error('Пустой blob — нечего отправлять');
        }

        downloadBlob(blob, fileName);

        try {
          // Имя файла передается третьим параметром и уходит в заголовки Multipart-запроса на бэкенд
          const result = await uploadToServer(url, blob, fileName);
          uploaded = result.ok;
          if (!result.ok) uploadError = result.error || `HTTP ${result.status}`;
          console.log('[Offscreen] upload result:', result);
        } catch (e) {
          uploadError = e.message;
          console.error('[Offscreen] upload failed:', e);
        }

        chrome.runtime.sendMessage({
          type: uploaded ? 'UPLOAD_DONE' : 'UPLOAD_ERROR',
          error: uploadError
        }).catch(() => {});

        resolve({ ok: true, fileName, uploaded, uploadError });
      } catch (e) {
        resolve({ ok: false, error: e.message });
      }

      chunks = [];
      mediaRecorder = null;
      activeStream = null;
      meta = null;
      uploadUrl = null;

      try {
        sourceNode?.disconnect();
        silentGain?.disconnect();
        audioContext?.close();
      } catch {}
      sourceNode = null;
      silentGain = null;
      audioContext = null;
    };

    recorder.stop();
    stream?.getTracks().forEach((t) => t.stop());
  });
}

/* ---------- Локальное сохранение ---------- */

function downloadBlob(blob, fileName) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

/* ---------- Отправка на FastAPI ---------- */

async function uploadToServer(endpoint, blob, fileName) {
  console.log('[Offscreen] POST', endpoint, 'size=', blob.size, 'type=', blob.type);

  const form = new FormData();
  // Передаем файл с новым сгенерированным/кастомным именем
  form.append('audio', blob, fileName || 'recording.webm');

  try {
    const resp = await fetch(endpoint, {
      method: 'POST',
      body: form
    });

    console.log('[Offscreen] response', resp.status, resp.type);

    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      return { ok: false, status: resp.status, error: text };
    }

    const json = await resp.json().catch(() => ({}));
    return { ok: true, status: resp.status, data: json };
  } catch (e) {
    console.error('[Offscreen] fetch threw:', e);
    return { ok: false, error: e.message };
  }
}
