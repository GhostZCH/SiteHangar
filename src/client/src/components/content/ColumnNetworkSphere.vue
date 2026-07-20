<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { publicApi } from '@/api/public';
import type { ModuleCard, CategoryNode } from '@/types/content';

const props = defineProps<{ modules: ModuleCard[] }>();
const router = useRouter();

const canvasRef = ref<HTMLCanvasElement | null>(null);
const wrapRef = ref<HTMLDivElement | null>(null);
const tip = ref<{ text: string; x: number; y: number } | null>(null);
const ready = ref(false);

interface NetNode {
  x: number; y: number; z: number;
  size: number;
  color: [number, number, number];
  glow: number;
  tw: number;
  type: 'shell' | 'column' | 'category' | 'article';
  label?: string;
  link?: string;
}
type Link = [number, number, number];

const nodes: NetNode[] = [];
const links: Link[] = [];

function hsl(h: number, s: number, l: number): [number, number, number] {
  s /= 100; l /= 100;
  const k = (n: number) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  return [Math.round(f(0) * 255), Math.round(f(8) * 255), Math.round(f(4) * 255)];
}

function spherePoint(radius: number) {
  const u = Math.random() * 2 - 1;
  const t = Math.random() * Math.PI * 2;
  const s = Math.sqrt(1 - u * u);
  return { x: radius * s * Math.cos(t), y: radius * s * Math.sin(t), z: radius * u };
}

const rand = (a: number, b: number) => a + Math.random() * (b - a);

// 栏目基础色相（每个栏目一个色系）
const COLUMN_HUES = [172, 42, 268, 205, 330, 0, 100, 235];

function buildGraph(R: number, categoryMap: Map<string, CategoryNode[]>) {
  nodes.length = 0;
  links.length = 0;

  // 外围稀疏球壳
  const shellColor = hsl(215, 18, 78);
  for (let i = 0; i < 420; i++) {
    nodes.push({ ...spherePoint(R * rand(0.86, 1.0)), size: rand(0.6, 1.4), color: shellColor, glow: 0, tw: Math.random() * 6, type: 'shell' });
  }

  // 栏目簇均匀分布在球体内部
  const count = props.modules.length;
  props.modules.forEach((m, mi) => {
    const golden = Math.PI * (3 - Math.sqrt(5));
    const y = count === 1 ? 0 : 1 - (mi / Math.max(count - 1, 1)) * 2;
    const rad = Math.sqrt(Math.max(0, 1 - y * y));
    const theta = golden * mi;
    const cr = R * 0.42;
    const cx = Math.cos(theta) * rad * cr;
    const cy = y * cr * 0.85;
    const cz = Math.sin(theta) * rad * cr * 0.7;

    const hue = COLUMN_HUES[mi % COLUMN_HUES.length];
    const colColor = hsl(hue, 75, 72);
    const colIdx = nodes.length;
    nodes.push({ x: cx, y: cy, z: cz, size: 3.2, color: [255, 255, 255], glow: 18, tw: Math.random() * 6, type: 'column', label: m.title, link: m.link });

    const cats = categoryMap.get(m.id) || [];
    const spread = R * (count > 2 ? 0.24 : 0.3);
    let prev = colIdx;
    cats.forEach((cat, ci) => {
      // 同一栏目下每个分类一个色相，文章继承分类色（同色系）
      const catHue = (hue + ci * 28) % 360;
      const catColor = hsl(catHue, 78, 68);
      const artColor = hsl(catHue, 62, 60);
      const a = (ci / Math.max(cats.length, 1)) * Math.PI * 2 + rand(-0.4, 0.4);
      const d = spread * rand(0.5, 1);
      const ccx = cx + Math.cos(a) * d;
      const ccy = cy + Math.sin(a) * d;
      const ccz = cz + rand(-spread, spread) * 0.4;
      const catIdx = nodes.length;
      nodes.push({ x: ccx, y: ccy, z: ccz, size: 2.2, color: catColor, glow: 9, tw: Math.random() * 6, type: 'category', label: cat.name });
      links.push([colIdx, catIdx, 0.35]);

      const articles = cat.links || [];
      const shown = articles.slice(0, 14);
      let prevArt = catIdx;
      shown.forEach((l, ai) => {
        const aa = Math.random() * Math.PI * 2;
        const ad = spread * rand(0.2, 0.62);
        const idx = nodes.length;
        nodes.push({
          x: ccx + Math.cos(aa) * ad,
          y: ccy + Math.sin(aa) * ad,
          z: ccz + rand(-ad, ad) * 0.5,
          size: rand(0.9, 1.6), color: artColor, glow: 4, tw: Math.random() * 6,
          type: 'article', label: l.title, link: l.url,
        });
        links.push([Math.random() < 0.7 ? catIdx : prevArt, idx, rand(0.18, 0.4)]);
        prevArt = idx;
      });
      prev = catIdx;
    });
  });

  // 栏目之间的稀疏长连线
  for (let i = 0; i < Math.min(40, nodes.length / 8); i++) {
    const a = (Math.random() * nodes.length) | 0;
    const b = (Math.random() * nodes.length) | 0;
    if (a !== b) links.push([a, b, rand(0.03, 0.09)]);
  }
}

