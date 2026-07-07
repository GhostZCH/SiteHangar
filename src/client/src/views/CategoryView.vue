<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { publicApi } from '@/api/public';
import type { RenderResponse } from '@/types/content';
import PageLoading from '@/components/content/PageLoading.vue';
import PageError from '@/components/content/PageError.vue';

const route = useRoute();
const data = ref<RenderResponse | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const activeTab = ref(0);

async function load() {
  loading.value = true;
  error.value = null;
  activeTab.value = 0;
  try {
    data.value = await publicApi.render([route.params.moduleSlug as string]);
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || '加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => route.params.moduleSlug, load);
</script>

<template>
  <div class="category-page">
    <div class="category-page-inner">
      <PageLoading v-if="loading" />
      <PageError v-else-if="error" :message="error" />
      <div v-else-if="data">
        <header class="mb-8 pb-6" style="border-bottom: 1px solid var(--outline-variant);">
          <h1 class="hero-title" style="font-size: 36px;">
            {{ data.data.page?.title || data.column?.name }}
          </h1>
          <div v-if="data.data.page?.tags?.length" class="mt-3 flex flex-wrap gap-2">
            <span v-for="(t, i) in data.data.page.tags" :key="i" class="hero-tag">{{ t }}</span>
          </div>
        </header>

        <!-- 最近更新 -->
        <section v-if="data.data.recent?.length" class="cat-section">
          <h2 class="cat-section-title">最近更新</h2>
          <div class="cat-recent-grid">
            <router-link
              v-for="(r, i) in data.data.recent"
              :key="i"
              :to="r.link"
              class="cat-recent-card"
            >
              <div class="cat-recent-title">{{ r.title }}</div>
              <div v-if="r.subtitle" class="cat-recent-desc">{{ r.subtitle }}</div>
              <div v-if="r.desc" class="cat-recent-desc">{{ r.desc }}</div>
            </router-link>
          </div>
        </section>

        <!-- 分类列表 -->
        <section v-if="data.data.categories?.length">
          <h2 class="cat-section-title">分类索引</h2>
          <div class="cat-tabs">
            <button
              v-for="(cat, i) in data.data.categories"
              :key="i"
              class="cat-tab"
              :class="{ active: activeTab === i }"
              @click="activeTab = i"
            >
              {{ cat.name }}
            </button>
          </div>

          <div
            v-for="(cat, i) in data.data.categories"
            :key="i"
            class="cat-panel"
            :class="{ active: activeTab === i }"
          >
            <!-- 有 subCategories 的分类（如 wiki） -->
            <div v-if="cat.subCategories?.length" class="cat-sub-grid">
              <div v-for="(sub, j) in cat.subCategories" :key="j" class="cat-sub-card">
                <h3 class="cat-sub-title">{{ sub.name }}</h3>
                <ul class="cat-link-list">
                  <li v-for="(l, k) in sub.links" :key="k">
                    <router-link :to="l.url" class="cat-link-item">{{ l.title }}</router-link>
                  </li>
                </ul>
              </div>
            </div>
            <!-- 只有 links 的分类（如 tools） -->
            <div v-else-if="cat.links?.length" class="cat-link-only">
              <ul class="cat-link-list">
                <li v-for="(l, k) in cat.links" :key="k">
                  <router-link :to="l.url" class="cat-link-item">{{ l.title }}</router-link>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
