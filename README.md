# 弹幕获取 API (Danmu Fetch API)

一个基于 FastAPI 的异步弹幕聚合服务，支持从多个主流视频平台获取弹幕数据，具体支持的平台请看`lib`文件目录，返回用于[weizhenye/Danmaku](https://github.com/weizhenye/Danmaku)的弹幕数据。

## 功能特性

- 🚀 **异步并行处理**: 使用 asyncio 并行获取多平台弹幕，提高响应速度
- 🔍 **多种获取方式**: 支持豆瓣 ID、标题搜索和直接 URL 三种弹幕获取方式
- 🎯 **平台聚合**: 一次请求获取所有支持平台的弹幕数据
- 📊 **标准化输出**: 统一的弹幕数据格式，便于后续处理
- 🛡️ **异常容错**: 单个平台失败不影响其他平台数据获取
- 📖 **完整文档**: 内置 Swagger UI 和 ReDoc 文档

## 快速开始

### 环境要求

- Python 3.13
- 依赖包详见 `requirements.txt`

### 安装与运行

1. **克隆仓库**

   ```bash
   git clone https://github.com/panxiaoguang/fetch_danmu.git
   cd fetch_danmu
   ```

2. **安装依赖**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   fastapi dev
   ```

服务将在 `http://0.0.0.0:8000` 启动，支持热重载。

### API 文档

启动服务后，可通过以下地址访问 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API 接口

### 1. 通过豆瓣 ID 获取弹幕

```
GET /danmu/by_douban_id
```

**参数:**

- `douban_id` (必需): 豆瓣电影/剧集 ID
- `episode_number` (可选): 指定集数

**示例:**

```bash
curl "http://localhost:8000/danmu/by_douban_id?douban_id=123456&episode_number=1"
```

### 2. 通过标题搜索获取弹幕

```
GET /danmu/by_title
```

**参数:**

- `title` (必需): 视频标题
- `season_number` (可选): 季数，默认为 1
- `episode_number` (可选): 集数

**示例:**

```bash
curl "http://localhost:8000/danmu/by_title?title=电视剧名称&season_number=1&episode_number=1"
```

### 3. 通过 URL 直接获取弹幕

```
GET /danmu/by_url
```

**参数:**

- `url` (必需): 视频页面 URL

**示例:**

```bash
curl "http://localhost:8000/danmu/by_url?url=https://www.bilibili.com/video/BV1234567890"
```

### 4. 健康检查

```
GET /health
```

**示例:**

```bash
curl "http://localhost:8000/health"
```

## 响应格式

### 成功响应

```json
{
  "code": 0,
  "msg": null,
  "data": [
    {
      "text": "弹幕内容",
      "time": 123.45,
      "color": "#FFFFFF",
      "mode": 0,
      "style": {},
      "border": false
    }
  ]
}
```

### 错误响应

```json
{
  "code": -1,
  "msg": "错误信息"
}
```

## 数据模型

### DanmuItem (弹幕项)

**弹幕的返回格式是按照弹幕库的格式匹配的**

| 字段   | 类型    | 描述          | 默认值  |
| ------ | ------- | ------------- | ------- |
| text   | string  | 弹幕内容      | -       |
| time   | float   | 弹幕时间(秒)  | -       |
| color  | string  | 弹幕颜色      | #FFFFFF |
| mode   | int     | 弹幕模式(0-2) | 0       |
| style  | object  | 弹幕样式      | {}      |
| border | boolean | 是否有边框    | false   |

## 核心组件

### DanmuService

中央服务类，负责：

- 并行调用各平台弹幕提取器
- 异常处理和容错
- 数据聚合和标准化

### 平台提取器

每个平台都有独立的提取器模块：

- 处理平台特定的 URL 格式
- 解析平台 API 响应
- 统一数据格式输出

## 开发指南

### 添加新平台支持

1. 在 `lib/` 目录创建新的平台提取器
2. 实现 `get_*_danmu(url)` 函数
3. 在 `DanmuService` 中添加对应的任务
4. 更新文档

## 错误处理

- HTTP 404: 未找到对应的视频链接或豆瓣信息
- HTTP 500: 服务器内部错误
- 平台级错误: 不会中断整体请求，只影响该平台数据

## 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 贡献

所有弹幕获取和豆瓣搜索的代码都是从[thshu/fnos-tv](https://github.com/thshu/fnos-tv)仓库中 1:1 复制的，感谢作者的贡献。
本仓库由于使用了 fastapi, 所以将原本所有的同步代码全部修改为异步类型。
同时本仓库将弹幕接口解耦，并适配了[weizhenye/Danmaku](https://github.com/weizhenye/Danmaku)的格式。

## 注意事项

- 本项目仅用于学习和研究目的
- 请遵守相关平台的使用条款
- 弹幕数据版权归原平台所有
