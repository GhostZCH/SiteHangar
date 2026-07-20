/**
 * KaTeX 懒加载封装
 * 首次调用时动态 import katex 及其 CSS，避免拖慢首屏。
 * 加载完成后触发回调，驱动组件重新渲染公式。
 */

type Katex = typeof import('katex');

let katexPromise: Promise<Katex> | null = null;
let katexInstance: Katex | null = null;
const readyCallbacks = new Set<() => void>();

function loadKatex(): Promise<Katex> {
  if (!katexPromise) {
    katexPromise = Promise.all([
      import('katex'),
      import('katex/dist/katex.min.css'),
    ]).then(([katex]) => {
      katexInstance = katex.default ?? katex;
      readyCallbacks.forEach((cb) => cb());
      readyCallbacks.clear();
      return katexInstance;
    });
  }
  return katexPromise;
}

/** 注册 katex 加载完成回调（用于触发组件重渲染），返回注销函数 */
export function onKatexReady(cb: () => void): () => void {
  if (katexInstance) {
    cb();
    return () => {};
  }
  readyCallbacks.add(cb);
  return () => readyCallbacks.delete(cb);
}

/** 是否已加载完成（用于决定直接渲染还是显示占位） */
export function isKatexReady(): boolean {
  return katexInstance !== null;
}

function render(text: string, displayMode: boolean): string {
  // 触发懒加载；未完成时返回原文占位
  if (!katexInstance) {
    loadKatex();
    return text;
  }
  try {
    return katexInstance.renderToString(text, {
      throwOnError: false,
      displayMode,
    });
  } catch {
    return text;
  }
}

export function renderMathInline(text: string): string {
  return render(text, false);
}

export function renderMathBlock(text: string): string {
  return render(text, true);
}
