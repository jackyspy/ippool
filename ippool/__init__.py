# -*- coding: utf-8 -*-
# Created by jackyspy at 2020/3/12
"""IP地址池管理工具
主要完成IP地址段解析、合并、剔除等。
具有IP地址遍历能力。IPv4和IPv6使用不同类完成。

参数可以指定IP地址、网络地址、IP地址范围等。
>>> IPv4Pool('192.168.1.1')
IPv4Pool((IPv4Network('192.168.1.1/32'),))
>>> IPv4Pool('192.168.1.0/24')
IPv4Pool((IPv4Network('192.168.1.0/24'),))
>>> IPv4Pool('192.168.1.0/28')
IPv4Pool((IPv4Network('192.168.1.0/28'),))
>>> IPv4Pool('192.168.0.64-192.168.0.255')
IPv4Pool((IPv4Network('192.168.0.64/26'), IPv4Network('192.168.0.128/25')))

pool.add(ip_networks) 合并网络，等同于pool += ip_networks。别名：push(ip_networks)
ip_networks可以是网络地址、网段、IPv4Network实例和IPv4Pool实例。可以是上述对象的list/tuple等。
>>> pool = IPv4Pool('192.168.1.0/28')
>>> pool.add('192.168.1.0/24')
>>> pool
IPv4Pool((IPv4Network('192.168.1.0/24'),))
>>> pool += IPv4Pool('192.168.0.0/24')
>>> pool
IPv4Pool((IPv4Network('192.168.0.0/23'),))
>>> pool += IPv4Pool('192.168.0.0-192.168.0.255')
>>> pool += IPv4Pool('192.168.2.0-192.168.2.31')
>>> pool
IPv4Pool((IPv4Network('192.168.0.0/23'), IPv4Network('192.168.2.0/27')))

pool.remove(self, other, strict=False) 剔除某一部分网络。等同于pool -= ip_networks。别名：pop(ip_networks)
strict=True时，要求other必须包含于pool.networks某一部分。
strict=False时，other可以在pool中不存在，也可以跨多个网段。
>>> pool.remove('192.168.0.0/24')
IPv4Pool((IPv4Network('192.168.1.0/24'), IPv4Network('192.168.2.0/26'), IPv4Network('192.168.2.64/27')))
>>> pool -= '192.168.2.0/24', IPv4Network('192.168.1.0/26')
>>> pool
IPv4Pool((IPv4Network('192.168.1.64/26'), IPv4Network('192.168.1.128/25')))

+/-/& 分别用于合并、剔除和交集操作。 &等同于intersection()
>>> IPv4Pool('192.168.1.0/25') + IPv4Pool('192.168.1.128/25')
IPv4Pool((IPv4Network('192.168.1.0/24'),))
>>> IPv4Pool('192.168.1.0/24') - IPv4Pool('192.168.1.0/25')
IPv4Pool((IPv4Network('192.168.1.128/25'),))
>>> IPv4Pool('192.168.1.0/25') & '192.168.1.64-192.168.1.200'
IPv4Pool((IPv4Network('192.168.1.64/26'),))

item in pool 判断网段是否包含
>>> '192.168.1.0/25' in IPv4Pool('192.168.1.0/24')
True
>>> IPv4Network('192.168.1.0/24') in IPv4Pool('192.168.1.0/25')
False

pool.copy() 建立副本

len(pool)或pool.num_addresses属性，计算地址池的地址数量（不剔除网络地址、广播地址等）

pool == other 地址池比较

str(pool)、repr(pool)输出pool

iter(pool) 遍历所有的IP地址
>>> for ip in IPv4Pool('192.168.1.0/27'):
...     print(ip)
...
192.168.1.0
192.168.1.1
...

pool.networks属性，IPv4Network类型的tuple
"""
from .iprange import IPv4Range, IPv6Range
from .ippool import IPv4Pool, IPv6Pool
from .utils import (merge_ip_ranges, summarize_range, collapse_networks,
                    find_overlapping_ranges)

__all__ = [
    "IPv4Pool", "IPv6Pool", "IPv4Range", "IPv6Range", "merge_ip_ranges",
    "summarize_range", "collapse_networks", "find_overlapping_ranges"
]
