// background.js

const UPLOAD_URL = 'http://localhost:8000/audio';

let recordingTabId = null;
let timerInterval = null;
let currentSeconds = 0;
let originalMuteState = false;   // ← храним, был ли замьючен таб до старта

/* ---------- Клик по иконке ---------- */

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.id) return;

  // === СТОП ===
  if (recordingTabId === tab.id) {
    let customFileName = null;

    // Запрашиваем имя у пользователя через prompt на странице текущей вкладки
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          return prompt("Введите название файла для записи:", "");
        }
      });

      // Если пользователь ввел имя, сохраняем его и убираем лишние пробелы
      if (results && results[0] && results[0].result !== null) {
        customFileName = results[0].result.trim();
      }
    } catch (e) {
      console.warn('[Recorder] Не удалось вызвать prompt на странице:', e);
    }

    try {
      // Передаем введенное имя (или null, если отмена) в offscreen
      await chrome.runtime.sendMessage({
        target: 'offscreen',
        type: 'STOP',
        customFileName: customFileName
      });
    } catch (e) {
      console.warn('[Recorder] stop failed:', e);
    }

    // Восстанавливаем mute, если он был до старта
    if (originalMuteState) {
      try {
        await chrome.tabs.update(tab.id, { muted: true });
        console.log('[Recorder] mute восстановлен на вкладке', tab.id);
      } catch (e) {
        console.warn('[Recorder] не удалось восстановить mute:', e);
      }
      originalMuteState = false;
    }

    recordingTabId = null;
    stopTimer(tab.id);
    return;
  }

  if (recordingTabId !== null) {
    console.warn('[Recorder] уже идёт запись в другой вкладке');
    return;
  }

  // === СТАРТ ===
  try {
    // --- Диагностика состояния вкладки ---
    let info = await chrome.tabs.get(tab.id);
    console.log(
      '[Recorder] ДО старта: audible =', info.audible,
      '| muted =', info.mutedInfo?.muted,
      '| reason =', info.mutedInfo?.reason || 'n/a'
    );

    // --- Если вкладка замьючена, снимаем mute для захвата ---
    originalMuteState = !!info.mutedInfo?.muted;
    if (originalMuteState) {
      console.log('[Recorder] Вкладка замьючена — снимаю mute для захвата...');
      await chrome.tabs.update(tab.id, { muted: false });
      // Даём Chrome время применить состояние
      await new Promise((r) => setTimeout(r, 250));

      info = await chrome.tabs.get(tab.id);
      console.log(
        '[Recorder] ПОСЛЕ снятия mute: audible =', info.audible,
        '| muted =', info.mutedInfo?.muted
      );
    }

    // Предупреждаем, если вкладка сейчас ничего не воспроизводит
    if (!info.audible) {
      console.warn(
        '[Recorder] ВНИМАНИЕ: вкладка не воспроизводит звук (audible = false). ' +
        'Если на странице ничего не играет — запись будет пустой.'
      );
    }

    const streamId = await chrome.tabCapture.getMediaStreamId({
      targetTabId: tab.id
    });

    await ensureOffscreen();

    const resp = await chrome.runtime.sendMessage({
      target: 'offscreen',
      type: 'START',
      streamId,
      tabId: tab.id,
      uploadUrl: UPLOAD_URL
    });

    if (!resp?.ok) {
      throw new Error(resp?.error || 'offscreen START failed');
    }

    recordingTabId = tab.id;
    startTimer(tab.id);
    console.log('[Recorder] started on tab', tab.id, 'uploadUrl=', UPLOAD_URL);
  } catch (e) {
    console.error('[Recorder] start failed:', e);

    // Откатываем mute, если что-то пошло не так
    if (originalMuteState) {
      try { await chrome.tabs.update(tab.id, { muted: true }); } catch {}
      originalMuteState = false;
    }

    chrome.action.setBadgeText({ text: 'ERR', tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#888', tabId: tab.id });
    setTimeout(() => chrome.action.setBadgeText({ text: '', tabId: tab.id }), 3000);
  }
});

/* ---------- Таймер на бейдже ---------- */

function startTimer(tabId) {
  currentSeconds = 0;
  chrome.action.setBadgeBackgroundColor({ color: '#df2721', tabId });
  chrome.action.setBadgeText({ text: '00:00', tabId });

  timerInterval = setInterval(() => {
    currentSeconds++;
    const m = String(Math.floor(currentSeconds / 60)).padStart(2, '0');
    const s = String(currentSeconds % 60).padStart(2, '0');
    chrome.action.setBadgeText({ text: `${m}:${s}`, tabId });
  }, 1000);
}

function stopTimer(tabId) {
  clearInterval(timerInterval);
  timerInterval = null;
  currentSeconds = 0;
  chrome.action.setBadgeText({ text: '', tabId });
}

/* ---------- Offscreen ---------- */

async function ensureOffscreen() {
  const has = await chrome.offscreen.hasDocument?.();
  if (has) return;
  await chrome.offscreen.createDocument({
    url: 'offscreen.html',
    reasons: ['USER_MEDIA'],
    justification: 'Запись аудио вкладки'
  });
}

/* ---------- Служебные сообщения ---------- */

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === 'PING') {
    sendResponse({ ok: true });
    return true;
  }
  if (msg?.type === 'UPLOAD_DONE') {
    const tabId = recordingTabId;
    if (tabId !== null) {
      chrome.action.setBadgeText({ text: '✓', tabId });
      chrome.action.setBadgeBackgroundColor({ color: '#16a34a', tabId });
      setTimeout(() => {
        chrome.action.setBadgeText({ text: '', tabId });
      }, 3000);
    }
    sendResponse({ ok: true });
    return true;
  }
  if (msg?.type === 'UPLOAD_ERROR') {
    const tabId = recordingTabId;
    if (tabId !== null) {
      chrome.action.setBadgeText({ text: 'ERR', tabId });
      chrome.action.setBadgeBackgroundColor({ color: '#888', tabId });
      setTimeout(() => {
        chrome.action.setBadgeText({ text: '', tabId });
      }, 3000);
    }
    sendResponse({ ok: true });
    return true;
  }
  return false;
});

chrome.tabs.onRemoved.addListener((tabId) => {
  if (recordingTabId === tabId) {
    recordingTabId = null;
    originalMuteState = false;
    stopTimer(tabId);
  }
});
