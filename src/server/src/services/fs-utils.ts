import fs from 'fs/promises';
import path from 'path';
import yaml from 'js-yaml';

/**
 * 读取 JSON 文件
 */
export async function readJsonFile<T = any>(filePath: string): Promise<T | null> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(content);
  } catch (err: any) {
    if (err.code === 'ENOENT') return null;
    throw new Error(`读取文件失败: ${filePath} - ${err.message}`);
  }
}

/**
 * 读取 YAML 文件
 */
export async function readYamlFile<T = any>(filePath: string): Promise<T | null> {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return yaml.load(content) as T;
  } catch (err: any) {
    if (err.code === 'ENOENT') return null;
    throw new Error(`读取文件失败: ${filePath} - ${err.message}`);
  }
}

/**
 * 读取 meta 文件（优先 meta.yaml，回退 meta.json）
 */
export async function readMetaFile<T = any>(dirPath: string): Promise<T | null> {
  const yamlPath = path.join(dirPath, 'meta.yaml');
  const jsonPath = path.join(dirPath, 'meta.json');
  
  // 优先读取 meta.yaml
  const yamlData = await readYamlFile<T>(yamlPath);
  if (yamlData !== null) return yamlData;
  
  // 回退到 meta.json
  return readJsonFile<T>(jsonPath);
}

/**
 * 写入 JSON 文件（原子写入：先写临时文件再重命名）
 */
export async function writeJsonFile(filePath: string, data: any): Promise<void> {
  const dir = path.dirname(filePath);
  await fs.mkdir(dir, { recursive: true });
  const tmpPath = `${filePath}.tmp`;
  await fs.writeFile(tmpPath, JSON.stringify(data, null, 2), 'utf-8');
  await fs.rename(tmpPath, filePath);
}

/**
 * 删除文件或目录
 */
export async function removePath(filePath: string): Promise<void> {
  try {
    await fs.rm(filePath, { recursive: true, force: true });
  } catch (err: any) {
    if (err.code !== 'ENOENT') throw err;
  }
}

/**
 * 列出目录下的子目录（按字母顺序排序）
 */
export async function listDirs(dirPath: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    return entries
      .filter(e => e.isDirectory())
      .map(e => e.name)
      .sort((a, b) => a.localeCompare(b, 'zh-CN'));
  } catch (err: any) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}

/**
 * 列出目录下的文件
 */
export async function listFiles(dirPath: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    return entries.filter(e => e.isFile()).map(e => e.name);
  } catch (err: any) {
    if (err.code === 'ENOENT') return [];
    throw err;
  }
}
