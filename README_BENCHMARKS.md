# ipools 基准测试指南

本文档介绍如何使用 pytest-benchmark 对 ipools 库进行性能测试。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements-dev.txt
# 或者
pip install pytest pytest-benchmark
```

### 2. 运行普通测试

```bash
# 运行所有测试（不包括基准测试）
pytest

# 运行特定测试文件
pytest tests/test_ippool.py

# 运行特定测试
pytest tests/test_ippool.py::test_ipv4_pool_init
```

### 3. 运行基准测试

```bash
# 运行所有基准测试
pytest tests/test_benchmarks.py --benchmark-only

# 运行特定测试
pytest tests/test_benchmarks.py::TestIPv4PoolBenchmarks::test_add_single_network --benchmark-only

# 使用脚本运行
python scripts/run_benchmarks.py

# 使用Makefile (Linux/Mac)
make benchmark
```

## 测试覆盖范围

### IPv4Pool 基准测试

- **添加操作**: 单个网络、多个网络、重叠网络
- **移除操作**: 单个网络、多个网络、重叠网络
- **交集操作**: 小型、中型、大型池
- **包含检查**: 单个IP、网络、多个IP
- **属性访问**: networks、ip_ranges
- **复制操作**: 不同大小的池

### IPv6Pool 基准测试

- **添加操作**: 单个和多个IPv6网络
- **交集操作**: 中型IPv6池
- **包含检查**: IPv6地址
- **范围获取**: IPv6范围

### 边界情况测试

- **空池操作**: 空池的各种操作
- **单个IP池**: 最小规模测试
- **大型网络池**: 最大规模测试
- **碎片化池**: 高度碎片化的网络池
- **相邻网络**: 需要合并的网络

### 内存使用测试

- **大型池创建**: 内存使用情况
- **序列化性能**: str() 和 repr() 性能

## 配置选项

### pytest.ini 配置

```ini
[tool:pytest]
addopts = 
    --strict-markers
    --strict-config
markers =
    benchmark: marks tests as benchmark tests
```

**注意**: 基准测试配置已从默认配置中移除，需要手动指定参数运行基准测试。

### 命令行选项

- `--benchmark-only`: 只运行基准测试
- `--benchmark-min-rounds=5`: 最小运行轮数
- `--benchmark-warmup=on`: 启用预热
- `--benchmark-disable-gc`: 禁用垃圾回收
- `--benchmark-sort=name`: 按名称排序
- `--benchmark-save=name`: 保存结果
- `--benchmark-compare=file`: 与基线比较

## 使用脚本

### 基本用法

```bash
# 运行所有基准测试
python scripts/run_benchmarks.py

# 保存基线
python scripts/run_benchmarks.py --save-baseline

# 与基线比较
python scripts/run_benchmarks.py --compare

# 过滤测试
python scripts/run_benchmarks.py --filter ipv4
python scripts/run_benchmarks.py --filter add
```

### 脚本选项

- `--compare`: 与基线比较
- `--save-baseline`: 保存当前结果为基线
- `--filter`: 过滤测试（如：ipv4, ipv6, add, remove等）
- `--output`: 输出文件名
- `--rounds`: 最小运行轮数
- `--warmup`: 启用预热

## 结果解读

### 输出示例

```
Name (time in ms)         Min     Max    Mean    StdDev  Median    IQR    Outliers  OPS  Rounds  Iterations
----------------------------------------------------------------------------------------------------------
test_add_single_network   0.001   0.002   0.001   0.000   0.001   0.000      0;0  1000.0      10           1
test_add_multiple_networks 0.050   0.060   0.055   0.003   0.055   0.005      0;0    18.2      10           1
```

### 关键指标

- **Min/Max**: 最小/最大执行时间
- **Mean**: 平均执行时间
- **StdDev**: 标准差
- **OPS**: 每秒操作数
- **Rounds**: 运行轮数
- **Iterations**: 每轮迭代数

## CI/CD 集成

### GitHub Actions

项目包含 `.github/workflows/benchmark.yml` 工作流，会：

1. 在每次推送和PR时运行基准测试
2. 每周自动运行基准测试
3. 保存基准测试结果作为工件
4. 与基线比较并在性能下降时失败

### 基线管理

```bash
# 创建基线
pytest tests/test_benchmarks.py --benchmark-only --benchmark-save=baseline

# 与基线比较
pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare=.benchmarks/baseline.json

# 设置性能下降阈值
pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare=.benchmarks/baseline.json --benchmark-compare-fail=mean:10%
```

## 性能优化建议

### 测试设计

1. **测试数据规模**: 包含小、中、大三种规模
2. **边界情况**: 测试空池、单个IP等极端情况
3. **操作类型**: 覆盖所有主要操作
4. **数据模式**: 包含重叠、相邻、碎片化等不同模式

### 结果分析

1. **趋势分析**: 关注性能变化趋势
2. **异常检测**: 识别性能异常点
3. **回归测试**: 确保新功能不引入性能回归
4. **基准比较**: 与历史基线比较

## 故障排除

### 常见问题

1. **测试失败**: 检查依赖是否正确安装
2. **结果不稳定**: 增加运行轮数或禁用GC
3. **内存不足**: 减少测试数据规模
4. **基线比较失败**: 检查基线文件是否存在

### 调试技巧

```bash
# 详细输出
pytest tests/test_benchmarks.py --benchmark-only -v

# 调试模式
pytest tests/test_benchmarks.py --benchmark-only --pdb

# 只运行一个测试
pytest tests/test_benchmarks.py::TestIPv4PoolBenchmarks::test_add_single_network --benchmark-only
```

## 贡献指南

### 添加新测试

1. 在 `tests/test_benchmarks.py` 中添加新的测试方法
2. 使用 `@pytest.mark.benchmark` 标记
3. 包含适当的文档字符串
4. 确保测试覆盖不同的数据规模

### 测试命名规范

- 测试方法名应清晰描述测试内容
- 使用 `test_` 前缀
- 包含操作类型和数据规模信息

### 性能基准

- 定期更新性能基准
- 记录性能变化原因
- 在README中更新性能数据 