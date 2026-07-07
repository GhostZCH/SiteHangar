import { ref, onMounted, onBeforeUnmount } from 'vue';

export function useMobileBarAutoHide() {
  const barsVisible = ref(true);
  let lastScrollY = 0;
  let lastScrollTime = 0;
  let scrollSpeed = 0;
  let hideTimer: ReturnType<typeof setTimeout> | null = null;
  let isScrolling = false;

  const SPEED_THRESHOLD = 80; // px/s，超过此速度视为快速滚动
  const HIDE_DELAY = 1500; // ms，停留后自动隐藏
  const CHECK_INTERVAL = 150; // ms，检测滚动速度的间隔

  function showBars() {
    barsVisible.value = true;
    if (hideTimer) {
      clearTimeout(hideTimer);
      hideTimer = null;
    }
  }

  function scheduleHide() {
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      barsVisible.value = false;
    }, HIDE_DELAY);
  }

  function onScroll() {
    const now = Date.now();
    const currentY = window.scrollY;
    const deltaY = currentY - lastScrollY;
    const deltaTime = now - lastScrollTime;

    if (deltaTime > 0) {
      scrollSpeed = Math.abs(deltaY) / (deltaTime / 1000);
    }

    lastScrollY = currentY;
    lastScrollTime = now;

    if (!isScrolling) {
      isScrolling = true;
      // 滚动开始时显示边栏
      showBars();
    }
  }

  function checkScrollState() {
    const now = Date.now();
    const timeSinceLastScroll = now - lastScrollTime;

    if (timeSinceLastScroll > CHECK_INTERVAL && isScrolling) {
      // 滚动已停止
      isScrolling = false;

      if (scrollSpeed > SPEED_THRESHOLD) {
        // 快速滚动停止后，保持显示一段时间再隐藏
        scheduleHide();
      } else {
        // 慢速滚动或停留，立即隐藏
        barsVisible.value = false;
      }
    }

    scrollSpeed = scrollSpeed * 0.8; // 速度衰减
  }

  function onClick() {
    showBars();
    scheduleHide();
  }

  let scrollInterval: ReturnType<typeof setInterval> | null = null;

  onMounted(() => {
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('click', onClick, { passive: true });
    window.addEventListener('touchstart', onClick, { passive: true });
    lastScrollY = window.scrollY;
    lastScrollTime = Date.now();
    scrollInterval = setInterval(checkScrollState, CHECK_INTERVAL);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', onScroll);
    window.removeEventListener('click', onClick);
    window.removeEventListener('touchstart', onClick);
    if (scrollInterval) clearInterval(scrollInterval);
    if (hideTimer) clearTimeout(hideTimer);
  });

  return { barsVisible };
}
