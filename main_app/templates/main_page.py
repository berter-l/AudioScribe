MAIN_PAGE_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аудио транскрипция</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 40px 20px;
        }

        .container { width: 100%; max-width: 600px; }

        h1 {
            font-size: 24px;
            margin-bottom: 24px;
            color: #333;
            font-weight: 600;
        }

        .upload-section, .files-section {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }

        input[type="file"] { display: none; }

        .file-label {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px 20px;
            border: 2px dashed #d0d0d0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            color: #666;
            font-size: 14px;
            text-align: center;
            margin-bottom: 16px;
        }

        .file-label:hover, .file-label.has-file {
            border-color: #4a90e2;
            color: #4a90e2;
            background: #f8fbff;
        }

        button {
            width: 100%;
            padding: 12px;
            background: #4a90e2;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover:not(:disabled) { background: #3a7bc8; }
        button:disabled { background: #ccc; cursor: not-allowed; }

        .status {
            margin-top: 12px;
            font-size: 14px;
            text-align: center;
            min-height: 20px;
        }

        .status.success { color: #2e7d32; }
        .status.error { color: #c62828; }
        .status.loading { color: #666; }

        .files-list { list-style: none; }

        .files-list li {
            padding: 12px 14px;
            border-radius: 8px;
            margin-bottom: 8px;
            background: #fafafa;
            transition: background 0.2s;
        }

        .files-list li:hover { background: #f0f0f0; }

        .files-list a {
            display: flex;
            align-items: center;
            color: #333;
            text-decoration: none;
            font-size: 14px;
            gap: 10px;
        }

        .files-list a:hover { color: #4a90e2; }
        .files-list a::before { content: "🎵"; font-size: 16px; }

        .empty {
            color: #999;
            font-size: 14px;
            text-align: center;
            padding: 20px;
        }

        .refresh-btn {
            background: transparent;
            color: #4a90e2;
            padding: 6px 12px;
            width: auto;
            font-size: 13px;
        }

        .refresh-btn:hover:not(:disabled) { background: #f0f7ff; }

        .header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .header-row h2 {
            font-size: 18px;
            color: #333;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Аудио транскрипция</h1>

        <div class="upload-section">
            <div class="file-input-wrapper">
                <input type="file" id="audioInput" accept="audio/*">
                <label for="audioInput" class="file-label" id="fileLabel">
                    Нажмите, чтобы выбрать аудиофайл
                </label>
            </div>
            <button id="uploadBtn" disabled>Отправить</button>
            <div class="status" id="status"></div>
        </div>

        <div class="files-section">
            <div class="header-row">
                <h2>Обработанные файлы</h2>
                <button class="refresh-btn" id="refreshBtn">Обновить</button>
            </div>
            <ul class="files-list" id="filesList">
                <li class="empty">Загрузка...</li>
            </ul>
        </div>
    </div>

    <script>
        // API_BASE can be overridden by injecting a meta tag server-side.
        // Default: same host, port 8000 (orchestrator).
        const metaApi = document.querySelector('meta[name="api-base"]');
        const API_BASE = metaApi
            ? metaApi.getAttribute('content')
            : `http://${window.location.hostname}:8000`;

        const audioInput = document.getElementById('audioInput');
        const fileLabel = document.getElementById('fileLabel');
        const uploadBtn = document.getElementById('uploadBtn');
        const statusEl = document.getElementById('status');
        const filesList = document.getElementById('filesList');
        const refreshBtn = document.getElementById('refreshBtn');

        audioInput.addEventListener('change', () => {
            const file = audioInput.files[0];
            if (file) {
                fileLabel.textContent = file.name;
                fileLabel.classList.add('has-file');
                uploadBtn.disabled = false;
            } else {
                fileLabel.textContent = 'Нажмите, чтобы выбрать аудиофайл';
                fileLabel.classList.remove('has-file');
                uploadBtn.disabled = true;
            }
        });

        uploadBtn.addEventListener('click', async () => {
            const file = audioInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('audio', file);

            uploadBtn.disabled = true;
            statusEl.textContent = 'Отправка...';
            statusEl.className = 'status loading';

            try {
                const response = await fetch(`${API_BASE}/audio`, {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) throw new Error(`Ошибка: ${response.status}`);

                statusEl.textContent = 'Файл успешно отправлен';
                statusEl.className = 'status success';

                audioInput.value = '';
                fileLabel.textContent = 'Нажмите, чтобы выбрать аудиофайл';
                fileLabel.classList.remove('has-file');

                setTimeout(loadFiles, 1500);
            } catch (err) {
                statusEl.textContent = err.message || 'Ошибка отправки';
                statusEl.className = 'status error';
                uploadBtn.disabled = false;
            }
        });

        async function loadFiles() {
            try {
                const response = await fetch(`${API_BASE}/files-metadata`);
                if (!response.ok) throw new Error('Не удалось загрузить файлы');
                const files = await response.json();

                if (!files || files.length === 0) {
                    filesList.innerHTML = '<li class="empty">Нет файлов</li>';
                    return;
                }

                filesList.innerHTML = files.map(file => `
                    <li>
                        <a href="${escapeAttr(file.result_s3_url)}"
                           download="${escapeAttr(file.name)}"
                           target="_blank" rel="noopener">
                            ${escapeHtml(file.name)}
                        </a>
                    </li>
                `).join('');
            } catch (err) {
                filesList.innerHTML = `<li class="empty">Ошибка: ${escapeHtml(err.message)}</li>`;
            }
        }

        function escapeHtml(str) {
            return String(str)
                .replace(/&/g, '&amp;').replace(/</g, '&lt;')
                .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }
        const escapeAttr = escapeHtml;

        refreshBtn.addEventListener('click', loadFiles);
        loadFiles();
    </script>
</body>
</html>"""