// ---------- 渲染 ----------
let raf = 0;
let rotY = 0, rotX = 0.25;
let dragging = false, px = 0, py = 0, moved = 0;
let proj: { x: number; y: number; d: number }[] = [];
const FOV = 3.2;

function draw(time: number) {
  const canvas = canvasRef.value, wrap = wrapRef.value;
  if (!canvas || !wrap) return;
  const ctx = canvas.getContext('2d')!;
  const dpr = devicePixelRatio || 1;
  const w = wrap.clientWidth, h = wrap.clientHeight;
  if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
    canvas.width = w * dpr;
    canvas.height = h * dpr;
  }
  const W = canvas.width, H = canvas.height;
  const R = Math.min(W, H) * 0.36;

  ctx.clearRect(0, 0, W, H);
  if (!dragging) rotY += 0.0016;

  const cx = W / 2, cy = H / 2;
  const sy = Math.sin(rotY), cyv = Math.cos(rotY);
  const sx = Math.sin(rotX), cxv = Math.cos(rotX);

  proj = new Array(nodes.length);
  for (let i = 0; i < nodes.length; i++) {
    const n = nodes[i];
    let x = n.x * cyv - n.z * sy;
    let z = n.x * sy + n.z * cyv;
    let y = n.y * cxv - z * sx;
    const depth = FOV / (FOV + z / R);
    proj[i] = { x: cx + x * depth, y: cy + y * depth, d: depth };
  }

  ctx.globalCompositeOperation = 'lighter';
  ctx.lineWidth = dpr * 0.6;
  for (const [a, b, alpha] of links) {
    const pa = proj[a], pb = proj[b];
    const c = nodes[a].glow >= nodes[b].glow ? nodes[a].color : nodes[b].color;
    ctx.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${alpha * (pa.d + pb.d) * 0.5})`;
    ctx.beginPath();
    ctx.moveTo(pa.x, pa.y);
    ctx.lineTo(pb.x, pb.y);
    ctx.stroke();
  }

  for (let i = 0; i < nodes.length; i++) {
    const n = nodes[i], p = proj[i];
    const twinkle = 0.72 + 0.28 * Math.sin(time * 0.002 + n.tw);
    const size = n.size * p.d * dpr * twinkle;
    const [r, g, b] = n.color;
    const alpha = Math.min(1, 0.6 * p.d) * twinkle;

    if (n.glow > 0) {
      const gr = size * (n.type === 'column' ? 8 : 4.5);
      const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, gr);
      grad.addColorStop(0, `rgba(${r},${g},${b},${alpha * 0.5})`);
      grad.addColorStop(0.4, `rgba(${r},${g},${b},${alpha * 0.12})`);
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(p.x, p.y, gr, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = n.type === 'column' ? `rgba(255,255,255,${alpha})` : `rgba(${r},${g},${b},${alpha})`;
    ctx.beginPath();
    ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
    ctx.fill();
  }

  // 边缘暗角（无边界融入背景）
  ctx.globalCompositeOperation = 'source-over';
  const vg = ctx.createRadialGradient(cx, cy, R * 1.02, cx, cy, R * 1.38);
  vg.addColorStop(0, 'rgba(0,0,0,0)');
  vg.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = vg;
  ctx.fillRect(0, 0, W, H);

  raf = requestAnimationFrame(draw);
}

// ---------- 交互 ----------
function hitNode(e: MouseEvent): number {
  const canvas = canvasRef.value;
  if (!canvas) return -1;
  const rect = canvas.getBoundingClientRect();
  const dpr = devicePixelRatio || 1;
  const mx = (e.clientX - rect.left) * dpr;
  const my = (e.clientY - rect.top) * dpr;
  let best = -1, bestD = 18 * dpr;
  for (let i = 0; i < proj.length; i++) {
    const n = nodes[i];
    if (n.type === 'shell') continue;
    const dx = proj[i].x - mx, dy = proj[i].y - my;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const hitR = Math.max(bestD, n.size * 3 * dpr);
    if (dist < hitR && (best === -1 || dist < bestD)) { best = i; bestD = dist; }
  }
  return best;
}

function onDown(e: PointerEvent) { dragging = true; moved = 0; px = e.clientX; py = e.clientY; }
function onUp(e: PointerEvent) {
  if (dragging && moved < 6) {
    const idx = hitNode(e);
    if (idx >= 0 && nodes[idx].link) router.push(nodes[idx].link!);
  }
  dragging = false;
}
function onMove(e: PointerEvent) {
  if (dragging) {
    moved += Math.abs(e.clientX - px) + Math.abs(e.clientY - py);
    rotY += (e.clientX - px) * 0.005;
    rotX = Math.max(-1.2, Math.min(1.2, rotX + (e.clientY - py) * 0.005));
    px = e.clientX; py = e.clientY;
    tip.value = null;
    return;
  }
  const idx = hitNode(e);
  if (idx >= 0 && nodes[idx].label) {
    tip.value = { text: nodes[idx].label!, x: e.clientX + 12, y: e.clientY + 10 };
    canvasRef.value!.style.cursor = nodes[idx].link ? 'pointer' : 'default';
  } else {
    tip.value = null;
    if (canvasRef.value) canvasRef.value.style.cursor = 'grab';
  }
}

onMounted(async () => {
  // 拉取每个栏目的分类数据（栏目→分类→文章）
  const categoryMap = new Map<string, CategoryNode[]>();
  await Promise.all(props.modules.map(async (m) => {
    try {
      const res = await publicApi.render([m.id]);
      categoryMap.set(m.id, res.data.categories || []);
    } catch { categoryMap.set(m.id, []); }
  }));
  buildGraph(100, categoryMap);
  ready.value = true;
  raf = requestAnimationFrame(draw);
});

onUnmounted(() => cancelAnimationFrame(raf));
</script>

<template>
  <div ref="wrapRef" class="column-sphere">
    <canvas
      ref="canvasRef"
      class="column-sphere-canvas"
      @pointerdown="onDown"
      @pointerup="onUp"
      @pointermove="onMove"
      @pointerleave="tip = null"
    ></canvas>
    <div v-if="tip" class="column-sphere-tip" :style="{ left: tip.x + 'px', top: tip.y + 'px' }">
      {{ tip.text }}
    </div>
  </div>
</template>

<style scoped>
.column-sphere {
  position: relative;
  width: min(720px, 92vw);
  height: min(560px, 70vh);
  margin: 64px auto 0;
}
.column-sphere-canvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
}
.column-sphere-canvas:active { cursor: grabbing; }
.column-sphere-tip {
  position: fixed;
  z-index: 60;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(12, 16, 28, 0.85);
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  pointer-events: none;
  white-space: nowrap;
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
