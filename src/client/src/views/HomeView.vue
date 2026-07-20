<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { publicApi } from '@/api/public';
import type { ModuleCard } from '@/types/content';

const modules = ref<ModuleCard[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// 站点配置（从 API 加载）
const siteConfig = ref<{ title?: string; brand_name?: string; subtitle?: string }>({});

// 文字解码动画
const decodedTitle = ref('');
const decodedSubtitle = ref('');
const showCursor = ref(true);
const titleTarget = computed(() => siteConfig.value.title || 'SiteHangar');
const subtitleTarget = computed(() => siteConfig.value.subtitle || '');
const brandName = computed(() => siteConfig.value.brand_name || '');
const scrambleChars = '!<>-_\/[]{}—=+*^?#________';

function scrambleText(
  target: string,
  setter: (val: string) => void,
  delay: number,
  duration: number
) {
  const startTime = Date.now() + delay;
  const length = target.length;

  function update() {
    const elapsed = Date.now() - startTime;
    if (elapsed < 0) {
      requestAnimationFrame(update);
      return;
    }
    const progress = Math.min(elapsed / duration, 1);
    const revealed = Math.floor(progress * length);
    let result = '';
    for (let i = 0; i < length; i++) {
      if (i < revealed) {
        result += target[i];
      } else {
        result += scrambleChars[Math.floor(Math.random() * scrambleChars.length)];
      }
    }
    setter(result);
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      setter(target);
    }
  }
  update();
}

const modulesSectionRef = ref<HTMLElement | null>(null);

function scrollToModules() {
  modulesSectionRef.value?.scrollIntoView({ behavior: 'smooth' });
}

// 3D 卡片鼠标跟踪
const cardRefs = ref<Map<string, HTMLElement>>(new Map());
const containerRef = ref<HTMLElement | null>(null);

function setCardRef(el: any, id: string) {
  if (el) {
    // el 可能是 Vue 组件实例，取 $el 获取真实 DOM 元素
    const domEl = el.$el || el;
    if (domEl instanceof HTMLElement) {
      cardRefs.value.set(id, domEl);
    }
  }
}

function getCardRef(id: string): HTMLElement | undefined {
  return cardRefs.value.get(id);
}

function handleCardMouseMove(e: MouseEvent, cardId: string) {
  const card = getCardRef(cardId);
  if (!card) return;
  const rect = card.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  card.style.setProperty('--mx', x + 'px');
  card.style.setProperty('--my', y + 'px');
}

function handleCardMouseLeave(cardId: string) {
  // 无需处理，纯CSS hover效果
}

// 容器视差
function handleContainerMouseMove(e: MouseEvent) {
  if (!containerRef.value) return;
  const x = (e.clientX / window.innerWidth - 0.5) * 15;
  const y = (e.clientY / window.innerHeight - 0.5) * 15;
  containerRef.value.style.transform = `rotateY(${x * 0.2}deg) rotateX(${-y * 0.2}deg)`;
}

// 浮动粒子
interface Particle {
  id: number;
  left: string;
  top: string;
  duration: string;
  size: string;
  driftY: string;
  driftX: string;
}

const floatingParticles = ref<Particle[]>([]);
let cursorInterval: ReturnType<typeof setInterval> | null = null;
let cleanupTimer: ReturnType<typeof setInterval> | null = null;
let spawnTimer: ReturnType<typeof setTimeout> | null = null;
let particleIdCounter = 0;

onUnmounted(() => {
  if (cursorInterval) clearInterval(cursorInterval);
  if (cleanupTimer) clearInterval(cleanupTimer);
  if (spawnTimer) clearTimeout(spawnTimer);
  cardRefs.value.clear();
});

