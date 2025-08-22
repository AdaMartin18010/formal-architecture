# 2. 在Kubernetes中使用OpenAPI定义CRD

## 目录

- [2. 在Kubernetes中使用OpenAPI定义CRD](#2-在kubernetes中使用openapi定义crd)
  - [目录](#目录)
  - [1. 引言与背景](#1-引言与背景)
    - [1.1 CRD与OpenAPI的关系](#11-crd与openapi的关系)
    - [1.2 Kubernetes API扩展的价值](#12-kubernetes-api扩展的价值)
  - [2. CRD基础概念](#2-crd基础概念)
    - [2.1 自定义资源定义结构](#21-自定义资源定义结构)
    - [2.2 OpenAPI v3 Schema集成](#22-openapi-v3-schema集成)
    - [2.3 版本管理与演进](#23-版本管理与演进)
  - [3. 核心功能与特性](#3-核心功能与特性)
    - [3.1 类型验证与约束](#31-类型验证与约束)
    - [3.2 默认值与计算字段](#32-默认值与计算字段)
    - [3.3 子资源支持](#33-子资源支持)
    - [3.4 打印列配置](#34-打印列配置)
  - [4. 高级模式与最佳实践](#4-高级模式与最佳实践)
    - [4.1 复杂Schema设计](#41-复杂schema设计)
    - [4.2 验证规则配置](#42-验证规则配置)
    - [4.3 版本转换策略](#43-版本转换策略)
    - [4.4 性能优化](#44-性能优化)
  - [5. 工具链与自动化](#5-工具链与自动化)
    - [5.1 代码生成工具](#51-代码生成工具)
    - [5.2 验证与测试](#52-验证与测试)
    - [5.3 CI/CD集成](#53-cicd集成)
  - [6. 实际应用案例](#6-实际应用案例)
    - [6.1 微服务部署CRD](#61-微服务部署crd)
    - [6.2 数据库配置CRD](#62-数据库配置crd)
    - [6.3 监控告警CRD](#63-监控告警crd)
  - [7. 故障排除与调试](#7-故障排除与调试)
    - [7.1 常见问题](#71-常见问题)
    - [7.2 调试技巧](#72-调试技巧)
  - [8. 参考文献](#8-参考文献)
    - [8.1 官方文档](#81-官方文档)
    - [8.2 工具文档](#82-工具文档)
    - [8.3 最佳实践](#83-最佳实践)
    - [8.4 相关技术](#84-相关技术)

---

## 1. 引言与背景

Kubernetes 允许用户通过**自定义资源定义（Custom Resource Definition, CRD）**来扩展其API。
CRD 的核心是其 Schema（模式），它定义了自定义资源的结构和字段。
Kubernetes 使用 **OpenAPI v3 Schema** 来定义和验证这些自定义资源，
这使得 Kubernetes API 成为 OpenAPI 规范在大型分布式系统中成功应用的典范。

### 1.1 CRD与OpenAPI的关系

CRD是Kubernetes API扩展的机制，而OpenAPI Schema是定义这些扩展资源结构的标准方式：

- **CRD**: 定义新的资源类型和API端点
- **OpenAPI Schema**: 定义资源的数据结构和验证规则
- **集成优势**: 统一的验证、文档和工具支持

### 1.2 Kubernetes API扩展的价值

通过CRD扩展Kubernetes API的价值：

- **声明式配置**: 使用YAML/JSON定义复杂应用状态
- **类型安全**: 编译时和运行时类型检查
- **工具集成**: 与kubectl、Helm等工具无缝集成
- **生态系统**: 利用Kubernetes的监控、RBAC、审计等能力

## 2. CRD基础概念

### 2.1 自定义资源定义结构

CRD的基本结构包含元数据、规范定义和版本管理：

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: mycrds.example.com
  annotations:
    description: "自定义资源定义示例"
spec:
  group: example.com
  names:
    plural: mycrds
    singular: mycrd
    kind: MyCRD
    shortNames:
    - mc
    categories:
    - all
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          # OpenAPI Schema定义
```

### 2.2 OpenAPI v3 Schema集成

在CRD的`.spec.versions`字段中，每一个版本都可以内嵌一个`openAPIV3Schema`。这个schema定义了该版本自定义资源的结构、类型和验证规则。

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: mycrds.example.com
spec:
  group: example.com
  names:
    plural: mycrds
    singular: mycrd
    kind: MyCRD
    shortNames:
    - mc
  scope: Namespaced
  
  versions:
    - name: v1
      served: true
      storage: true
      additionalPrinterColumns:
      - name: Replicas
        type: integer
        description: The number of desired replicas
        jsonPath: .spec.replicas
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
        
      subresources:
        status: {}
        scale:
          specReplicasPath: .spec.replicas
          statusReplicasPath: .status.replicas

      schema:
        openAPIV3Schema:
          type: object
          required:
          - spec
          properties:
            spec:
              type: object
              required:
              - image
              - replicas
              properties:
                replicas:
                  type: integer
                  description: "副本数量，必须是正数"
                  minimum: 1
                  maximum: 100
                  default: 1
                image:
                  type: string
                  description: "要部署的容器镜像"
                  pattern: '^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]/[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9](:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$'
                resources:
                  type: object
                  properties:
                    requests:
                      type: object
                      properties:
                        cpu:
                          type: string
                          pattern: '^([0-9]+m?|[0-9]*\.[0-9]+)$'
                        memory:
                          type: string
                          pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                    limits:
                      type: object
                      properties:
                        cpu:
                          type: string
                          pattern: '^([0-9]+m?|[0-9]*\.[0-9]+)$'
                        memory:
                          type: string
                          pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                ports:
                  type: array
                  items:
                    type: object
                    required:
                    - port
                    properties:
                      port:
                        type: integer
                        minimum: 1
                        maximum: 65535
                      protocol:
                        type: string
                        enum:
                        - TCP
                        - UDP
                        default: TCP
                      name:
                        type: string
                        pattern: '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
            status:
              type: object
              properties:
                availableReplicas:
                  type: integer
                  description: "当前可用的副本数量"
                  minimum: 0
                conditions:
                  type: array
                  items:
                    type: object
                    required:
                    - type
                    - status
                    properties:
                      type:
                        type: string
                        enum:
                        - Available
                        - Progressing
                        - Degraded
                      status:
                        type: string
                        enum:
                        - True
                        - False
                        - Unknown
                      lastTransitionTime:
                        type: string
                        format: date-time
                      reason:
                        type: string
                      message:
                        type: string
```

### 2.3 版本管理与演进

CRD支持多版本定义，实现API的平滑演进：

```yaml
spec:
  versions:
    - name: v1alpha1
      served: true
      storage: false
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
                  minimum: 1
                image:
                  type: string
                # v1alpha1 特有的字段
                experimentalFeature:
                  type: boolean
                  default: false
    - name: v1beta1
      served: true
      storage: false
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
                  minimum: 1
                image:
                  type: string
                # v1beta1 改进的字段
                resources:
                  type: object
                  properties:
                    requests:
                      type: object
                    limits:
                      type: object
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          # 完整的v1 schema定义
  
  conversion:
    strategy: Webhook
    webhook:
      clientConfig:
        service:
          namespace: default
          name: my-crd-conversion-webhook
          path: /convert
          port: 443
      conversionReviewVersions:
      - v1
```

## 3. 核心功能与特性

### 3.1 类型验证与约束

OpenAPI Schema提供强大的类型验证能力：

```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          # 字符串验证
          name:
            type: string
            minLength: 1
            maxLength: 63
            pattern: '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
          
          # 数值验证
          port:
            type: integer
            minimum: 1
            maximum: 65535
            multipleOf: 1
          
          # 枚举验证
          protocol:
            type: string
            enum:
            - HTTP
            - HTTPS
            - TCP
            - UDP
          
          # 数组验证
          tags:
            type: array
            minItems: 0
            maxItems: 10
            uniqueItems: true
            items:
              type: string
              maxLength: 50
          
          # 对象验证
          config:
            type: object
            additionalProperties: false
            properties:
              timeout:
                type: integer
                minimum: 1
              retries:
                type: integer
                minimum: 0
                maximum: 10
```

### 3.2 默认值与计算字段

支持默认值和计算字段：

```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          replicas:
            type: integer
            minimum: 1
            default: 1
          strategy:
            type: string
            enum:
            - RollingUpdate
            - Recreate
            default: RollingUpdate
          rollingUpdate:
            type: object
            properties:
              maxUnavailable:
                type: string
                default: "25%"
              maxSurge:
                type: string
                default: "25%"
```

### 3.3 子资源支持

启用status和scale子资源：

```yaml
subresources:
  status: {}
  scale:
    specReplicasPath: .spec.replicas
    statusReplicasPath: .status.replicas
    labelSelectorPath: .status.labelSelector
```

### 3.4 打印列配置

自定义kubectl get的输出：

```yaml
additionalPrinterColumns:
- name: Replicas
  type: integer
  description: The number of desired replicas
  jsonPath: .spec.replicas
- name: Available
  type: integer
  description: The number of available replicas
  jsonPath: .status.availableReplicas
- name: Age
  type: date
  jsonPath: .metadata.creationTimestamp
- name: Status
  type: string
  description: The current status
  jsonPath: .status.conditions[?(@.type=="Available")].status
```

## 4. 高级模式与最佳实践

### 4.1 复杂Schema设计

处理复杂的嵌套结构：

```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          # 使用oneOf进行条件验证
          deployment:
            oneOf:
            - required: [image, replicas]
            - required: [image, autoscaling]
            properties:
              image:
                type: string
              replicas:
                type: integer
                minimum: 1
              autoscaling:
                type: object
                properties:
                  minReplicas:
                    type: integer
                    minimum: 1
                  maxReplicas:
                    type: integer
                    minimum: 1
                  targetCPUUtilizationPercentage:
                    type: integer
                    minimum: 1
                    maximum: 100
          
          # 使用allOf组合多个schema
          security:
            allOf:
            - $ref: '#/components/schemas/SecurityContext'
            - type: object
              properties:
                runAsNonRoot:
                  type: boolean
                  default: true
          
          # 使用anyOf允许多种类型
          volumeMounts:
            type: array
            items:
              anyOf:
              - $ref: '#/components/schemas/ConfigMapVolumeMount'
              - $ref: '#/components/schemas/SecretVolumeMount'
              - $ref: '#/components/schemas/EmptyDirVolumeMount'
    
    # 定义可重用的schema组件
    components:
      schemas:
        SecurityContext:
          type: object
          properties:
            runAsUser:
              type: integer
              minimum: 0
            runAsGroup:
              type: integer
              minimum: 0
            fsGroup:
              type: integer
              minimum: 0
        
        ConfigMapVolumeMount:
          type: object
          required: [name, mountPath]
          properties:
            name:
              type: string
            mountPath:
              type: string
            readOnly:
              type: boolean
              default: true
```

### 4.2 验证规则配置

使用Kubernetes 1.25+的验证规则：

```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          replicas:
            type: integer
            minimum: 1
            maximum: 100
          resources:
            type: object
            properties:
              requests:
                type: object
                properties:
                  cpu:
                    type: string
                  memory:
                    type: string
              limits:
                type: object
                properties:
                  cpu:
                    type: string
                  memory:
                    type: string
            x-kubernetes-validations:
            - rule: "self.limits.cpu >= self.requests.cpu"
              message: "CPU limit must be greater than or equal to CPU request"
            - rule: "self.limits.memory >= self.requests.memory"
              message: "Memory limit must be greater than or equal to memory request"
```

### 4.3 版本转换策略

实现版本间的自动转换：

```yaml
conversion:
  strategy: Webhook
  webhook:
    clientConfig:
      service:
        namespace: default
        name: my-crd-conversion-webhook
        path: /convert
        port: 443
    conversionReviewVersions:
    - v1
    - v1beta1
```

### 4.4 性能优化

优化CRD性能的最佳实践：

```yaml
# 1. 使用preserveUnknownFields减少验证开销
spec:
  versions:
    - name: v1
      schema:
        openAPIV3Schema:
          x-kubernetes-preserve-unknown-fields: true

# 2. 合理使用required字段
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        # 只在真正必需的字段上使用required
        required: [image]
        properties:
          image:
            type: string

# 3. 避免过深的嵌套
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          # 扁平化设计，避免过深嵌套
          configMapName:
            type: string
          secretName:
            type: string
          # 而不是 config.data.configMapName
```

## 5. 工具链与自动化

### 5.1 代码生成工具

使用kubebuilder和code-generator：

```bash
# 安装kubebuilder
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)
chmod +x kubebuilder && mv kubebuilder /usr/local/bin/

# 初始化项目
kubebuilder init --domain example.com --repo github.com/example/my-operator
kubebuilder create api --group apps --version v1 --kind MyApp

# 生成代码
make manifests
make generate
```

### 5.2 验证与测试

使用工具验证CRD：

```bash
# 使用kubeval验证
kubeval my-crd.yaml

# 使用kustomize验证
kustomize build . | kubectl apply --dry-run=client -f -

# 使用conftest进行策略验证
conftest verify --policy policies/ --data my-crd.yaml
```

### 5.3 CI/CD集成

GitHub Actions工作流示例：

```yaml
name: CRD Validation

on:
  push:
    paths:
      - 'crd/**'
  pull_request:
    paths:
      - 'crd/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Go
        uses: actions/setup-go@v3
        with:
          go-version: '1.19'
      
      - name: Install tools
        run: |
          go install sigs.k8s.io/kubebuilder/cmd/kubebuilder@latest
          go install github.com/instrumenta/kubeval@latest
      
      - name: Validate CRD
        run: |
          for file in crd/*.yaml; do
            kubeval "$file"
          done
      
      - name: Test CRD
        run: |
          kubectl apply --dry-run=client -f crd/
```

## 6. 实际应用案例

### 6.1 微服务部署CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: microservices.apps.example.com
spec:
  group: apps.example.com
  names:
    plural: microservices
    singular: microservice
    kind: Microservice
    shortNames:
    - ms
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      additionalPrinterColumns:
      - name: Replicas
        type: integer
        jsonPath: .spec.replicas
      - name: Status
        type: string
        jsonPath: .status.phase
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
      
      subresources:
        status: {}
        scale:
          specReplicasPath: .spec.replicas
          statusReplicasPath: .status.replicas
      
      schema:
        openAPIV3Schema:
          type: object
          required: [spec]
          properties:
            spec:
              type: object
              required: [image, replicas]
              properties:
                image:
                  type: string
                  description: "容器镜像"
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 100
                  default: 1
                resources:
                  type: object
                  properties:
                    requests:
                      type: object
                      properties:
                        cpu:
                          type: string
                          pattern: '^([0-9]+m?|[0-9]*\.[0-9]+)$'
                        memory:
                          type: string
                          pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                    limits:
                      type: object
                      properties:
                        cpu:
                          type: string
                          pattern: '^([0-9]+m?|[0-9]*\.[0-9]+)$'
                        memory:
                          type: string
                          pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                ports:
                  type: array
                  items:
                    type: object
                    required: [port]
                    properties:
                      port:
                        type: integer
                        minimum: 1
                        maximum: 65535
                      protocol:
                        type: string
                        enum: [TCP, UDP]
                        default: TCP
                      name:
                        type: string
                        pattern: '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
                env:
                  type: array
                  items:
                    type: object
                    required: [name]
                    properties:
                      name:
                        type: string
                        pattern: '^[A-Z_][A-Z0-9_]*$'
                      value:
                        type: string
                      valueFrom:
                        type: object
                        properties:
                          configMapKeyRef:
                            type: object
                            required: [name, key]
                            properties:
                              name:
                                type: string
                              key:
                                type: string
                          secretKeyRef:
                            type: object
                            required: [name, key]
                            properties:
                              name:
                                type: string
                              key:
                                type: string
                volumes:
                  type: array
                  items:
                    type: object
                    required: [name]
                    properties:
                      name:
                        type: string
                        pattern: '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
                      configMap:
                        type: object
                        properties:
                          name:
                            type: string
                      secret:
                        type: object
                        properties:
                          secretName:
                            type: string
                      emptyDir:
                        type: object
                        properties:
                          medium:
                            type: string
                            enum: [Memory, ""]
                          sizeLimit:
                            type: string
            status:
              type: object
              properties:
                phase:
                  type: string
                  enum: [Pending, Running, Succeeded, Failed]
                replicas:
                  type: integer
                  minimum: 0
                availableReplicas:
                  type: integer
                  minimum: 0
                conditions:
                  type: array
                  items:
                    type: object
                    required: [type, status]
                    properties:
                      type:
                        type: string
                        enum: [Available, Progressing, Degraded]
                      status:
                        type: string
                        enum: [True, False, Unknown]
                      lastTransitionTime:
                        type: string
                        format: date-time
                      reason:
                        type: string
                      message:
                        type: string
```

### 6.2 数据库配置CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: databases.data.example.com
spec:
  group: data.example.com
  names:
    plural: databases
    singular: database
    kind: Database
    shortNames:
    - db
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      additionalPrinterColumns:
      - name: Type
        type: string
        jsonPath: .spec.type
      - name: Version
        type: string
        jsonPath: .spec.version
      - name: Status
        type: string
        jsonPath: .status.phase
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
      
      subresources:
        status: {}
      
      schema:
        openAPIV3Schema:
          type: object
          required: [spec]
          properties:
            spec:
              type: object
              required: [type, version]
              properties:
                type:
                  type: string
                  enum: [MySQL, PostgreSQL, MongoDB, Redis]
                  description: "数据库类型"
                version:
                  type: string
                  description: "数据库版本"
                storage:
                  type: object
                  required: [size]
                  properties:
                    size:
                      type: string
                      pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                    storageClass:
                      type: string
                resources:
                  type: object
                  properties:
                    requests:
                      type: object
                      properties:
                        cpu:
                          type: string
                          pattern: '^([0-9]+m?|[0-9]*\.[0-9]+)$'
                        memory:
                          type: string
                          pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                    limits:
                      type: object
                      properties:
                        cpu:
                          type: string
                          pattern: '^([0-9]+m?|[0-9]*\.[0-9]+)$'
                        memory:
                          type: string
                          pattern: '^([0-9]+[KMGTPEZYkmgtpezy]i?|[0-9]*\.[0-9]+[KMGTPEZYkmgtpezy]i?)$'
                backup:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: false
                    schedule:
                      type: string
                      pattern: '^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$'
                    retention:
                      type: integer
                      minimum: 1
                      maximum: 365
                      default: 7
                monitoring:
                  type: object
                  properties:
                    enabled:
                      type: boolean
                      default: true
                    metrics:
                      type: array
                      items:
                        type: string
                        enum: [cpu, memory, disk, connections, queries]
            status:
              type: object
              properties:
                phase:
                  type: string
                  enum: [Pending, Creating, Running, Failed, Terminating]
                endpoint:
                  type: string
                port:
                  type: integer
                credentials:
                  type: object
                  properties:
                    username:
                      type: string
                    passwordSecret:
                      type: string
                conditions:
                  type: array
                  items:
                    type: object
                    required: [type, status]
                    properties:
                      type:
                        type: string
                        enum: [Ready, Available, BackupReady]
                      status:
                        type: string
                        enum: [True, False, Unknown]
                      lastTransitionTime:
                        type: string
                        format: date-time
                      reason:
                        type: string
                      message:
                        type: string
```

### 6.3 监控告警CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: alertrules.monitoring.example.com
spec:
  group: monitoring.example.com
  names:
    plural: alertrules
    singular: alertrule
    kind: AlertRule
    shortNames:
    - ar
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      additionalPrinterColumns:
      - name: Severity
        type: string
        jsonPath: .spec.severity
      - name: Enabled
        type: boolean
        jsonPath: .spec.enabled
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
      
      subresources:
        status: {}
      
      schema:
        openAPIV3Schema:
          type: object
          required: [spec]
          properties:
            spec:
              type: object
              required: [name, query, severity]
              properties:
                name:
                  type: string
                  maxLength: 63
                  pattern: '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
                description:
                  type: string
                  maxLength: 256
                query:
                  type: string
                  description: "PromQL查询表达式"
                severity:
                  type: string
                  enum: [critical, warning, info]
                enabled:
                  type: boolean
                  default: true
                for:
                  type: string
                  pattern: '^([0-9]+[smhdwy]?|[0-9]*\.[0-9]+[smhdwy]?)$'
                  default: "5m"
                labels:
                  type: object
                  additionalProperties:
                    type: string
                annotations:
                  type: object
                  additionalProperties:
                    type: string
                thresholds:
                  type: object
                  properties:
                    warning:
                      type: number
                    critical:
                      type: number
                notification:
                  type: object
                  properties:
                    channels:
                      type: array
                      items:
                        type: string
                        enum: [email, slack, webhook, pagerduty]
                    recipients:
                      type: array
                      items:
                        type: string
                        format: email
                    webhook:
                      type: object
                      properties:
                        url:
                          type: string
                          format: uri
                        method:
                          type: string
                          enum: [GET, POST, PUT]
                          default: POST
                        headers:
                          type: object
                          additionalProperties:
                            type: string
            status:
              type: object
              properties:
                lastEvaluation:
                  type: string
                  format: date-time
                firing:
                  type: boolean
                activeAlerts:
                  type: integer
                  minimum: 0
                conditions:
                  type: array
                  items:
                    type: object
                    required: [type, status]
                    properties:
                      type:
                        type: string
                        enum: [Ready, Firing, Resolved]
                      status:
                        type: string
                        enum: [True, False, Unknown]
                      lastTransitionTime:
                        type: string
                        format: date-time
                      reason:
                        type: string
                      message:
                        type: string
```

## 7. 故障排除与调试

### 7.1 常见问题

1. **Schema验证失败**

   ```bash
   # 检查CRD状态
   kubectl get crd mycrds.example.com -o yaml
   
   # 查看详细错误
   kubectl describe crd mycrds.example.com
   ```

2. **版本转换问题**

   ```bash
   # 检查webhook状态
   kubectl get validatingwebhookconfigurations
   kubectl get mutatingwebhookconfigurations
   
   # 查看webhook日志
   kubectl logs -n default deployment/my-crd-conversion-webhook
   ```

3. **性能问题**

   ```bash
   # 检查API Server资源使用
   kubectl top pods -n kube-system | grep api-server
   
   # 查看API Server日志
   kubectl logs -n kube-system kube-apiserver-$(hostname)
   ```

### 7.2 调试技巧

```bash
# 1. 使用--dry-run验证
kubectl apply --dry-run=client -f my-crd.yaml

# 2. 使用--validate=false跳过验证
kubectl apply --validate=false -f my-crd.yaml

# 3. 使用kubectl explain查看字段说明
kubectl explain mycrd.spec

# 4. 使用kubectl get --show-labels查看标签
kubectl get mycrd --show-labels

# 5. 使用kubectl describe查看详细信息
kubectl describe mycrd my-instance
```

## 8. 参考文献

### 8.1 官方文档

- [Kubernetes CRD Documentation](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
- [OpenAPI v3 Specification](https://spec.openapis.org/oas/v3.0.3)
- [Kubernetes API Conventions](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md)

### 8.2 工具文档

- [Kubebuilder Book](https://book.kubebuilder.io/)
- [Kubernetes Code Generator](https://github.com/kubernetes/code-generator)
- [kubeval - CRD Validation](https://github.com/instrumenta/kubeval)

### 8.3 最佳实践

- [Kubernetes API Design Guidelines](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md)
- [CRD Best Practices](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/#specifying-a-structural-schema)
- [OpenAPI Schema Best Practices](https://swagger.io/docs/specification/data-models/)

### 8.4 相关技术

- [Kubernetes Operators](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [Kubernetes Admission Controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Kubernetes API Server](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)

---

**最后更新**: 2025年01月
