<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useSiteStore } from '@/stores/site';
import { renderMathInline, renderMathBlock, onKatexReady } from '@/composables/useKatex';
import MermaidBlock from './MermaidBlock.vue';
import TreeBlock from './TreeBlock.vue';

const props = defineProps<{ items: string[] }>();
const route = useRoute();
const siteStore = useSiteStore();

// katex 加载完成后触发重渲染（公式占位符替换为真实渲染结果）
const katexReady = ref(false);
let offKatexReady: (() => void) | null = null;
onMounted(() => {
  offKatexReady = onKatexReady(() => {
    katexReady.value = true;
  });
});
onUnmounted(() => {
  offKatexReady?.();
});

function getPageAssetBaseUrl(): string {
  const site = siteStore.siteSlug || 'www';
  const moduleSlug = (route.params.moduleSlug as string) || '';
  const pathParam = route.params.path;
  const pathRest = Array.isArray(pathParam) ? pathParam : pathParam ? [pathParam] : [];
  const pagePath = pathRest.join('/');
  // 构建完整路径：site/moduleSlug/pagePath
  const fullPath = moduleSlug ? `${moduleSlug}/${pagePath}` : pagePath;
  return `/api/page-asset/${site}/${fullPath}`;
}

function resolveAssetPath(src: string): string {
  if (src.startsWith('http://') || src.startsWith('https://') || src.startsWith('/')) {
    return src;
  }
  const baseUrl = getPageAssetBaseUrl();
  return `${baseUrl}/${src}`;
}

function getHeadingText(text: string): string {
  if (text.startsWith('#### ')) return text.slice(5);
  if (text.startsWith('### ')) return text.slice(4);
  if (text.startsWith('## ')) return text.slice(3);
  return text;
}

function getHeadingLevel(text: string): number {
  if (text.startsWith('#### ')) return 4;
  if (text.startsWith('### ')) return 3;
  if (text.startsWith('## ')) return 2;
  return 0;
}

function extractSpecialBlocks(text: string): Array<{ type: 'text' | 'mermaid' | 'tree'; content: string }> {
  const parts: Array<{ type: 'text' | 'mermaid' | 'tree'; content: string }> = [];
  const regex = /```(mermaid|tree)\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: text.slice(lastIndex, match.index) });
    }
    parts.push({ type: match[1] as 'mermaid' | 'tree', content: match[2].trim() });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push({ type: 'text', content: text.slice(lastIndex) });
  }

  if (parts.length === 0) {
    parts.push({ type: 'text', content: text });
  }

  return parts;
}

function renderMarkdown(text: string): string {
  // 先处理代码块，避免内部内容被其他规则处理
  // 处理代码块 ```...```（排除 mermaid 和 tree）
  let result = text.replace(
    /```(?!mermaid|tree)(\w*)\n?([\s\S]*?)```/g,
    (match, lang, code) => {
      const escaped = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const langLabel = lang ? `<div class="code-lang-label">${lang}</div>` : '';
      // 添加行号
      const lines = escaped.split('\n');
      // 移除末尾的空行，避免最后一行是空行时多出行号
      while (lines.length > 0 && lines[lines.length - 1] === '') {
        lines.pop();
      }
      const lineNumbers = lines.map((_, i) => `<span class="line-num">${i + 1}</span>`).join('');
      const codeWithLines = lines.map(line => `<span class="code-line">${line || ' '}</span>`).join('');
      return `<pre class="code-block">${langLabel}<div class="code-wrapper"><div class="line-numbers">${lineNumbers}</div><code>${codeWithLines}</code></div></pre>`;
    }
  );
  // 处理公式：块级公式 $$...$$
  result = result.replace(
    /\$\$([\s\S]*?)\$\$/g,
    (match, formula) => `<span class="math-block">${renderMathBlock(formula)}</span>`
  );
  // 处理公式：行内公式 $...$
  result = result.replace(
    /\$([^\s$][^$]*?)\$/g,
    (match, formula) => `<span class="math-inline">${renderMathInline(formula)}</span>`
  );
  // 处理二级标题 ## heading
  result = result.replace(
    /^##\s+(.+)$/gm,
    '<h2 class="md-heading">$1</h2>'
  );
  // 处理三级标题 ### heading
  result = result.replace(
    /^###\s+(.+)$/gm,
    '<h3 class="md-heading">$1</h3>'
  );
  // 处理四级标题 #### heading
  result = result.replace(
    /^####\s+(.+)$/gm,
    '<h4 class="md-heading">$1</h4>'
  );
  result = result.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong>$1</strong>'
  );
  // 处理斜体 *text*
  result = result.replace(
    /(?<!\*)\*([^*]+)\*(?!\*)/g,
    '<em>$1</em>'
  );
  // 处理行内代码 `code`
  result = result.replace(
    /`([^`]+)`/g,
    '<code>$1</code>'
  );
  // 处理图片 ![image](url)
  result = result.replace(
    /!\[image\]\(([^)]+)\)/g,
    (match, src) => {
      const resolvedSrc = resolveAssetPath(src);
      return `<img src="${resolvedSrc}" alt="" class="md-image" />`;
    }
  );
  // 处理链接 [text](url)
  result = result.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener">$1</a>'
  );
  // 处理引用 > text
  result = result.replace(
    /^>\s+(.+)$/gm,
    '<blockquote>$1</blockquote>'
  );
  // 处理无序列表项（在段落中）
  result = result.replace(
    /^-\s+(.+)$/gm,
    '<li>$1</li>'
  );
  // 处理有序列表项（在段落中）
  result = result.replace(
    /^\d+\.\s+(.+)$/gm,
    '<li>$1</li>'
  );
  // 如果包含 <li> 但没有 <ul> 或 <ol>，自动包裹
  if (result.includes('<li>') && !result.includes('<ul>') && !result.includes('<ol>')) {
    result = '<ul>' + result + '</ul>';
  }
  // 处理段落分隔：将空行分隔的文本拆分为多个 <p> 段落
  // 但不对已经包含块级元素的文本进行拆分
  if (!result.includes('<pre') && !result.includes('<ul>') && !result.includes('<ol>') && !result.includes('<blockquote')) {
    const paragraphs = result.split(/\n\n+/).filter(p => p.trim());
    if (paragraphs.length > 1) {
      result = paragraphs.map(p => `<p>${p.trim()}</p>`).join('');
    }
  }
  return result;
}

