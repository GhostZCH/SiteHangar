interface CacheEntry<T> {
  value: T;
  expiry: number;
}

const cache = new Map<string, CacheEntry<any>>();
const MAX_SIZE = 1000;
const DEFAULT_TTL_MS = 5 * 60 * 1000;

export function cacheKey(siteSlug: string, type: string, pagePath?: string): string {
  return pagePath ? `${siteSlug}:${type}:${pagePath}` : `${siteSlug}:${type}`;
}

function evictIfNeeded(): void {
  if (cache.size <= MAX_SIZE) return;
  const entries = Array.from(cache.entries());
  const toDelete = Math.ceil(MAX_SIZE * 0.2);
  for (let i = 0; i < toDelete; i++) {
    cache.delete(entries[i][0]);
  }
}

export function getCached<T>(key: string): T | undefined {
  const entry = cache.get(key);
  if (!entry) return undefined;
  if (Date.now() > entry.expiry) {
    cache.delete(key);
    return undefined;
  }
  return entry.value;
}

export function setCached<T>(key: string, value: T, ttlMs: number = DEFAULT_TTL_MS): void {
  evictIfNeeded();
  cache.set(key, { value, expiry: Date.now() + ttlMs });
}

export function clearCached(prefix: string): void {
  for (const key of cache.keys()) {
    if (key.startsWith(prefix)) cache.delete(key);
  }
}

export function clearAllCached(): void {
  cache.clear();
}
