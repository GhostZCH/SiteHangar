<script setup lang="ts">
export interface NavItem {
  id: string;
  title: string;
  subtitle?: string;
  short: string;
  active: boolean;
  to?: string;
}

const props = defineProps<{
  title: string;
  items: NavItem[];
  expanded?: boolean;
}>();

const emit = defineEmits<{
  click: [id: string];
  action: [];
}>();

function handleClick(item: NavItem) {
  if (!item.to) {
    emit('click', item.id);
  }
}

function truncateTitle(title: string, maxLen: number): string {
  if (title.length <= maxLen) return title;
  return title.slice(0, maxLen) + '...';
}
</script>

<template>
  <nav class="nav-list" :aria-label="title">
    <div class="nav-list-items">
      <component
        :is="item.to ? 'router-link' : 'a'"
        v-for="item in items"
        :key="item.id"
        :to="item.to"
        class="nav-list-item"
        :class="{ active: item.active }"
        @click.prevent="handleClick(item)"
      >
        <span v-if="!props.expanded" class="nav-list-short">{{ item.short }}</span>
        <span v-if="props.expanded" class="nav-list-text">
          <span class="nav-list-title">{{ truncateTitle(item.title, 6) }}</span>
          <span v-if="item.subtitle" class="nav-list-subtitle">{{ item.subtitle }}</span>
        </span>
      </component>
      <button class="nav-list-item nav-list-action" @click.prevent="emit('action')">
        <span class="nav-list-short">
          <slot name="action-short" />
        </span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.nav-list {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.nav-list-items {
  display: flex;
  flex-direction: column;
  padding: 0 8px;
  gap: 2px;
}

.nav-list-item {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 10px 0;
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--on-surface-variant);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 0;
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
}

.nav-list-item:hover {
  background: var(--surface-variant);
  color: var(--primary);
}

.nav-list-item.active {
  background: var(--primary-container);
  color: var(--on-primary-container);
  font-weight: 500;
}

.nav-list-short {
  font-size: 14px;
  font-weight: 500;
  width: 44px;
  text-align: left;
  padding-left: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.nav-list-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.nav-list-title {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.nav-list-subtitle {
  font-size: 12px;
  color: var(--on-surface-variant);
  opacity: 0.7;
  line-height: 1.4;
}

.nav-list-action {
  color: var(--on-surface-variant);
}

.nav-list-action:hover {
  color: var(--primary);
}

.nav-list-action-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>
