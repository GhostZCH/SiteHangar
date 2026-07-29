import { ref, watch, onMounted, onBeforeUnmount, type Ref } from 'vue';
import { useRoute } from 'vue-router';

export interface PageSection {
  id: string;
  title: string;
  subtitle?: string;
}

export function usePageSections(sections?: Ref<PageSection[]>) {
  const route = useRoute();
  const pageSections = ref<PageSection[]>([]);
  const activeSectionId = ref('');
  let observer: IntersectionObserver | null = null;

  function scrollToSection(id: string) {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function setupObserver() {
    if (observer) observer.disconnect();

    const sectionEls = document.querySelectorAll('.section[id]');
    if (!sectionEls.length) return;

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            activeSectionId.value = entry.target.id;
          }
        });
      },
      { rootMargin: '-80px 0px -60% 0px', threshold: 0 }
    );

    sectionEls.forEach((el) => observer!.observe(el));
  }

  function extractFromDom() {
    setTimeout(() => {
      const sectionEls = document.querySelectorAll('.section[id]');
      pageSections.value = Array.from(sectionEls).map((el) => {
        const id = el.id;
        const header = el.querySelector('.section-title');
        const title = header?.textContent?.trim() || id;
        const subtitle = el.getAttribute('data-subtitle') || undefined;
        return { id, title, subtitle };
      });
      setupObserver();
    }, 300);
  }

  function updateSections() {
    if (route.name !== 'detail') {
      pageSections.value = [];
      activeSectionId.value = '';
      if (observer) {
        observer.disconnect();
        observer = null;
      }
      return;
    }

    const source = sections?.value;
    if (source && source.length) {
      pageSections.value = source.map((s) => ({
        id: s.id,
        title: s.title,
        subtitle: s.subtitle,
      }));
      setupObserver();
      return;
    }

    extractFromDom();
  }

  watch(() => route.path, updateSections, { immediate: true });
  if (sections) {
    watch(sections, updateSections, { immediate: false });
  }
  onMounted(updateSections);
  onBeforeUnmount(() => {
    if (observer) observer.disconnect();
  });

  return { pageSections, activeSectionId, scrollToSection };
}
