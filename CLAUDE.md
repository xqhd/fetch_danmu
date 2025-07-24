# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python FastAPI service that aggregates danmu (弹幕/bullet comments) from multiple Chinese video platforms including Bilibili, iQiyi, Tencent Video, Youku, Mango TV, and Sohu. The service provides both direct URL-based danmu retrieval and Douban ID-based search functionality.

## Development Commands

**Run the development server:**
```bash
python main.py
```
This starts the FastAPI server with hot reload on `http://0.0.0.0:8000`

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

### Core Components

**main.py** - FastAPI application entry point with three main endpoints:
- `/danmu/by_douban_id` - Get danmu by Douban movie/TV ID
- `/danmu/by_title` - Search by title and get danmu  
- `/danmu/by_url` - Direct URL danmu extraction
- `/health` - Health check endpoint

**DanmuService class** - Central service orchestrating parallel danmu retrieval across platforms with async/await pattern

**lib/ directory** - Platform-specific extractors:
- `bilibili.py` - Bilibili danmu extraction with protobuf parsing
- `iqiyi.py` - iQiyi danmu extraction with protobuf parsing
- `tencent.py` - Tencent Video danmu extraction
- `youku.py` - Youku danmu extraction  
- `mgtv.py` - Mango TV danmu extraction
- `souhu.py` - Sohu Video danmu extraction
- `doubai_search.py` - Douban integration for platform URL discovery
- `utils.py` - URL parsing and protocol conversion utilities

### Data Models

**DanmuItem** - Standardized danmu structure:
- `text`: Comment content
- `time`: Timestamp in seconds
- `color`: Text color (default: #FFFFFF)
- `mode`: Display mode (0-2)
- `style`: Additional styling
- `border`: Border flag

**ApiResponse/ErrorResponse** - Unified API response format

### Key Patterns

- **Async/parallel processing**: All platform extractors run concurrently using `asyncio.gather()`
- **Exception resilience**: Individual platform failures don't break the entire request
- **Protocol buffers**: Bilibili and iQiyi use protobuf-generated parsers (`*_pb2.py` files)
- **URL normalization**: Custom protocol handling for platform-specific URLs via `utils.other2http()`
- **Douban integration**: Title search → Douban ID → platform URLs → danmu aggregation

### Error Handling

- HTTP exception handlers with standardized error responses
- Platform-specific failures are logged but don't interrupt aggregation
- 404 responses for missing Douban data or platform links
- 500 responses for server errors with detailed messages