interface RenderedPart {
  type: 'text' | 'mermaid' | 'tree';
  content: string;
  /** 仅 text 类型：预计算的 HTML */
  html?: string;
  /** 仅 text 类型：是否为列表 */
  isList?: boolean;
}

interface RenderedItem {
  headingLevel: number;
  headingText: string;
  parts: RenderedPart[];
}

/**
 * 预计算所有段落的 markdown 渲染结果。
 * 依赖 katexReady：katex 加载完成后重算，将公式占位替换为真实渲染。
 * 避免模板中对同一 content 重复调用 renderMarkdown（含高成本 katex/正则）。
 */
const renderedItems = computed<RenderedItem[]>(() => {
  // 显式依赖，katex 就绪后触发重算
  void katexReady.value;
  return props.items.map((p) => {
    const headingLevel = getHeadingLevel(p);
    const headingText = getHeadingText(p);
    if (headingLevel > 0) {
      return { headingLevel, headingText, parts: [] };
    }
    const parts = extractSpecialBlocks(p).map((part) => {
      if (part.type !== 'text') {
        return { type: part.type, content: part.content };
      }
      const html = renderMarkdown(part.content);
      const isList = html.startsWith('<ul') || html.startsWith('<ol');
      return { type: 'text' as const, content: part.content, html, isList };
    });
    return { headingLevel, headingText, parts };
  });
});
</script>

<template>
  <div class="section-desc">
    <template v-for="(item, i) in renderedItems" :key="i">
      <h3 v-if="item.headingLevel === 2" class="desc-heading desc-heading-h2">{{ item.headingText }}</h3>
      <h4 v-else-if="item.headingLevel === 3" class="desc-heading">{{ item.headingText }}</h4>
      <h5 v-else-if="item.headingLevel === 4" class="desc-heading desc-heading-h4">{{ item.headingText }}</h5>
      <template v-else>
        <template v-for="(part, pi) in item.parts" :key="pi">
          <MermaidBlock v-if="part.type === 'mermaid'" :code="part.content" />
          <TreeBlock v-else-if="part.type === 'tree'" :code="part.content" />
          <div v-else-if="part.isList" v-html="part.html"></div>
          <p v-else v-html="part.html"></p>
        </template>
      </template>
    </template>
  </div>
</template>

<style scoped>
.section-desc :deep(.code-block) {
  display: block;
  margin: 12px 0;
  background: var(--surface-variant);
  border-radius: 8px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Cascadia Code', 'Source Code Pro', 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--on-surface);
  overflow-x: auto;
  white-space: pre;
  word-break: normal;
  border: 1px solid var(--outline-variant);
  position: relative;
  padding-top: 36px;
  padding-bottom: 0;
  padding-left: 0;
  padding-right: 0;
}

.section-desc :deep(.code-lang-label) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 6px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--outline-variant);
  border-radius: 8px 8px 0 0;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Cascadia Code', 'Source Code Pro', 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-desc :deep(.code-wrapper) {
  display: flex;
  align-items: stretch;
}

