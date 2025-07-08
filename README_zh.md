[English](README.md) | [中文](README_zh.md)

# ipools

高效的 IPv4/IPv6 地址池管理与运算库

[![PyPI version](https://badge.fury.io/py/ipools.svg)](https://pypi.org/project/ipools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 简介

`ippool` 是一个用于高效管理、合并、查找和集合运算的 IPv4/IPv6 地址池的 Python 库。支持灵活的输入格式（CIDR、区间、字符串、对象），高性能的合并、交集、差集和包含判断，适用于网络自动化、安全、资源分配等场景。

---

## 主要特性

- 快速添加/移除/合并 IP 段与网段
- 同时支持 IPv4 和 IPv6
- 灵活输入：CIDR、区间字符串、元组、对象等
- 高效的交集、差集、包含等集合运算
- 支持输出为最简网络集合或原始区间
- Pythonic API，测试完善，生产可用
- 提供命令行工具，支持批量处理

---

## 安装

```bash
pip install ipools
```

---

## 快速上手（Python API）

```python
from ippool import IPv4Pool, IPv6Pool

# 创建池，支持CIDR和区间字符串
pool = IPv4Pool(["192.168.1.0/24", "10.0.0.1-10.0.0.10"])

# 添加更多网段
pool.add("172.16.0.0/16")

# 移除子网
pool.remove("192.168.1.128/25")

# 判断IP是否在池中
print("192.168.1.5" in pool)  # True
print("192.168.2.1" in pool)  # False

# 获取合并后的最简网络
print(pool.networks)  # (IPv4Network('10.0.0.1/32'), ..., IPv4Network('172.16.0.0/16'))

# 求交集
other = IPv4Pool("10.0.0.0/8")
print(pool & other)

# 集合运算示例
pool1 = IPv4Pool("192.168.1.0/24")
pool2 = IPv4Pool("192.168.1.128/25")
pool3 = IPv4Pool("192.168.2.0/24")

# 并集
union = pool1 + pool2 + pool3
print(f"并集包含 {union.num_addresses} 个IP地址")

# 差集
diff = pool1 - pool2
print(f"差集包含 {diff.num_addresses} 个IP地址")

# 交集
intersection = pool1 & pool2
print(f"交集包含 {intersection.num_addresses} 个IP地址")

# IPv6支持
ipv6_pool = IPv6Pool(["2001:db8::/48", "2001:db8:1::/48"])
print(f"IPv6池包含 {ipv6_pool.num_addresses} 个地址")

# 复杂操作示例
# 从大网段中排除多个小网段
large_network = IPv4Pool("10.0.0.0/8")
excluded_networks = [
    "10.0.1.0/24",
    "10.0.2.0/24", 
    "10.1.0.0/16"
]
result = large_network - excluded_networks
print(f"排除后剩余 {result.num_addresses} 个IP地址")

# 检查IP范围是否重叠
range1 = IPv4Pool("192.168.1.0/24")
range2 = IPv4Pool("192.168.1.128/25")
if range1 & range2:
    print("IP范围有重叠")

# 获取池的统计信息
print(f"池包含 {len(pool.networks)} 个网络")
print(f"池包含 {len(pool.ip_ranges)} 个IP范围")
print(f"总IP数量: {pool.num_addresses}")

# 从字符串批量创建
networks_str = """
192.168.1.0/24
10.0.0.0/8
172.16.0.0/16
"""
pool_from_str = IPv4Pool(networks_str)
print(f"从字符串创建了包含 {pool_from_str.num_addresses} 个IP的池")

# 复制和修改
pool_copy = pool.copy()
pool_copy.add("192.168.3.0/24")
print(f"原池: {pool.num_addresses} IPs, 副本: {pool_copy.num_addresses} IPs")
```

---

## 命令行用法

安装后可直接使用 `ippool` 命令：

### 基础操作

```bash
# 默认合并操作（无需指定命令）
ippool 192.168.1.0/24 192.168.2.0/24
ippool --format json "192.168.1.0/24;192.168.2.0/24" 192.168.3.0-127
ippool --format stat "192.168.1.0/24,10.0.0.0/8"
ippool --format=cidr -o output.json 192.168.1.0/24 192.168.1.100-192.168.1.200 192.168.2.0-100

# 差集操作（注意：全局选项必须在子命令之前）
ippool --format cidr diff "192.168.0.0/16" 192.168.1.0/24
# 从一个或多个大IP段，去掉多个小IP段
ippool --format cidr diff 192.168.0.0/16 "192.168.1.0/24;192.168.2.0-192.168.100.255,192.168.254.0-255"
# 从文件加载地址池
ippool --ipv6 diff @ippool1.txt @ippool2.txt

# 多个池的交集
ippool --format json intersect "192.168.1.0/24" "192.168.1.128/25" "192.168.1.192/26"
```

### 输入格式

```bash
# 直接输入，支持分隔符（逗号、分号）
ippool "192.168.1.0/24,10.0.0.0/8;172.16.0.0/16"

# 从文件读取
ippool @ranges.txt
ippool @"包含空格的路径/ranges.txt"

# 从标准输入读取
cat ranges.txt | ippool -

# 混合不同输入源
ippool @vpc1.txt "192.168.1.0/24" @vpc2.txt
```

### 输出格式

```bash
# 范围格式（默认）
ippool "192.168.1.0/24;192.168.2.0/24"
# 输出: 192.168.1.0-192.168.2.255

# CIDR格式
ippool --format=cidr 192.168.1.0/24,192.168.2.0/24
# 输出: 192.168.1.0/24
#       192.168.2.0/24

# 统计信息
ippool --format=stat "192.168.1.0/24"
# 输出: Networks: 1
#         Total IPs: 256
#         Largest: 192.168.1.0/24 (256 IPs)
#         Smallest: 192.168.1.0/24 (256 IPs)

# JSON格式
ippool --format=json "192.168.1.0/24"
# 输出: {
#   "ranges": ["192.168.1.0-192.168.1.255"],
#   "cidr": ["192.168.1.0/24"],
#   "total_ips": 256
# }
```

### 高级用法

```bash
# IPv6支持
ippool --ipv6 "2001:db8::/48" "2001:db8:1::/48"

# 输出到文件
ippool --format=json --output=result.json "192.168.1.0/24"

# 复杂操作
ippool --format=stat "192.168.1.0/24,10.0.0.0/8,172.16.0.0/16"

# 批量处理多个文件
ippool --format=cidr -o merged.txt @file1.txt @file2.txt @file3.txt

# 从标准输入处理
echo "192.168.1.0/24\n10.0.0.0/8" | ippool --format=json -
```

### overlap 子命令

- overlap 子命令用于查找多个 IP 段/网段输入中的所有重叠区间，并输出每个重叠区间及其涉及的源区间。
- 支持 IPv4 和 IPv6，支持混合输入格式（CIDR、范围、整数、@文件、stdin 等）。


```sh
ippool overlap 192.168.1.0/24 192.168.1.128/25
ippool --ipv6 overlap 2001:db8::/48 2001:db8:0:8000::/49 2001:db8::1-2001:db8::10
```

```
[192.168.1.128-192.168.1.255]:
    192.168.1.0/24
    192.168.1.128/25
```

- 每个重叠区间用中括号括起，后跟所有涉及的源区间。
- 支持文件输入、stdin、混合格式等所有主命令支持的输入方式。

---

## 命令行帮助

```bash
ippool --help
ippool diff --help
ippool intersect --help
```

---

## 常见问题 FAQ

**Q: 支持哪些Python版本？**  
A: Python 3.7 及以上。

**Q: 支持哪些输入格式？**  
A: 支持CIDR（如 192.168.1.0/24）、区间字符串（如 192.168.1.1-192.168.1.10）、元组、对象、文件等。

**Q: 如何批量处理大池？**  
A: 推荐使用命令行工具，或分批处理，避免一次性展开所有IP。

**Q: 如何输出为JSON？**  
A: 使用 `--format=json`，如 `ippool "192.168.1.0/24" --format=json`

**Q: 支持IPv6吗？**  
A: 支持，命令行加 `--ipv6`。

**Q: 如何从文件读取？**  
A: 使用 `@` 符号，如 `ippool @ranges.txt`

**Q: 如何从标准输入读取？**  
A: 使用 `-` 符号，如 `cat ranges.txt | ippool -`

---

## Python API 详细示例

### 网络管理场景

```python
from ippool import IPv4Pool

# 场景1: 管理公司网络分配
company_networks = IPv4Pool([
    "10.0.0.0/8",      # 总部网络
    "172.16.0.0/12",   # 分支机构
    "192.168.0.0/16"   # 办公网络
])

# 分配部门网络
dept_allocations = {
    "IT部门": IPv4Pool("10.0.1.0/24"),
    "财务部": IPv4Pool("10.0.2.0/24"),
    "人事部": IPv4Pool("10.0.3.0/24")
}

# 检查是否有冲突
for dept, network in dept_allocations.items():
    if company_networks & network:
        print(f"{dept}网络分配有效")
    else:
        print(f"{dept}网络分配无效")

# 场景2: 安全策略配置
allowed_networks = IPv4Pool("192.168.1.0/24")
blocked_ranges = IPv4Pool([
    "192.168.1.100-192.168.1.110",  # 服务器维护时段
    "192.168.1.200-192.168.1.255"   # 测试环境
])

# 计算实际允许的网络
effective_allowed = allowed_networks - blocked_ranges
print(f"实际允许访问的IP数量: {effective_allowed.num_addresses}")
```

### 云平台资源管理

```python
from ippool import IPv4Pool, IPv6Pool

# 场景3: 云平台VPC管理
vpc_pools = {
    "vpc-1": IPv4Pool("10.1.0.0/16"),
    "vpc-2": IPv4Pool("10.2.0.0/16"),
    "vpc-3": IPv4Pool("10.3.0.0/16")
}

# 检查VPC间是否有IP冲突
def check_vpc_conflicts(vpc_pools):
    vpc_list = list(vpc_pools.values())
    for i, pool1 in enumerate(vpc_list):
        for j, pool2 in enumerate(vpc_list[i+1:], i+1):
            if pool1 & pool2:
                print(f"VPC {i+1} 和 VPC {j+1} 存在IP冲突")
                return True
    return False

# 场景4: 容器网络规划
kubernetes_pods = IPv4Pool("10.244.0.0/16")
kubernetes_services = IPv4Pool("10.96.0.0/12")

# 确保Pod和Service网络不重叠
if kubernetes_pods & kubernetes_services:
    print("警告: Pod和Service网络存在重叠")
else:
    print("Pod和Service网络配置正确")
```

### 数据分析与统计

```python
from ippool import IPv4Pool

# 场景5: 网络流量分析
def analyze_network_coverage(access_logs, network_pools):
    """
    分析访问日志中的IP地址覆盖情况
    """
    # 假设access_logs是包含IP地址的列表
    accessed_ips = IPv4Pool(access_logs)
    
    results = {}
    for name, pool in network_pools.items():
        overlap = accessed_ips & pool
        coverage_rate = overlap.num_addresses / pool.num_addresses
        results[name] = {
            "total_ips": pool.num_addresses,
            "accessed_ips": overlap.num_addresses,
            "coverage_rate": coverage_rate
        }
    
    return results

# 场景6: 网络利用率统计
def calculate_network_utilization(allocated_pools, total_network):
    """
    计算网络利用率
    """
    total_allocated = IPv4Pool()
    for pool in allocated_pools:
        total_allocated += pool
    
    utilization = total_allocated & total_network
    utilization_rate = utilization.num_addresses / total_network.num_addresses
    
    return {
        "total_ips": total_network.num_addresses,
        "allocated_ips": utilization.num_addresses,
        "utilization_rate": utilization_rate,
        "available_ips": total_network.num_addresses - utilization.num_addresses
    }
```

### 自动化脚本示例

```python
from ippool import IPv4Pool
import json

# 场景7: 批量网络配置生成
def generate_network_configs(base_network, subnet_count, subnet_size):
    """
    从基础网络生成多个子网配置
    """
    base_pool = IPv4Pool(base_network)
    configs = []
    
    # 这里简化处理，实际需要更复杂的子网划分逻辑
    for i in range(subnet_count):
        # 示例：创建子网配置
        config = {
            "name": f"subnet-{i+1}",
            "network": f"10.0.{i}.0/24",
            "gateway": f"10.0.{i}.1",
            "dhcp_range": f"10.0.{i}.10-10.0.{i}.254"
        }
        configs.append(config)
    
    return configs

# 场景8: 配置文件验证
def validate_network_config(config_file):
    """
    验证网络配置文件中的IP地址设置
    """
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    networks = IPv4Pool()
    errors = []
    
    for item in config.get('networks', []):
        try:
            network = IPv4Pool(item['cidr'])
            # 检查是否有重叠
            if networks & network:
                errors.append(f"网络 {item['name']} 与其他网络重叠")
            networks += network
        except Exception as e:
            errors.append(f"网络 {item['name']} 配置错误: {e}")
    
    return errors

# 使用示例
if __name__ == "__main__":
    # 验证配置文件
    errors = validate_network_config('network_config.json')
    if errors:
        print("配置验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置验证通过")
```

---

## 许可证

MIT License，详见 [LICENSE](LICENSE)。

---

## 相关链接

- [PyPI](https://pypi.org/project/ipools/)
- [GitHub](https://github.com/jackyspy/ippool)

---

## 作者

- [jackyspy](https://github.com/jackyspy)
- [Theunsafe](https://github.com/Theunsafe)
- [tutu](https://github.com/tutu) 