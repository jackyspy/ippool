# ippool 开发指南

## 🚀 快速开始

### 环境设置
```bash
# 克隆项目
git clone https://github.com/jackyspy/ippool.git
cd ippool

# 安装开发依赖
pip install -r requirements-dev.txt

# 以可编辑模式安装项目（重要！）
pip install -e .
```

**注意**: `pip install -e .` 是必需的步骤，它会以可编辑模式安装当前项目，确保：
- pytest 能够正确找到项目的模块
- 代码修改后无需重新安装即可生效
- 导入测试时不会出现模块找不到的错误

**简化安装**: 也可以使用 Makefile 命令：
```bash
make install
```
```

### 运行测试

#### 普通测试（默认）
```bash
# 运行所有测试（不包括基准测试）
pytest

# 运行特定测试文件
pytest tests/test_ippool.py

# 运行特定测试
pytest tests/test_ippool.py::test_ipv4_pool_init
```

#### 基准测试（需要特殊参数）
```bash
# 运行所有基准测试
pytest tests/test_benchmarks.py --benchmark-only

# 运行特定基准测试
pytest tests/test_benchmarks.py::TestIPv4PoolBenchmarks::test_add_single_network --benchmark-only

# 使用脚本运行
python scripts/run_benchmarks.py

# 使用Makefile (Linux/Mac)
make benchmark

# 保存基准测试结果
make benchmark-save

# 与基线比较
make benchmark-compare
```
```

## 📋 常用命令

### 测试相关
```bash
# 运行所有测试
pytest

# 运行基准测试
pytest --benchmark-only

# 运行测试并生成覆盖率报告
pytest --cov=ippool

# 运行特定类型的测试
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
pytest -m benchmark     # 基准测试
```

### 基准测试相关
```bash
# 保存基准测试结果
pytest tests/test_benchmarks.py --benchmark-only --benchmark-save=baseline

# 与基线比较
pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare=.benchmarks/baseline.json

# 过滤基准测试
python scripts/run_benchmarks.py --filter ipv4
python scripts/run_benchmarks.py --filter add
```

### 代码质量
```bash
# 格式化代码
black ippool/ tests/

# 代码检查
flake8 ippool/ tests/

# 类型检查
mypy ippool/

# 使用Makefile进行完整检查
make check

# 清理缓存文件
make clean
```

## 🔧 配置说明

### pytest 配置
- **默认行为**: 只运行普通测试，不运行基准测试
- **运行基准测试**: 需要添加 `--benchmark-only` 参数
- **运行所有测试**: 使用 `--benchmark-enable` 参数

### 基准测试配置
基准测试的配置参数需要在命令行中指定：
- `--benchmark-min-rounds=5`: 最小运行轮数
- `--benchmark-warmup=on`: 启用预热
- `--benchmark-disable-gc`: 禁用垃圾回收
- `--benchmark-sort=name`: 按名称排序

## 📊 性能测试结果

基准测试会显示详细的性能指标：
- **Min/Max**: 最小/最大执行时间
- **Mean**: 平均执行时间
- **StdDev**: 标准差
- **OPS**: 每秒操作数
- **Rounds**: 运行轮数

## 🎯 最佳实践

1. **日常开发**: 使用 `pytest` 运行普通测试
2. **性能优化**: 使用 `pytest --benchmark-only` 运行基准测试
3. **CI/CD**: 分别运行普通测试和基准测试
4. **性能监控**: 定期保存和比较基准测试结果

## 📚 更多信息

- 详细基准测试指南: [README_BENCHMARKS.md](README_BENCHMARKS.md)
- 基准测试结果总结: [BENCHMARK_SUMMARY.md](BENCHMARK_SUMMARY.md)
- 项目主页: [README.md](README.md)
- 中文文档: [README_zh.md](README_zh.md)

## 🤝 贡献指南

如果你想为 ippool 项目做出贡献，请：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

在提交代码前，请确保：
- 所有测试通过 (`make test`)
- 代码格式正确 (`make format`)
- 类型检查通过 (`make typecheck`)
- 性能没有显著下降 (`make benchmark-compare`)

## 🔧 故障排除

### 常见问题

**Q: pytest 报错 "ModuleNotFoundError: No module named 'ippool'"**  
A: 确保运行了 `pip install -e .` 命令

**Q: 测试运行时找不到模块**  
A: 检查是否正确安装了项目，运行 `pip list | grep ippool` 确认

**Q: 代码修改后测试结果没有更新**  
A: 确保使用了 `pip install -e .` 安装，这样代码修改会自动生效

**Q: 基准测试运行失败**  
A: 确保安装了 pytest-benchmark: `pip install pytest-benchmark` 