onMounted(async () => {
  // 确保页面从顶部开始（延迟执行以覆盖路由滚动行为）
  setTimeout(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }, 0);

  try {
    const res = await publicApi.render([]);
    modules.value = res.data.modules || [];
    // 读取站点配置（新结构：page 合并了 hero）
    const page = res.data.page || {};
    const hero = res.data.hero || {};
    siteConfig.value = {
      title: page.title || hero.title || 'SiteHangar',
      brand_name: page.brand_name || hero.brand_name || '',
      subtitle: page.subtitle || hero.subtitle || '',
    };
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || '加载失败';
  } finally {
    loading.value = false;
  }

  // 启动文字解码动画（在 siteConfig 读取完成后）
  scrambleText(titleTarget.value, (val) => { decodedTitle.value = val; }, 300, 800);
  scrambleText(subtitleTarget.value, (val) => { decodedSubtitle.value = val; }, 1200, 1000);

  // 光标闪烁 - 标题完成后停止
  const titleDone = ref(false);
  const subtitleDone = ref(false);

  setTimeout(() => { titleDone.value = true; }, 300 + 800);
  setTimeout(() => { subtitleDone.value = true; }, 1200 + 1000);

  cursorInterval = setInterval(() => {
    if (titleDone.value && subtitleDone.value) {
      showCursor.value = false;
      if (cursorInterval) clearInterval(cursorInterval);
    } else {
      showCursor.value = !showCursor.value;
    }
  }, 530);

  // 生成浮动粒子系统（持续循环：生成→上升→消失→补充）
  const maxParticles = 50;
  const spawnInterval = 100; // 每100ms尝试生成一个
  const particleLifeTime = 8000; // 8秒后生命周期结束，CSS动画控制上升

  function createParticle(): Particle {
    particleIdCounter++;
    const size = 1 + Math.random() * 4; // 1-5px，差异化大小
    const duration = 4 + Math.random() * 8; // 4-12s，上升速度差异化
    return {
      id: particleIdCounter,
      left: Math.random() * 100 + '%',
      top: (66 + Math.random() * 34) + '%', // 从页面下方1/3区域随机出现 (66-100%)
      duration: duration + 's',
      size: size + 'px',
      driftY: (-120 - Math.random() * 200) + 'px', // 向上移动距离
      driftX: (-20 + Math.random() * 40) + 'px',  // 左右漂移
    };
  }

  function spawnParticle() {
    if (floatingParticles.value.length < maxParticles) {
      floatingParticles.value.push(createParticle());
    }
    // 不管是否生成成功，都继续定时器，保持循环
    spawnTimer = setTimeout(spawnParticle, spawnInterval);
  }

  // 清理过期的粒子（生命周期结束）
  function cleanupParticles() {
    const now = Date.now();
    // 使用birthTime来跟踪，但更简单的方式：粒子出生8秒后移除
    // 这里我们直接检查每个粒子的"年龄"
    floatingParticles.value = floatingParticles.value.filter((p: Particle & { birthTime?: number }) => {
      if (!p.birthTime) {
        p.birthTime = now;
        return true;
      }
      return now - p.birthTime < particleLifeTime;
    });
  }

  // 启动生成和清理循环
  spawnParticle();
  cleanupTimer = setInterval(cleanupParticles, 500); // 每500ms清理一次
});

const hasModules = computed(() => modules.value.length > 0);
</script>

<template>
  <div class="home-view">
    <!-- 全局背景层（覆盖整个页面） -->
    <div class="global-bg-layer">
      <div class="global-bg-gradient"></div>
      <div class="global-bg-noise"></div>
    </div>

    <!-- 全局浮动粒子（覆盖整个页面） -->
    <div class="floating-particles">
      <div
        v-for="p in floatingParticles"
        :key="p.id"
        class="particle"
        :style="{
          left: p.left,
          top: p.top,
          animationDuration: p.duration,
          width: p.size,
          height: p.size,
          '--drift-x': p.driftX,
          '--drift-y': p.driftY,
        }"
      ></div>
    </div>

    <!-- ===== Hero Section ===== -->
    <section class="hero-enhanced">
      <!-- Hero 内容 -->
      <div class="hero-content-enhanced">
        <div class="brand-tag" v-if="brandName">&lt; {{ brandName }} /&gt;</div>
        <h1 class="hero-title-enhanced">
          <span class="decode-text">{{ decodedTitle }}</span>
        </h1>
        <p class="hero-subtitle-enhanced">
          <span class="decode-text">{{ decodedSubtitle }}</span>
        </p>
        <div class="hero-cta">
          <button class="cta-btn-primary" @click="scrollToModules">立即探索</button>
        </div>
      </div>

      <!-- 滚动指示器 -->
      <div class="scroll-indicator">
        <div class="mouse"></div>
        <span>SCROLL</span>
      </div>
    </section>

    <!-- ===== 栏目卡片 Section ===== -->
    <section ref="modulesSectionRef" class="modules-section">
      <div v-if="loading" class="loading-state">加载中…</div>
      <div v-else-if="error" class="error-state">{{ error }}</div>
      <div
        v-else-if="hasModules"
        ref="containerRef"
        class="home-modules-grid-enhanced"
        :class="{ 'is-four-modules': modules.length === 4 }"
        @mousemove="handleContainerMouseMove"
      >
        <router-link
          v-for="(m, idx) in modules"
          :key="m.id"
          :to="m.link"
          class="home-module-card-enhanced"
          :ref="(el) => setCardRef(el, m.id)"
          @mousemove="(e) => handleCardMouseMove(e, m.id)"
        >
          <!-- 卡片背景图片 -->
          <div class="card-bg" v-if="m.image">
            <img
              :src="m.image"
              :alt="m.title"
              class="card-bg-img"
              loading="lazy"
            />
            <div class="card-bg-overlay"></div>
          </div>

          <!-- 光晕效果 -->
          <div class="card-glow"></div>

          <div class="card-content">
            <h3 class="card-title">{{ m.title }}</h3>
            <p class="card-desc">{{ m.description }}</p>
            <div class="card-arrow">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </div>
          </div>
        </router-link>
      </div>
      <div v-else class="empty-state">暂无栏目</div>
    </section>
  </div>
</template>

<style src="@/styles/home-view.css"></style>
