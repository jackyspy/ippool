# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2020-03-12

### Added
- Initial release of ippool
- Efficient IPv4/IPv6 address pool management and operations
- Fast add/remove/merge of IP ranges and networks
- Support for both IPv4 and IPv6 protocols
- Flexible input formats: CIDR, range strings, tuples, objects
- Efficient intersection, subtraction, and membership operations
- Output as summarized networks or raw ranges
- Pythonic API with comprehensive test coverage
- Command-line interface with multiple input/output formats
- Support for multiple input separators (comma, semicolon, space)
- File input support with @ prefix
- Stdin input support with - symbol
- Multiple output formats: range (default), cidr, stat, json
- IPv6 support in CLI
- Comprehensive error handling and validation
- Production-ready codebase with extensive test suite

### Features
- **Core Operations**: Merge, diff, intersect operations on IP pools
- **Input Flexibility**: Direct input, file reading, stdin support
- **Output Formats**: Range, CIDR, statistics, and JSON formats
- **Performance**: Optimized algorithms for large IP pools
- **Compatibility**: Python 3.7+ support
- **Documentation**: Comprehensive README in English and Chinese

