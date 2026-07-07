(function () {
  'use strict';

  const API_BASE = '';

  // 状态
  let currentSite = '';
  let currentDir = ''; // 当前选中的目录（相对路径）
  let currentFile = ''; // 当前编辑的文件（相对路径）
  let openFiles = []; // 打开的文件列表
  let activeFile = ''; // 当前激活的文件
  let fileContents = {}; // 缓存的文件内容
  let modifiedFiles = new Set(); // 已修改的文件
  let compileDebounceTimer = null;
  let isTyping = false;
  let editorMode = 'none'; // 'none' | 'single' | 'multi'

  // DOM 元素
  const siteSelector = document.getElementById('siteSelector');
  const fileTree = document.getElementById('fileTree');
  const editorEmpty = document.getElementById('editorEmpty');
  const editorContent = document.getElementById('editorContent');
  const editorTabs = document.getElementById('editorTabs');
  const chapterList = document.getElementById('chapterList');
  const editorTextarea = document.getElementById('editorTextarea');
  const previewContent = document.getElementById('previewContent');
  const statusText = document.getElementById('statusText');
  const newFileModal = document.getElementById('newFileModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalInput = document.getElementById('modalInput');
  const toast = document.getElementById('toast');

  // 设置根目录相关 DOM
  const setRootModal = document.getElementById('setRootModal');
  const rootInput = document.getElementById('rootInput');

  // 工具函数
  async function apiGet(url) {
    const res = await fetch(API_BASE + url);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async function apiPost(url, body) {
    const res = await fetch(API_BASE + url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async function apiDelete(url) {
    const res = await fetch(API_BASE + url, { method: 'DELETE' });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = 'toast show ' + type;
    setTimeout(() => { toast.className = 'toast'; }, 2500);
  }

  function setStatus(text) {
    statusText.textContent = text;
  }

  // 初始化站点选择器
  async function initSites() {
    const data = await apiGet('/api/files?path=');
    const sites = (data.items || []).filter(i => i.type === 'directory');
    siteSelector.innerHTML = '';
    sites.forEach(site => {
      const opt = document.createElement('option');
      opt.value = site.name;
      opt.textContent = site.name;
      siteSelector.appendChild(opt);
    });
    if (sites.length > 0) {
      currentSite = sites[0].name;
      loadFileTree('');
    }
  }

  siteSelector.addEventListener('change', () => {
    currentSite = siteSelector.value;
    currentDir = '';
    currentFile = '';
    openFiles = [];
    activeFile = '';
    fileContents = {};
    modifiedFiles.clear();
    editorMode = 'none';
    renderEditor();
    loadFileTree('');
  });

  // 文件树
  async function loadFileTree(relPath) {
    const path = currentSite + (relPath ? '/' + relPath : '');
    const data = await apiGet('/api/files?path=' + encodeURIComponent(path));
    const items = data.items || [];
    renderTreeItems(items, relPath);
  }

  function renderTreeItems(items, parentRelPath) {
    const container = parentRelPath ? document.getElementById('tree-children-' + escapeId(parentRelPath)) : fileTree;
    if (!container) return;
    container.innerHTML = '';

    items.forEach(item => {
      const el = document.createElement('div');
      el.className = 'tree-item';
      el.dataset.path = item.path;
      el.dataset.type = item.type;

      const toggle = document.createElement('span');
      toggle.className = 'toggle' + (item.type === 'directory' ? '' : ' empty');
      toggle.textContent = item.type === 'directory' ? '▶' : '';
      el.appendChild(toggle);

      const icon = document.createElement('span');
      icon.className = 'icon';
      icon.textContent = item.type === 'directory' ? '📁' : '📄';
      el.appendChild(icon);

      const name = document.createElement('span');
      name.className = 'name';
      name.textContent = item.name;
      el.appendChild(name);

      if (item.type === 'directory') {
        const childContainer = document.createElement('div');
        childContainer.className = 'tree-children';
        childContainer.id = 'tree-children-' + escapeId(item.path);
        el.appendChild(childContainer);

        toggle.addEventListener('click', (e) => {
          e.stopPropagation();
          if (childContainer.classList.contains('expanded')) {
            childContainer.classList.remove('expanded');
            toggle.textContent = '▶';
          } else {
            childContainer.classList.add('expanded');
            toggle.textContent = '▼';
            if (childContainer.children.length === 0) {
              const rel = item.path.replace(currentSite + '/', '');
              loadFileTree(rel);
            }
          }
        });
      }

      el.addEventListener('click', () => {
        document.querySelectorAll('.tree-item.active').forEach(a => a.classList.remove('active'));
        el.classList.add('active');
        if (item.type === 'directory') {
          onSelectDirectory(item.path);
        } else {
          onSelectFile(item.path);
        }
      });

      container.appendChild(el);
    });
  }

  function escapeId(path) {
    return path.replace(/[^a-zA-Z0-9]/g, '_');
  }

  // 选择目录
  async function onSelectDirectory(path) {
    currentDir = path;
    currentFile = '';

    // 检测模式
    const hasPage = await checkFileExists(path + '/page.md');
    const hasMeta = await checkFileExists(path + '/meta.md');

    if (hasPage) {
      editorMode = 'single';
      openFile(path + '/page.md');
    } else if (hasMeta) {
      editorMode = 'multi';
      await openMultiMode(path);
    } else {
      editorMode = 'none';
      renderEditor();
    }
  }

  async function checkFileExists(path) {
    try {
      const data = await apiGet('/api/file/exists?path=' + encodeURIComponent(path));
      return data.exists && data.is_file;
    } catch {
      return false;
    }
  }

  // 选择文件
  async function onSelectFile(path) {
    currentFile = path;
    openFile(path);
  }

  async function openFile(path) {
    if (!openFiles.includes(path)) {
      openFiles.push(path);
    }
    activeFile = path;

    if (!fileContents.hasOwnProperty(path)) {
      try {
        const data = await apiGet('/api/file?path=' + encodeURIComponent(path));
        fileContents[path] = data.content;
      } catch (e) {
        showToast('读取文件失败: ' + e.message, 'error');
        return;
      }
    }

    renderEditor();
    editorTextarea.value = fileContents[path] || '';
    updatePreview();
  }

  async function openMultiMode(dirPath) {
    // 读取 meta.md 和章节文件
    const metaPath = dirPath + '/meta.md';
    if (!fileContents.hasOwnProperty(metaPath)) {
      try {
        const data = await apiGet('/api/file?path=' + encodeURIComponent(metaPath));
        fileContents[metaPath] = data.content;
      } catch (e) {
        fileContents[metaPath] = '---\ntitle: \n---\n';
      }
    }

    // 扫描章节文件
    const dirRel = dirPath.replace(currentSite + '/', '');
    const listData = await apiGet('/api/files?path=' + encodeURIComponent(dirPath));
    const chapters = (listData.items || []).filter(i => /^\d{2}-.*\.md$/.test(i.name) && i.type === 'file');

    for (const ch of chapters) {
      if (!fileContents.hasOwnProperty(ch.path)) {
        try {
          const data = await apiGet('/api/file?path=' + encodeURIComponent(ch.path));
          fileContents[ch.path] = data.content;
        } catch {
          fileContents[ch.path] = '---\ntitle: \n---\n';
        }
      }
    }

    openFiles = [metaPath, ...chapters.map(c => c.path)];
    activeFile = metaPath;
    renderEditor();
    editorTextarea.value = fileContents[metaPath] || '';
    updatePreview();
  }

  // 渲染编辑器
  function renderEditor() {
    if (editorMode === 'none') {
      editorEmpty.style.display = 'flex';
      editorContent.style.display = 'none';
      return;
    }

    editorEmpty.style.display = 'none';
    editorContent.style.display = 'flex';

    // 标签页
    editorTabs.innerHTML = '';
    openFiles.forEach(path => {
      const tab = document.createElement('div');
      tab.className = 'editor-tab' + (path === activeFile ? ' active' : '');
      const name = path.split('/').pop();
      const isModified = modifiedFiles.has(path);
      tab.innerHTML = '<span>' + escapeHtml(name) + (isModified ? ' ●' : '') + '</span>';
      if (openFiles.length > 1) {
        const close = document.createElement('span');
        close.className = 'close';
        close.innerHTML = '×';
        close.addEventListener('click', (e) => {
          e.stopPropagation();
          closeFile(path);
        });
        tab.appendChild(close);
      }
      tab.addEventListener('click', () => {
        switchToFile(path);
      });
      editorTabs.appendChild(tab);
    });

    // 章节列表（多 MD 模式）
    if (editorMode === 'multi') {
      chapterList.style.display = 'block';
      renderChapterList();
    } else {
      chapterList.style.display = 'none';
    }
  }

  function renderChapterList() {
    const metaPath = currentDir + '/meta.md';
    const chapters = openFiles.filter(p => p !== metaPath && /^\d{2}-/.test(p.split('/').pop()));

    let html = '<h4>章节</h4>';
    html += '<div class="chapter-item' + (activeFile === metaPath ? ' active' : '') + '" data-path="' + escapeHtml(metaPath) + '">';
    html += '<span class="chapter-name">meta.md (元数据)</span></div>';

    chapters.forEach(ch => {
      const name = ch.split('/').pop();
      html += '<div class="chapter-item' + (activeFile === ch ? ' active' : '') + '" data-path="' + escapeHtml(ch) + '">';
      html += '<span class="chapter-name">' + escapeHtml(name) + '</span>';
      html += '<span class="chapter-del" data-path="' + escapeHtml(ch) + '">×</span></div>';
    });

    html += '<button class="add-chapter-btn" id="addChapterBtn">+ 添加章节</button>';
    chapterList.innerHTML = html;

    chapterList.querySelectorAll('.chapter-item').forEach(el => {
      el.addEventListener('click', () => {
        switchToFile(el.dataset.path);
      });
    });

    chapterList.querySelectorAll('.chapter-del').forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteChapter(el.dataset.path);
      });
    });

    const addBtn = document.getElementById('addChapterBtn');
    if (addBtn) {
      addBtn.addEventListener('click', addChapter);
    }
  }

  function switchToFile(path) {
    if (activeFile === path) return;
    // 保存当前内容
    if (activeFile) {
      fileContents[activeFile] = editorTextarea.value;
    }
    activeFile = path;
    renderEditor();
    editorTextarea.value = fileContents[path] || '';
    updatePreview();
  }

  function closeFile(path) {
    if (modifiedFiles.has(path)) {
      if (!confirm('文件已修改，确定关闭吗？')) return;
    }
    const idx = openFiles.indexOf(path);
    openFiles = openFiles.filter(p => p !== path);
    delete fileContents[path];
    modifiedFiles.delete(path);

    if (activeFile === path) {
      activeFile = openFiles.length > 0 ? openFiles[Math.max(0, idx - 1)] : '';
      if (activeFile) {
        editorTextarea.value = fileContents[activeFile] || '';
      }
    }
    renderEditor();
    if (activeFile) updatePreview();
  }

  async function addChapter() {
    const dirPath = currentDir;
    const listData = await apiGet('/api/files?path=' + encodeURIComponent(dirPath));
    const existing = (listData.items || []).filter(i => /^\d{2}-/.test(i.name));
    const nextNum = String(existing.length + 1).padStart(2, '0');
    const filename = nextNum + '-new-chapter.md';
    const path = dirPath + '/' + filename;
    const content = '---\ntitle: 新章节\n---\n\n';

    await apiPost('/api/file', { path, content });
    fileContents[path] = content;
    openFiles.push(path);
    switchToFile(path);
    showToast('章节已添加', 'success');
  }

  async function deleteChapter(path) {
    if (!confirm('确定删除章节 ' + path.split('/').pop() + ' 吗？')) return;
    await apiDelete('/api/file?path=' + encodeURIComponent(path));
    closeFile(path);
    showToast('章节已删除', 'success');
  }

  // 编辑器输入
  editorTextarea.addEventListener('input', () => {
    if (activeFile) {
      fileContents[activeFile] = editorTextarea.value;
      modifiedFiles.add(activeFile);
      renderEditor();
    }
    updatePreview();
    triggerAutoCompile();
  });

  editorTextarea.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = editorTextarea.selectionStart;
      const end = editorTextarea.selectionEnd;
      editorTextarea.setRangeText('  ', start, end, 'end');
    }
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      saveCurrentFile();
    }
  });

  // 粘贴图片
  editorTextarea.addEventListener('paste', async (e) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.type.indexOf('image') !== -1) {
        e.preventDefault();
        const blob = item.getAsFile();
        const reader = new FileReader();
        reader.onload = async (ev) => {
          const base64 = ev.target.result;
          const ext = blob.type === 'image/png' ? 'png' : (blob.type === 'image/jpeg' ? 'jpg' : 'png');
          const timestamp = Date.now();
          const dirPath = currentDir || (currentFile ? currentFile.substring(0, currentFile.lastIndexOf('/')) : currentSite);
          const imgPath = dirPath + '/img/paste-' + timestamp + '.' + ext;
          try {
            await apiPost('/api/file/upload', { path: imgPath, data: base64 });
            const imgName = 'img/paste-' + timestamp + '.' + ext;
            const md = '![' + imgName + '](' + imgName + ')';
            const start = editorTextarea.selectionStart;
            const end = editorTextarea.selectionEnd;
            editorTextarea.setRangeText(md, start, end, 'end');
            fileContents[activeFile] = editorTextarea.value;
            modifiedFiles.add(activeFile);
            updatePreview();
            showToast('图片已粘贴', 'success');
          } catch (err) {
            showToast('图片上传失败: ' + err.message, 'error');
          }
        };
        reader.readAsDataURL(blob);
        break;
      }
    }
  });

  // 保存
  async function saveCurrentFile() {
    if (!activeFile) return;
    fileContents[activeFile] = editorTextarea.value;
    try {
      await apiPost('/api/file', { path: activeFile, content: fileContents[activeFile] });
      modifiedFiles.delete(activeFile);
      renderEditor();
      showToast('保存成功', 'success');
    } catch (e) {
      showToast('保存失败: ' + e.message, 'error');
    }
  }

  document.getElementById('btnSave').addEventListener('click', saveCurrentFile);

  // 编译
  async function compileCurrentPage() {
    if (!currentDir) {
      showToast('请先选择一个页面目录', 'error');
      return;
    }
    // 先保存所有修改
    for (const path of modifiedFiles) {
      try {
        await apiPost('/api/file', { path, content: fileContents[path] });
      } catch (e) {
        showToast('保存失败: ' + path + ' - ' + e.message, 'error');
        return;
      }
    }
    modifiedFiles.clear();
    renderEditor();

    try {
      setStatus('编译中...');
      const result = await apiPost('/api/build', { path: currentDir });
      setStatus('编译成功');
      showToast('编译成功: ' + result.path, 'success');
    } catch (e) {
      setStatus('编译失败');
      showToast('编译失败: ' + e.message, 'error');
    }
  }

  document.getElementById('btnCompile').addEventListener('click', compileCurrentPage);

  // 自动编译
  function triggerAutoCompile() {
    isTyping = true;
    if (compileDebounceTimer) clearTimeout(compileDebounceTimer);
    compileDebounceTimer = setTimeout(() => {
      isTyping = false;
    }, 3000);
  }

  // 每1秒检查：如果不在输入状态且存在未编译的修改，则执行编译
  setInterval(() => {
    if (!isTyping && modifiedFiles.size > 0 && currentDir && (editorMode === 'single' || editorMode === 'multi')) {
      compileCurrentPage();
    }
  }, 1000);

  // Markdown 预览渲染
  function updatePreview() {
    const text = editorTextarea.value || '';
    previewContent.innerHTML = renderMarkdown(text);
  }

  function renderMarkdown(text) {
    if (!text) return '<p style="color:#666;">无内容</p>';

    let html = escapeHtml(text);

    // 代码块
    html = html.replace(/```(\w*)\n([\s\S]*?)\n```/g, (match, lang, code) => {
      return '<pre><code>' + code + '</code></pre>';
    });

    // 围栏块 ::: type
    html = html.replace(/:::\s*(\w+)\n([\s\S]*?)\n:::/g, (match, type, content) => {
      return '<pre><code>::: ' + type + '\n' + content + '\n:::</code></pre>';
    });

    // 图片
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

    // 链接
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

    // 加粗
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // 斜体
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

    // 行内代码
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 标题
    html = html.replace(/^######\s(.+)$/gm, '<h6>$1</h6>');
    html = html.replace(/^#####\s(.+)$/gm, '<h5>$1</h5>');
    html = html.replace(/^####\s(.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^###\s(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^##\s(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^#\s(.+)$/gm, '<h1>$1</h1>');

    // 引用
    html = html.replace(/^&gt;\s(.+)$/gm, '<blockquote>$1</blockquote>');

    // 无序列表
    html = html.replace(/^(\s*)-\s(.+)$/gm, (match, indent, content) => {
      return '<li>' + content + '</li>';
    });

    // 有序列表
    html = html.replace(/^(\s*)\d+\.\s(.+)$/gm, (match, indent, content) => {
      return '<li>' + content + '</li>';
    });

    // 表格
    html = html.replace(/^(\|.+\|)$/gm, (match) => {
      const cells = match.slice(1, -1).split('|').map(c => '<td>' + c.trim() + '</td>').join('');
      return '<tr>' + cells + '</tr>';
    });

    // 分隔线
    html = html.replace(/^---$/gm, '<hr>');

    // 段落换行
    const paragraphs = html.split('\n\n');
    html = paragraphs.map(p => {
      const trimmed = p.trim();
      if (!trimmed) return '';
      if (trimmed.startsWith('<h') || trimmed.startsWith('<pre') || trimmed.startsWith('<blockquote') ||
          trimmed.startsWith('<li') || trimmed.startsWith('<tr') || trimmed.startsWith('<hr')) {
        return trimmed;
      }
      return '<p>' + trimmed.replace(/\n/g, '<br>') + '</p>';
    }).join('\n');

    // 包裹表格行
    html = html.replace(/(<tr>.+<\/tr>)/gs, '<table>$1</table>');

    // 包裹列表项
    html = html.replace(/(<li>.+<\/li>)/gs, '<ul>$1</ul>');

    return html;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // 新建文件/目录
  let newModalType = 'file';
  let newModalTargetDir = '';

  document.getElementById('btnNewFile').addEventListener('click', () => {
    newModalType = 'file';
    newModalTargetDir = currentDir || currentSite;
    modalTitle.textContent = '新建文件';
    modalInput.value = '';
    modalInput.placeholder = '文件名，如 page.md';
    newFileModal.classList.remove('hidden');
    modalInput.focus();
  });

  document.getElementById('btnNewDir').addEventListener('click', () => {
    newModalType = 'directory';
    newModalTargetDir = currentDir || currentSite;
    modalTitle.textContent = '新建目录';
    modalInput.value = '';
    modalInput.placeholder = '目录名';
    newFileModal.classList.remove('hidden');
    modalInput.focus();
  });

  document.getElementById('modalCancel').addEventListener('click', () => {
    newFileModal.classList.add('hidden');
  });

  newFileModal.addEventListener('click', (e) => {
    if (e.target === newFileModal) newFileModal.classList.add('hidden');
  });

  document.getElementById('modalConfirm').addEventListener('click', async () => {
    const name = modalInput.value.trim();
    if (!name) return;

    const path = newModalTargetDir + '/' + name;
    try {
      if (newModalType === 'file') {
        await apiPost('/api/file', { path, content: '' });
        showToast('文件已创建', 'success');
      } else {
        await apiPost('/api/file', { path: path + '/.gitkeep', content: '' });
        showToast('目录已创建', 'success');
      }
      newFileModal.classList.add('hidden');
      // 刷新文件树
      const parentRel = newModalTargetDir.replace(currentSite + '/', '');
      const parentEl = document.getElementById('tree-children-' + escapeId(newModalTargetDir));
      if (parentEl) {
        parentEl.classList.add('expanded');
        await loadFileTree(parentRel);
      } else {
        await loadFileTree('');
      }
    } catch (e) {
      showToast('创建失败: ' + e.message, 'error');
    }
  });

  modalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('modalConfirm').click();
    if (e.key === 'Escape') newFileModal.classList.add('hidden');
  });

  // 设置数据根目录
  document.getElementById('btnSetRoot').addEventListener('click', async () => {
    try {
      const config = await apiGet('/api/config');
      rootInput.value = config.data_root || '';
      setRootModal.classList.remove('hidden');
      rootInput.focus();
    } catch (e) {
      showToast('获取配置失败: ' + e.message, 'error');
    }
  });

  document.getElementById('rootCancel').addEventListener('click', () => {
    setRootModal.classList.add('hidden');
  });

  setRootModal.addEventListener('click', (e) => {
    if (e.target === setRootModal) setRootModal.classList.add('hidden');
  });

  document.getElementById('rootConfirm').addEventListener('click', async () => {
    const newRoot = rootInput.value.trim();
    if (!newRoot) return;
    try {
      await apiPost('/api/config', { data_root: newRoot });
      setRootModal.classList.add('hidden');
      showToast('数据根目录已设置', 'success');
      // 重置状态并重新加载
      currentSite = '';
      currentDir = '';
      currentFile = '';
      openFiles = [];
      activeFile = '';
      fileContents = {};
      modifiedFiles.clear();
      editorMode = 'none';
      renderEditor();
      initSites();
    } catch (e) {
      showToast('设置失败: ' + e.message, 'error');
    }
  });

  rootInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('rootConfirm').click();
    if (e.key === 'Escape') setRootModal.classList.add('hidden');
  });

  // 初始化
  initSites().catch(e => {
    showToast('初始化失败: ' + e.message, 'error');
  });
})();
