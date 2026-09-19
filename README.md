# 13-metrofare（地铁票价）

Metrofare — 站间最短站数 + 分段票价表

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4200 |
| API | http://localhost:9200 |

## 主链

选起终点站 → 按站数/里程规则算票价 → 出示票价卡

## 点对点一口价

在分段表之外，可为一对**有向**起终点登记一口价：

| 接口 | 说明 |
| --- | --- |
| `GET /api/flat-fares` | 列出全部一口价对 |
| `POST /api/flat-fares` | 登记 `{start, end, price}`；同一对重复登记返回 409 |
| `DELETE /api/flat-fares/{id}` | 删除后该 OD 回到分段表 |

询价 `POST /api/quote` 命中一口价时 `fare` 为一口价、`via_flat=true`，
并仍返回最短途经站 `path`、站数 `hops` 与分段参考价 `segment_fare`；
未命中则纯按站数套分段表。`persist=false` 为只读试算，不落库；
已落库记录保留当时应付，删除一口价不改写。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
