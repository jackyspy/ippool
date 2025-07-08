# -*- coding: utf-8 -*-
# Created by jackyspy at 2020/3/12
from functools import total_ordering
import socket


@total_ordering
class IPv6Address(int):
    __slots__ = ()

    def __new__(cls, address):
        if isinstance(address, (int, IPv6Address)):
            if address < 0 or address > (1 << 128) - 1:
                raise ValueError(f"IPv6 address value out of range: {address}")
            value = address
        elif isinstance(address, str):
            try:
                ip_bytes = socket.inet_pton(socket.AF_INET6, address)
                value = int.from_bytes(ip_bytes, byteorder='big')
            except OSError as e:
                raise ValueError(f"Invalid IPv6 address: {address}") from e
        else:
            raise TypeError(f"Invalid address type: {type(address)}")

        return super().__new__(cls, value)

    def __str__(self):
        return socket.inet_ntop(socket.AF_INET6,
                                self.to_bytes(16, byteorder='big'))

    def __repr__(self):
        return f"IPv6Address('{str(self)}')"

    def __eq__(self, other):
        if isinstance(other, str):
            other = IPv6Address(other)

        return super().__eq__(other)

    def __lt__(self, other):
        if isinstance(other, str):
            other = IPv6Address(other)

        return super().__lt__(other)

    def __hash__(self):
        return int(self)


@total_ordering
class IPv6Network:
    __slots__ = ("_ip", "_mask_bit")

    def __init__(self, network):
        if isinstance(network, str):
            if "/" in network:
                ip_str, mask_bit_str = network.split("/")
                self._ip = int(IPv6Address(ip_str))
                self._mask_bit = int(mask_bit_str)
            else:
                self._ip = int(IPv6Address(network))
                self._mask_bit = 128
        elif isinstance(network, tuple) and len(network) == 2:
            self._ip = int(network[0])
            self._mask_bit = int(network[1])
        elif isinstance(network, IPv6Network):
            self._ip = network._ip
            self._mask_bit = network._mask_bit
        else:
            raise TypeError(f"Invalid network type: {type(network)}")

        if not (0 <= self._mask_bit <= 128):
            raise ValueError("mask_bit must be between 0 and 128")

        self._ip = self._ip & self._netmask_int()

    def _netmask_int(self):
        return ((1 << self._mask_bit) -
                1) << (128 - self._mask_bit) if self._mask_bit else 0

    @property
    def network_address(self):
        return IPv6Address(self._ip)

    @property
    def broadcast_address(self):
        return IPv6Address(self._ip | ((1 << (128 - self._mask_bit)) - 1))

    @property
    def num_addresses(self):
        return 1 << (128 - self._mask_bit)

    def __str__(self):
        return f"{str(self.network_address)}/{self._mask_bit}"

    def __repr__(self):
        return f"IPv6Network('{str(self)}')'"

    def __eq__(self, other):
        if isinstance(other, IPv6Network):
            return self._ip == other._ip and self._mask_bit == other._mask_bit

        raise TypeError("other must be an IPv4Network object")

    def __lt__(self, other):
        if isinstance(other, IPv6Network):
            if self._ip != other._ip:
                return self._ip < other._ip

            return self._mask_bit > other._mask_bit

        raise TypeError("other must be an IPv4Network object")

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self < other or self == other)

    def __ge__(self, other):
        return not (self < other)

    def subnet_of(self, other):
        """Check if this network is a subnet of another network."""
        if not isinstance(other, IPv6Network):
            raise TypeError("other must be an IPv6Network object")
        return (self._mask_bit >= other._mask_bit
                and (self._ip & other._netmask_int()) == other._ip)
