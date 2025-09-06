# 3. Protobuf与gRPC入门

## 目录

- [3. Protobuf与gRPC入门](#3-protobuf与grpc入门)
  - [目录](#目录)
  - [1. 引言与背景](#1-引言与背景)
    - [1.1 Protobuf与gRPC的关系](#11-protobuf与grpc的关系)
    - [1.2 为什么选择Protobuf和gRPC](#12-为什么选择protobuf和grpc)
  - [2. Protobuf基础概念](#2-protobuf基础概念)
    - [2.1 语法版本](#21-语法版本)
    - [2.2 数据类型](#22-数据类型)
    - [2.3 字段规则](#23-字段规则)
    - [2.4 包和导入](#24-包和导入)
  - [3. 消息定义](#3-消息定义)
    - [3.1 基本消息结构](#31-基本消息结构)
    - [3.2 嵌套消息](#32-嵌套消息)
    - [3.3 枚举类型](#33-枚举类型)
    - [3.4 映射类型](#34-映射类型)
    - [3.5 导入标准类型](#35-导入标准类型)
  - [4. 服务定义](#4-服务定义)
    - [4.1 一元RPC](#41-一元rpc)
    - [4.2 服务器流式RPC](#42-服务器流式rpc)
    - [4.3 客户端流式RPC](#43-客户端流式rpc)
    - [4.4 双向流式RPC](#44-双向流式rpc)
  - [5. 高级特性](#5-高级特性)
    - [5.1 字段编号管理](#51-字段编号管理)
    - [5.2 向后兼容性](#52-向后兼容性)
    - [5.3 选项和扩展](#53-选项和扩展)
    - [5.4 代码生成](#54-代码生成)
  - [6. 工具链与最佳实践](#6-工具链与最佳实践)
    - [6.1 开发工具](#61-开发工具)
    - [6.2 版本控制策略](#62-版本控制策略)
    - [6.3 性能优化](#63-性能优化)
    - [6.4 调试技巧](#64-调试技巧)
  - [7. 实际应用案例](#7-实际应用案例)
    - [7.1 微服务通信](#71-微服务通信)
    - [7.2 数据存储](#72-数据存储)
    - [7.3 配置管理](#73-配置管理)
  - [8. 参考文献](#8-参考文献)
    - [8.1 官方文档](#81-官方文档)
    - [8.2 工具文档](#82-工具文档)
    - [8.3 最佳实践](#83-最佳实践)
    - [8.4 相关技术](#84-相关技术)

---

## 1. 引言与背景

Protocol Buffers (Protobuf) 是 Google 开发的一种语言无关、平台无关、可扩展的序列化数据格式，常用于通信协议和数据存储。
它通过接口定义语言（IDL）来定义数据结构和服务，然后使用编译器为不同语言生成高效的本地代码。

gRPC 是一个基于 Protobuf 的高性能、开源的通用 RPC (Remote Procedure Call) 框架。

### 1.1 Protobuf与gRPC的关系

- **Protobuf**: 数据序列化格式和IDL
- **gRPC**: 基于HTTP/2的RPC框架，使用Protobuf作为消息格式
- **协同工作**: Protobuf定义接口，gRPC实现通信

### 1.2 为什么选择Protobuf和gRPC

**优势**：

- **高性能**: 二进制格式，序列化/反序列化速度快
- **强类型**: 编译时类型检查，减少运行时错误
- **跨语言**: 支持多种编程语言
- **向后兼容**: 字段编号机制保证API演进
- **代码生成**: 自动生成客户端和服务端代码

**适用场景**：

- 微服务间通信
- 高性能API
- 跨语言系统集成
- 大数据传输

## 2. Protobuf基础概念

### 2.1 语法版本

Protobuf支持两种语法版本：

```protobuf
// Proto2 语法（旧版本，仍在使用）
syntax = "proto2";

// Proto3 语法（推荐，简化了语法）
syntax = "proto3";
```

**Proto3的主要改进**：

- 移除了required字段
- 简化了默认值规则
- 改进了枚举处理
- 更好的JSON映射

### 2.2 数据类型

Protobuf支持多种数据类型：

```protobuf
syntax = "proto3";

message DataTypes {
  // 数值类型
  int32 int_field = 1;        // 32位有符号整数
  int64 long_field = 2;       // 64位有符号整数
  uint32 uint_field = 3;      // 32位无符号整数
  uint64 ulong_field = 4;     // 64位无符号整数
  sint32 sint_field = 5;      // 32位有符号整数（变长编码）
  sint64 slong_field = 6;     // 64位有符号整数（变长编码）
  fixed32 fixed32_field = 7;  // 32位无符号整数（固定长度）
  fixed64 fixed64_field = 8;  // 64位无符号整数（固定长度）
  sfixed32 sfixed32_field = 9; // 32位有符号整数（固定长度）
  sfixed64 sfixed64_field = 10; // 64位有符号整数（固定长度）
  
  // 浮点类型
  float float_field = 11;     // 32位浮点数
  double double_field = 12;   // 64位浮点数
  
  // 字符串类型
  string string_field = 13;   // UTF-8编码字符串
  bytes bytes_field = 14;     // 字节数组
  
  // 布尔类型
  bool bool_field = 15;       // 布尔值
}
```

### 2.3 字段规则

```protobuf
syntax = "proto3";

message FieldRules {
  // 单数字段（默认）
  string single_field = 1;
  
  // 可选字段（Proto3中所有字段默认都是可选的）
  optional string optional_field = 2;
  
  // 重复字段（数组/列表）
  repeated string repeated_field = 3;
  
  // 打包重复字段（更高效的编码）
  repeated int32 packed_field = 4 [packed = true];
}
```

### 2.4 包和导入

```protobuf
syntax = "proto3";

// 包声明，防止命名冲突
package com.example.user;

// 导入其他proto文件
import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// 导入公共proto文件
import "common/types.proto";

// 使用导入的类型
message User {
  string id = 1;
  string name = 2;
  google.protobuf.Timestamp created_at = 3;
  common.UserType type = 4;
}
```

## 3. 消息定义

### 3.1 基本消息结构

```protobuf
syntax = "proto3";

package user_service;

// 用户消息定义
message User {
  // 基本字段
  string id = 1;
  string username = 2;
  string email = 3;
  string full_name = 4;
  
  // 可选字段
  optional string phone = 5;
  optional string avatar_url = 6;
  
  // 重复字段
  repeated string roles = 7;
  repeated Permission permissions = 8;
  
  // 时间戳
  google.protobuf.Timestamp created_at = 9;
  google.protobuf.Timestamp updated_at = 10;
  
  // 枚举字段
  UserStatus status = 11;
  
  // 嵌套消息
  Address address = 12;
  
  // 映射字段
  map<string, string> metadata = 13;
}

// 权限消息
message Permission {
  string resource = 1;
  string action = 2;
  bool granted = 3;
}

// 地址消息
message Address {
  string street = 1;
  string city = 2;
  string state = 3;
  string country = 4;
  string postal_code = 5;
}

// 用户状态枚举
enum UserStatus {
  UNKNOWN = 0;    // 默认值
  ACTIVE = 1;
  INACTIVE = 2;
  SUSPENDED = 3;
  DELETED = 4;
}
```

### 3.2 嵌套消息

```protobuf
syntax = "proto3";

package ecommerce;

// 订单消息
message Order {
  string order_id = 1;
  string user_id = 2;
  repeated OrderItem items = 3;
  OrderStatus status = 4;
  
  // 嵌套消息定义
  message OrderItem {
    string product_id = 1;
    string product_name = 2;
    int32 quantity = 3;
    double unit_price = 4;
    double total_price = 5;
  }
  
  // 嵌套枚举
  enum OrderStatus {
    PENDING = 0;
    CONFIRMED = 1;
    SHIPPED = 2;
    DELIVERED = 3;
    CANCELLED = 4;
  }
}
```

### 3.3 枚举类型

```protobuf
syntax = "proto3";

package payment;

// 支付方式枚举
enum PaymentMethod {
  UNKNOWN_PAYMENT_METHOD = 0;
  CREDIT_CARD = 1;
  DEBIT_CARD = 2;
  BANK_TRANSFER = 3;
  DIGITAL_WALLET = 4;
  CRYPTOCURRENCY = 5;
}

// 支付状态枚举
enum PaymentStatus {
  UNKNOWN_STATUS = 0;
  PENDING = 1;
  PROCESSING = 2;
  COMPLETED = 3;
  FAILED = 4;
  REFUNDED = 5;
  CANCELLED = 6;
}

// 使用枚举的消息
message Payment {
  string payment_id = 1;
  string order_id = 2;
  double amount = 3;
  string currency = 4;
  PaymentMethod method = 5;
  PaymentStatus status = 6;
  google.protobuf.Timestamp created_at = 7;
}
```

### 3.4 映射类型

```protobuf
syntax = "proto3";

package config;

// 配置消息
message Configuration {
  string app_name = 1;
  string version = 2;
  
  // 字符串到字符串的映射
  map<string, string> environment_vars = 3;
  
  // 字符串到数值的映射
  map<string, int32> limits = 4;
  
  // 字符串到布尔值的映射
  map<string, bool> features = 5;
  
  // 字符串到消息的映射
  map<string, DatabaseConfig> databases = 6;
}

// 数据库配置
message DatabaseConfig {
  string host = 1;
  int32 port = 2;
  string username = 3;
  string password = 4;
  string database = 5;
}
```

### 3.5 导入标准类型

```protobuf
syntax = "proto3";

package example;

// 导入Google提供的标准类型
import "google/protobuf/timestamp.proto";
import "google/protobuf/duration.proto";
import "google/protobuf/wrappers.proto";
import "google/protobuf/struct.proto";
import "google/protobuf/any.proto";
import "google/protobuf/empty.proto";

// 使用标准类型的消息
message Event {
  string event_id = 1;
  string event_type = 2;
  
  // 时间戳
  google.protobuf.Timestamp timestamp = 3;
  
  // 持续时间
  google.protobuf.Duration duration = 4;
  
  // 包装类型（可以为null）
  google.protobuf.StringValue description = 5;
  google.protobuf.Int32Value priority = 6;
  
  // 动态结构
  google.protobuf.Struct metadata = 7;
  
  // 任意类型
  google.protobuf.Any payload = 8;
}

// 使用空消息的服务
service EventService {
  rpc CreateEvent(CreateEventRequest) returns (google.protobuf.Empty);
  rpc GetEvent(GetEventRequest) returns (Event);
}
```

## 4. 服务定义

### 4.1 一元RPC

```protobuf
syntax = "proto3";

package user_service;

import "google/protobuf/timestamp.proto";

// 用户服务
service UserService {
  // 一元RPC：客户端发送一个请求，服务器返回一个响应
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
}

// 请求和响应消息
message CreateUserRequest {
  string username = 1;
  string email = 2;
  string full_name = 3;
  string password = 4;
}

message CreateUserResponse {
  User user = 1;
  bool success = 2;
  string message = 3;
}

message GetUserRequest {
  string user_id = 1;
}

message GetUserResponse {
  User user = 1;
  bool found = 2;
}

message UpdateUserRequest {
  string user_id = 1;
  string username = 2;
  string email = 3;
  string full_name = 4;
}

message UpdateUserResponse {
  User user = 1;
  bool success = 2;
  string message = 3;
}

message DeleteUserRequest {
  string user_id = 1;
}

message DeleteUserResponse {
  bool success = 1;
  string message = 2;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total_count = 2;
  int32 page = 3;
  int32 page_size = 4;
}

// 用户消息
message User {
  string id = 1;
  string username = 2;
  string email = 3;
  string full_name = 4;
  UserStatus status = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
}

enum UserStatus {
  UNKNOWN = 0;
  ACTIVE = 1;
  INACTIVE = 2;
  SUSPENDED = 3;
}
```

### 4.2 服务器流式RPC

```protobuf
syntax = "proto3";

package monitoring;

import "google/protobuf/timestamp.proto";

// 监控服务
service MonitoringService {
  // 服务器流式RPC：客户端发送一个请求，服务器返回一个数据流
  rpc StreamMetrics(StreamMetricsRequest) returns (stream MetricData);
  rpc StreamLogs(StreamLogsRequest) returns (stream LogEntry);
  rpc StreamEvents(StreamEventsRequest) returns (stream Event);
}

message StreamMetricsRequest {
  string service_name = 1;
  repeated string metric_names = 2;
  int32 interval_seconds = 3;
  int32 duration_seconds = 4;
}

message MetricData {
  string metric_name = 1;
  double value = 2;
  string unit = 3;
  google.protobuf.Timestamp timestamp = 4;
  map<string, string> labels = 5;
}

message StreamLogsRequest {
  string service_name = 1;
  string log_level = 2;
  google.protobuf.Timestamp start_time = 3;
  google.protobuf.Timestamp end_time = 4;
}

message LogEntry {
  string service_name = 1;
  string level = 2;
  string message = 3;
  google.protobuf.Timestamp timestamp = 4;
  map<string, string> context = 5;
}

message StreamEventsRequest {
  string event_type = 1;
  repeated string filters = 2;
}

message Event {
  string event_id = 1;
  string event_type = 2;
  string source = 3;
  google.protobuf.Timestamp timestamp = 4;
  map<string, string> data = 5;
}
```

### 4.3 客户端流式RPC

```protobuf
syntax = "proto3";

package file_upload;

import "google/protobuf/timestamp.proto";

// 文件上传服务
service FileUploadService {
  // 客户端流式RPC：客户端发送一个数据流，服务器返回一个响应
  rpc UploadFile(stream FileChunk) returns (UploadResponse);
  rpc UploadMultipleFiles(stream FileChunk) returns (UploadResponse);
  rpc StreamData(stream DataChunk) returns (StreamResponse);
}

message FileChunk {
  string file_id = 1;
  string filename = 2;
  bytes data = 3;
  int32 chunk_index = 4;
  int32 total_chunks = 5;
  bool is_last_chunk = 6;
  map<string, string> metadata = 7;
}

message UploadResponse {
  string file_id = 1;
  string filename = 2;
  int64 file_size = 3;
  string checksum = 4;
  bool success = 5;
  string message = 6;
  google.protobuf.Timestamp uploaded_at = 7;
}

message DataChunk {
  string stream_id = 1;
  bytes data = 2;
  int32 sequence_number = 3;
  bool is_last = 4;
}

message StreamResponse {
  string stream_id = 1;
  int32 total_chunks_received = 2;
  int64 total_bytes_received = 3;
  bool success = 4;
  string message = 5;
}
```

### 4.4 双向流式RPC

```protobuf
syntax = "proto3";

package chat;

import "google/protobuf/timestamp.proto";

// 聊天服务
service ChatService {
  // 双向流式RPC：客户端和服务器都可以互相发送数据流
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
  rpc VideoCall(stream VideoFrame) returns (stream VideoFrame);
  rpc AudioCall(stream AudioFrame) returns (stream AudioFrame);
}

message ChatMessage {
  string message_id = 1;
  string user_id = 2;
  string room_id = 3;
  string content = 4;
  MessageType type = 5;
  google.protobuf.Timestamp timestamp = 6;
  map<string, string> metadata = 7;
}

enum MessageType {
  UNKNOWN = 0;
  TEXT = 1;
  IMAGE = 2;
  FILE = 3;
  SYSTEM = 4;
}

message VideoFrame {
  string frame_id = 1;
  string user_id = 2;
  bytes frame_data = 3;
  int32 width = 4;
  int32 height = 5;
  string format = 6;
  google.protobuf.Timestamp timestamp = 7;
}

message AudioFrame {
  string frame_id = 1;
  string user_id = 2;
  bytes audio_data = 3;
  int32 sample_rate = 4;
  int32 channels = 5;
  google.protobuf.Timestamp timestamp = 6;
}
```

## 5. 高级特性

### 5.1 字段编号管理

```protobuf
syntax = "proto3";

package example;

// 字段编号的重要性
message User {
  // 字段编号1-15使用1个字节编码
  string id = 1;
  string name = 2;
  string email = 3;
  
  // 字段编号16-2047使用2个字节编码
  string description = 16;
  string avatar_url = 17;
  
  // 保留字段编号（防止未来使用）
  reserved 4, 5, 6;
  reserved "old_field1", "old_field2";
  
  // 使用注释说明字段编号的用途
  string phone = 7;      // 用户电话
  string address = 8;    // 用户地址
  int32 age = 9;         // 用户年龄
}
```

### 5.2 向后兼容性

```protobuf
syntax = "proto3";

package example;

// 版本1的消息
message UserV1 {
  string id = 1;
  string name = 2;
  string email = 3;
}

// 版本2的消息（向后兼容）
message UserV2 {
  string id = 1;           // 保持相同的字段编号
  string name = 2;         // 保持相同的字段编号
  string email = 3;        // 保持相同的字段编号
  string phone = 4;        // 新增字段
  string address = 5;      // 新增字段
  
  // 不要删除或重用字段编号
  // 不要改变字段类型
  // 不要改变字段名称
}
```

### 5.3 选项和扩展

```protobuf
syntax = "proto3";

package example;

import "google/protobuf/descriptor.proto";

// 使用选项
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  
  // 字段选项
  string password = 4 [deprecated = true];
  string phone = 5 [json_name = "phone_number"];
  
  // 消息选项
  option deprecated = false;
}

// 服务选项
service UserService {
  option deprecated = false;
  
  rpc GetUser(GetUserRequest) returns (GetUserResponse) {
    option deprecated = false;
  }
}

// 文件选项
option java_package = "com.example.user";
option java_outer_classname = "UserProto";
option go_package = "github.com/example/user";
option csharp_namespace = "Example.User";
```

### 5.4 代码生成

```bash
# 安装protoc编译器
# macOS
brew install protobuf

# Ubuntu/Debian
sudo apt-get install protobuf-compiler

# 生成代码
protoc --go_out=. --go_opt=paths=source_relative \
       --go-grpc_out=. --go-grpc_opt=paths=source_relative \
       user.proto

# 生成多种语言的代码
protoc --cpp_out=. \
       --csharp_out=. \
       --java_out=. \
       --js_out=. \
       --python_out=. \
       --ruby_out=. \
       --rust_out=. \
       user.proto
```

## 6. 工具链与最佳实践

### 6.1 开发工具

```bash
# 1. protoc编译器
protoc --version

# 2. buf工具（现代化的protobuf工具链）
# 安装
curl -sSL \
  "https://github.com/bufbuild/buf/releases/download/v1.28.1/buf-$(uname -s)-$(uname -m)" \
  -o "$HOME/.local/bin/buf" && chmod +x "$HOME/.local/bin/buf"

# 使用buf
buf lint
buf format
buf generate
buf breaking --against '.git#branch=main'

# 3. grpcurl（gRPC调试工具）
# 安装
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# 使用grpcurl
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 describe user.UserService
grpcurl -plaintext -d '{"user_id": "123"}' localhost:50051 user.UserService/GetUser
```

### 6.2 版本控制策略

```protobuf
// 版本控制最佳实践
syntax = "proto3";

package user.v1;  // 使用版本化的包名

// 使用语义化版本控制
option go_package = "github.com/example/user/v1;userv1";

// 在文件名中包含版本
// user_v1.proto

// 使用buf.yaml进行版本管理
```

```yaml
# buf.yaml
version: v1
name: buf.build/example/user
deps:
  - buf.build/googleapis/googleapis
lint:
  use:
    - DEFAULT
breaking:
  use:
    - FILE
```

### 6.3 性能优化

```protobuf
syntax = "proto3";

package example;

// 性能优化技巧
message OptimizedMessage {
  // 1. 使用packed编码减少重复字段的大小
  repeated int32 numbers = 1 [packed = true];
  
  // 2. 合理使用字段编号（1-15使用1字节编码）
  string id = 1;
  string name = 2;
  string email = 3;
  
  // 3. 避免使用不必要的包装类型
  int32 count = 4;  // 而不是 google.protobuf.Int32Value
  
  // 4. 使用适当的数值类型
  int32 small_number = 5;     // 对于小数字
  int64 large_number = 6;     // 对于大数字
  sint32 signed_number = 7;   // 对于有符号数字（变长编码）
}
```

### 6.4 调试技巧

```bash
# 1. 使用protoc的调试选项
protoc --descriptor_set_out=user.pb --include_imports user.proto

# 2. 使用grpcurl进行调试
grpcurl -plaintext -d @ localhost:50051 user.UserService/CreateUser << EOF
{
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "Test User"
}
EOF

# 3. 使用protobuf的文本格式进行调试
cat > user.txt << EOF
id: "123"
username: "testuser"
email: "test@example.com"
full_name: "Test User"
EOF

protoc --encode=user.User user.proto < user.txt > user.bin
protoc --decode=user.User user.proto < user.bin
```

## 7. 实际应用案例

### 7.1 微服务通信

```protobuf
syntax = "proto3";

package order_service;

import "google/protobuf/timestamp.proto";

// 订单服务
service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (CreateOrderResponse);
  rpc GetOrder(GetOrderRequest) returns (GetOrderResponse);
  rpc UpdateOrder(UpdateOrderRequest) returns (UpdateOrderResponse);
  rpc CancelOrder(CancelOrderRequest) returns (CancelOrderResponse);
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
}

message CreateOrderRequest {
  string user_id = 1;
  repeated OrderItem items = 2;
  Address shipping_address = 3;
  PaymentInfo payment_info = 4;
}

message CreateOrderResponse {
  Order order = 1;
  bool success = 2;
  string message = 3;
}

message Order {
  string order_id = 1;
  string user_id = 2;
  repeated OrderItem items = 3;
  double total_amount = 4;
  string currency = 5;
  OrderStatus status = 6;
  Address shipping_address = 7;
  PaymentInfo payment_info = 8;
  google.protobuf.Timestamp created_at = 9;
  google.protobuf.Timestamp updated_at = 10;
}

message OrderItem {
  string product_id = 1;
  string product_name = 2;
  int32 quantity = 3;
  double unit_price = 4;
  double total_price = 5;
}

message Address {
  string street = 1;
  string city = 2;
  string state = 3;
  string country = 4;
  string postal_code = 5;
}

message PaymentInfo {
  string payment_method = 1;
  string card_last_four = 2;
  string billing_address = 3;
}

enum OrderStatus {
  UNKNOWN = 0;
  PENDING = 1;
  CONFIRMED = 2;
  SHIPPED = 3;
  DELIVERED = 4;
  CANCELLED = 5;
}

// 其他请求/响应消息...
message GetOrderRequest {
  string order_id = 1;
}

message GetOrderResponse {
  Order order = 1;
  bool found = 2;
}

message UpdateOrderRequest {
  string order_id = 1;
  OrderStatus status = 2;
  repeated OrderItem items = 3;
}

message UpdateOrderResponse {
  Order order = 1;
  bool success = 2;
  string message = 3;
}

message CancelOrderRequest {
  string order_id = 1;
  string reason = 2;
}

message CancelOrderResponse {
  bool success = 1;
  string message = 2;
}

message ListOrdersRequest {
  string user_id = 1;
  int32 page = 2;
  int32 page_size = 3;
  OrderStatus status = 4;
}

message ListOrdersResponse {
  repeated Order orders = 1;
  int32 total_count = 2;
  int32 page = 3;
  int32 page_size = 4;
}
```

### 7.2 数据存储

```protobuf
syntax = "proto3";

package data_store;

import "google/protobuf/timestamp.proto";

// 数据存储服务
service DataStoreService {
  rpc Put(PutRequest) returns (PutResponse);
  rpc Get(GetRequest) returns (GetResponse);
  rpc Delete(DeleteRequest) returns (DeleteResponse);
  rpc List(ListRequest) returns (stream KeyValue);
  rpc Watch(WatchRequest) returns (stream WatchEvent);
}

message PutRequest {
  string key = 1;
  bytes value = 2;
  int64 ttl_seconds = 3;
  map<string, string> metadata = 4;
}

message PutResponse {
  bool success = 1;
  string message = 2;
  google.protobuf.Timestamp timestamp = 3;
}

message GetRequest {
  string key = 1;
  bool include_metadata = 2;
}

message GetResponse {
  bytes value = 1;
  bool found = 2;
  map<string, string> metadata = 3;
  google.protobuf.Timestamp created_at = 4;
  google.protobuf.Timestamp updated_at = 5;
}

message DeleteRequest {
  string key = 1;
}

message DeleteResponse {
  bool success = 1;
  string message = 2;
}

message ListRequest {
  string prefix = 1;
  int32 limit = 2;
  string start_key = 3;
}

message KeyValue {
  string key = 1;
  bytes value = 2;
  map<string, string> metadata = 3;
  google.protobuf.Timestamp updated_at = 4;
}

message WatchRequest {
  string key = 1;
  string prefix = 2;
}

message WatchEvent {
  EventType type = 1;
  string key = 2;
  bytes value = 3;
  google.protobuf.Timestamp timestamp = 4;
}

enum EventType {
  UNKNOWN = 0;
  PUT = 1;
  DELETE = 2;
}
```

### 7.3 配置管理

```protobuf
syntax = "proto3";

package config;

import "google/protobuf/timestamp.proto";

// 配置管理服务
service ConfigService {
  rpc GetConfig(GetConfigRequest) returns (GetConfigResponse);
  rpc SetConfig(SetConfigRequest) returns (SetConfigResponse);
  rpc DeleteConfig(DeleteConfigRequest) returns (DeleteConfigResponse);
  rpc ListConfigs(ListConfigsRequest) returns (ListConfigsResponse);
  rpc WatchConfig(WatchConfigRequest) returns (stream ConfigChange);
}

message GetConfigRequest {
  string key = 1;
  string environment = 2;
  string version = 3;
}

message GetConfigResponse {
  ConfigValue value = 1;
  bool found = 2;
  ConfigMetadata metadata = 3;
}

message SetConfigRequest {
  string key = 1;
  ConfigValue value = 2;
  string environment = 3;
  string description = 4;
}

message SetConfigResponse {
  bool success = 1;
  string message = 2;
  ConfigMetadata metadata = 3;
}

message ConfigValue {
  oneof value {
    string string_value = 1;
    int32 int_value = 2;
    double float_value = 3;
    bool bool_value = 4;
    bytes bytes_value = 5;
    string json_value = 6;
  }
}

message ConfigMetadata {
  string key = 1;
  string environment = 2;
  string version = 3;
  string description = 4;
  string created_by = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
  map<string, string> tags = 8;
}

message DeleteConfigRequest {
  string key = 1;
  string environment = 2;
}

message DeleteConfigResponse {
  bool success = 1;
  string message = 2;
}

message ListConfigsRequest {
  string environment = 1;
  string prefix = 2;
  int32 limit = 3;
  string start_key = 4;
}

message ListConfigsResponse {
  repeated ConfigMetadata configs = 1;
  int32 total_count = 2;
}

message WatchConfigRequest {
  string key = 1;
  string environment = 2;
}

message ConfigChange {
  ChangeType type = 1;
  ConfigMetadata metadata = 2;
  ConfigValue old_value = 3;
  ConfigValue new_value = 4;
  google.protobuf.Timestamp timestamp = 5;
}

enum ChangeType {
  UNKNOWN = 0;
  CREATED = 1;
  UPDATED = 2;
  DELETED = 3;
}
```

## 8. 参考文献

### 8.1 官方文档

- [Protocol Buffers Developer Guide](https://developers.google.com/protocol-buffers/docs/overview)
- [gRPC Documentation](https://grpc.io/docs/)
- [Protocol Buffers Language Guide](https://developers.google.com/protocol-buffers/docs/proto3)

### 8.2 工具文档

- [buf Documentation](https://docs.buf.build/)
- [grpcurl Documentation](https://github.com/fullstorydev/grpcurl)
- [protoc Documentation](https://developers.google.com/protocol-buffers/docs/reference/cpp/google.protobuf.compiler)

### 8.3 最佳实践

- [Protocol Buffers Best Practices](https://developers.google.com/protocol-buffers/docs/practices)
- [gRPC Best Practices](https://grpc.io/docs/guides/best-practices/)
- [API Design with Protocol Buffers](https://developers.google.com/protocol-buffers/docs/design)

### 8.4 相关技术

- [HTTP/2 Specification](https://httpwg.org/specs/rfc7540.html)
- [JSON-RPC](https://www.jsonrpc.org/)
- [REST API Design](https://restfulapi.net/)

---

**最后更新**: 2025年01月