.section-desc :deep(.line-numbers) {
  display: flex;
  flex-direction: column;
  padding: 12px 8px;
  background: var(--surface);
  border-right: 1px solid var(--outline-variant);
  border-radius: 0 0 0 8px;
  text-align: right;
  user-select: none;
  flex-shrink: 0;
}

.section-desc :deep(.line-num) {
  display: block;
  font-size: 13px;
  line-height: 1.6;
  color: var(--on-surface-variant);
  min-width: 20px;
}

.section-desc :deep(.code-block code) {
  display: block;
  padding: 12px 16px;
  background: transparent;
  border-radius: 0;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  flex: 1;
  overflow-x: auto;
}

.section-desc :deep(.code-line) {
  display: block;
  line-height: 1.6;
  min-height: 1.6em;
  white-space: pre;
}

.section-desc :deep(.code-block code) {
  background: transparent;
  padding: 0;
  border-radius: 0;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

.section-desc :deep(li) {
  margin-left: 20px;
  margin-bottom: 4px;
  color: var(--on-surface);
}

.section-desc :deep(ul) {
  background: var(--surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--outline-variant);
  overflow: hidden;
  padding: 0;
  margin: 12px 0;
}

.section-desc :deep(ul li) {
  margin-left: 0;
  padding: 10px 16px;
  border-bottom: 1px solid var(--outline-variant);
  list-style: none;
  position: relative;
  transition: background 0.2s ease;
  font-size: 13px;
  line-height: 1.5;
  color: var(--on-surface);
}

.section-desc :deep(ul li:last-child) {
  border-bottom: none;
}

.section-desc :deep(ul li:hover) {
  background: rgba(84, 110, 122, 0.03);
}

.section-desc :deep(ul li::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  border-radius: 0 2px 2px 0;
  background: var(--accent);
  opacity: 0.6;
}

[data-theme="night"] .section-desc :deep(ul li:hover) {
  background: rgba(56, 189, 248, 0.05);
}

.section-desc :deep(ul ul) {
  margin: 0;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
}

.section-desc :deep(ul ul li) {
  padding: 8px 16px 8px 32px;
  font-size: 12px;
  color: var(--on-surface-variant);
  border-bottom: none;
  border-top: 1px solid var(--outline-variant);
}

.section-desc :deep(ul ul li::before) {
  width: 2px;
  height: 12px;
  opacity: 0.4;
}

.section-desc :deep(.math-block) {
  display: block;
  margin: 12px 0;
  padding: 12px 16px;
  background: var(--surface-variant);
  border-radius: 8px;
  font-family: 'KaTeX_Math', 'Times New Roman', serif;
  font-size: 16px;
  color: var(--on-surface);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.section-desc :deep(.math-inline) {
  font-family: 'KaTeX_Math', 'Times New Roman', serif;
  font-size: 15px;
  color: var(--on-surface);
  padding: 0 2px;
}

.section-desc :deep(strong) {
  font-weight: 600;
  color: var(--on-surface);
}

.section-desc :deep(.md-heading) {
  font-weight: 700;
  color: var(--on-surface);
  margin: 24px 0 12px;
  border-bottom: 1px solid var(--outline-variant);
  padding-bottom: 8px;
}

.section-desc :deep(h2.md-heading) {
  font-size: 20px;
}

.section-desc :deep(h3.md-heading) {
  font-size: 16px;
}

.section-desc :deep(h4.md-heading) {
  font-size: 14px;
}

.section-desc :deep(.desc-heading) {
  font-weight: 700;
  color: var(--on-surface);
  font-size: 16px;
  margin: 16px 0 8px;
}

.section-desc :deep(.desc-heading-h2) {
  font-size: 20px;
  margin: 24px 0 12px;
  border-bottom: 1px solid var(--outline-variant);
  padding-bottom: 8px;
}

.section-desc :deep(.desc-heading-h4) {
  font-size: 14px;
  color: var(--on-surface-variant);
  margin: 12px 0 6px;
}

.section-desc :deep(em) {
  font-style: italic;
  color: var(--on-surface-variant);
}

.section-desc :deep(code) {
  background: var(--surface-variant);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', 'Cascadia Code', 'Source Code Pro', 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--accent);
}

.section-desc :deep(a) {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.section-desc :deep(a:hover) {
  border-bottom-color: var(--accent);
}

.section-desc :deep(blockquote) {
  display: block;
  margin: 12px 0;
  padding: 12px 16px;
  border-left: 4px solid var(--accent);
  background: var(--surface-variant);
  border-radius: 0 8px 8px 0;
  color: var(--on-surface-variant);
  font-style: italic;
}

.section-desc :deep(blockquote + blockquote) {
  margin-top: -8px;
}
</style>
