<script setup lang="ts">
const props = defineProps<{ message: string }>();
</script>

<template>
  <div class="content card p-8 text-center" style="color: #ef5350;">
    {{ message }}
  </div>
</template>
