.PHONY: help install test benchmark benchmark-save benchmark-compare clean

# 默认目标
help:
	@echo "可用的命令:"
	@echo "  install          - 安装开发依赖"
	@echo "  test             - 运行单元测试"
	@echo "  benchmark        - 运行基准测试"
	@echo "  benchmark-save   - 运行基准测试并保存结果"
	@echo "  benchmark-compare - 运行基准测试并与基线比较"
	@echo "  clean            - 清理缓存文件"

# 安装开发依赖
install:
	pip install -r requirements-dev.txt
	pip install -e .

# 运行单元测试
test:
	pytest tests/ -v --tb=short

# 运行基准测试
benchmark:
	pytest tests/test_benchmarks.py --benchmark-only --benchmark-min-rounds=5 --benchmark-warmup=on --benchmark-disable-gc --benchmark-sort=name --benchmark-columns=min,max,mean,stddev,rounds,iterations

# 运行基准测试并保存结果
benchmark-save:
	pytest tests/test_benchmarks.py --benchmark-only --benchmark-save=benchmark-results --benchmark-save-data --benchmark-min-rounds=5 --benchmark-warmup=on --benchmark-disable-gc

# 运行基准测试并与基线比较
benchmark-compare:
	pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare=.benchmarks/baseline.json --benchmark-compare-fail=mean:10% --benchmark-min-rounds=5 --benchmark-warmup=on --benchmark-disable-gc

# 运行特定基准测试
benchmark-ipv4:
	pytest tests/test_benchmarks.py::TestIPv4PoolBenchmarks --benchmark-only --benchmark-min-rounds=5 --benchmark-warmup=on --benchmark-disable-gc

benchmark-ipv6:
	pytest tests/test_benchmarks.py::TestIPv6PoolBenchmarks --benchmark-only --benchmark-min-rounds=5 --benchmark-warmup=on --benchmark-disable-gc

benchmark-edge:
	pytest tests/test_benchmarks.py::TestEdgeCaseBenchmarks --benchmark-only --benchmark-min-rounds=5 --benchmark-warmup=on --benchmark-disable-gc

# 使用脚本运行基准测试
benchmark-script:
	python scripts/run_benchmarks.py

benchmark-script-save:
	python scripts/run_benchmarks.py --save-baseline

benchmark-script-compare:
	python scripts/run_benchmarks.py --compare

# 清理缓存文件
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".benchmarks" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

# 格式化代码
format:
	black ippool/ tests/ scripts/
	flake8 ippool/ tests/ scripts/

# 类型检查
typecheck:
	mypy ippool/

# 完整检查
check: format typecheck test
	@echo "✅ 所有检查通过!"

# 性能分析
profile:
	python -m cProfile -o profile.stats scripts/run_benchmarks.py
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)" 