<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue';

const props = defineProps<{ src: string; modelValue: boolean }>();
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>();

const scale = ref(1);
const zoomed = computed(() => scale.value > 1.05);

function close() {
  emit('update:modelValue', false);
  scale.value = 1;
}

function toggleZoom() {
  scale.value = zoomed.value ? 1 : 1.5;
}

function onKeydown(ev: KeyboardEvent) {
  if (ev.key === 'Escape') close();
}

function onWheel(ev: WheelEvent) {
  ev.preventDefault();
  const delta = ev.deltaY > 0 ? -0.1 : 0.1;
  scale.value = Math.min(Math.max(0.2, scale.value + delta), 4);
}

watch(() => props.modelValue, (open) => {
  if (open) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
    scale.value = 1;
  }
});

onMounted(() => document.addEventListener('keydown', onKeydown));
onUnmounted(() => document.removeEventListener('keydown', onKeydown));
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="image-lightbox-overlay"
        @click.self="close"
        @wheel="onWheel"
      >
        <button class="lightbox-close" aria-label="关闭" @click="close">×</button>
        <button class="lightbox-toggle" aria-label="放大/缩小" @click="toggleZoom">
          {{ zoomed ? '缩小' : '放大' }}
        </button>

        <img
          :src="src"
          alt=""
          class="lightbox-image"
          :class="{ zoomed }"
          :style="{ transform: `scale(${scale})` }"
          @click="toggleZoom"
          @dblclick="toggleZoom"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.image-lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  backdrop-filter: blur(4px);
}

.lightbox-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  transition: transform 0.25s ease;
  cursor: zoom-in;
  border-radius: 4px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.lightbox-image.zoomed {
  cursor: zoom-out;
  max-width: none;
  max-height: none;
}

.lightbox-close,
.lightbox-toggle {
  position: absolute;
  top: 16px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 1001;
  line-height: 1;
  padding: 0;
}

.lightbox-close:hover,
.lightbox-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
}

.lightbox-close {
  right: 16px;
  font-size: 28px;
}

.lightbox-toggle {
  right: 64px;
  font-size: 12px;
  width: auto;
  padding: 0 12px;
  border-radius: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 640px) {
  .image-lightbox-overlay {
    padding: 20px;
  }
  .lightbox-toggle {
    right: 60px;
    font-size: 11px;
    padding: 0 8px;
  }
}
</style>
