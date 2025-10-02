const API_BASE = 'http://127.0.0.1:8000';

function b64ToBlobUrl(b64, mime = 'image/png') {
  const byteChars = atob(b64);
  const byteNumbers = new Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) {
    byteNumbers[i] = byteChars.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: mime });
  return URL.createObjectURL(blob);
}

function downloadBase64(name, b64, mime = 'image/png') {
  const url = b64ToBlobUrl(b64, mime);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  URL.revokeObjectURL(url);
  a.remove();
}

async function onSubmit(e) {
  e.preventDefault();
  const statusEl = document.getElementById('status');
  statusEl.textContent = 'En cours...';

  const fileInput = document.getElementById('file');
  if (!fileInput.files || fileInput.files.length === 0) {
    statusEl.textContent = 'Sélectionne une image.';
    return;
  }

  const params = new URLSearchParams();
  params.set('colors', document.getElementById('colors').value || '9');
  params.set('max_size', document.getElementById('max_size').value || '1024');
  params.set('thickness', document.getElementById('thickness').value || '2');
  params.set('min_area', document.getElementById('min_area').value || '80');
  params.set('merge_area', document.getElementById('merge_area').value || '200');
  params.set('outline_mode', document.getElementById('outline_mode').value || 'union');
  params.set('include_preview', document.getElementById('include_preview').checked ? 'true' : 'false');
  params.set('return_pdf', 'false');

  const form = new FormData();
  form.append('file', fileInput.files[0]);

  try {
    const resp = await fetch(`${API_BASE}/magic/convert?${params.toString()}`, {
      method: 'POST',
      body: form,
    });
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`HTTP ${resp.status}: ${text}`);
    }
    const data = await resp.json();
    renderResults(data);
    statusEl.textContent = 'Terminé';
  } catch (err) {
    console.error(err);
    statusEl.textContent = `Erreur: ${err.message}`;
  }
}

function renderResults(data) {
  const results = document.getElementById('results');
  const wsImg = document.getElementById('worksheet_img');
  const pvImg = document.getElementById('preview_img');
  const lbImg = document.getElementById('labels_img');
  const meta = document.getElementById('meta');

  // Worksheet
  if (data.worksheet_png) {
    wsImg.src = `data:image/png;base64,${data.worksheet_png}`;
    document.getElementById('dl_worksheet').onclick = () => downloadBase64('worksheet.png', data.worksheet_png);
  }

  // Preview
  if (data.preview_png) {
    pvImg.src = `data:image/png;base64,${data.preview_png}`;
    document.getElementById('dl_preview').onclick = () => downloadBase64('preview.png', data.preview_png);
  } else {
    pvImg.removeAttribute('src');
  }

  // Labels
  if (data.labels_png) {
    lbImg.src = `data:image/png;base64,${data.labels_png}`;
    document.getElementById('dl_labels').onclick = () => downloadBase64('labels.png', data.labels_png);
  } else {
    lbImg.removeAttribute('src');
  }

  meta.textContent = `Taille: ${data.meta.width}x${data.meta.height} • Couleurs: ${data.meta.colors}`;
  results.hidden = false;
}

document.getElementById('convert-form').addEventListener('submit', onSubmit);
