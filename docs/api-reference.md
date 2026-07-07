# API 接口文档

## 公开 API（无需认证）

### 渲染接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/render/*path` | GET | 通配渲染：首页 / 详情页 / 分类页 / info 页 |

### 站点与栏目接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/sites/:siteSlug/columns` | GET | 列出某站点的所有栏目 |
| `/api/sites/:siteSlug/columns/:columnSlug/pages` | GET | 列出某栏目下的所有页面 |

### 配置接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/config` | GET | 读取网站公开配置 |

## 路由挂载方式

```typescript
// app.ts
app.use('/api', publicRoutes);

// public.routes.ts
router.use(renderRoutes);   // /render/*path
router.use(moduleRoutes);   // /sites/:siteSlug/columns
```

## 响应格式

所有 API 返回统一的 JSON 格式：

```json
{
  "success": true,
  "data": { ... }
}
```

错误时返回：

```json
{
  "success": false,
  "error": "错误信息"
}
```
