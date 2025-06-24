# 在Kubernetes中使用OpenAPI定义CRD

Kubernetes 允许用户通过**自定义资源定义（Custom Resource Definition, CRD）**来扩展其API。CRD 的核心是其 Schema（模式），它定义了自定义资源的结构和字段。Kubernetes 使用 **OpenAPI v3 Schema** 来定义和验证这些自定义资源，这使得 Kubernetes API 成为 OpenAPI 规范在大型分布式系统中成功应用的典范。

本节将展示如何在一个CRD中嵌入OpenAPI Schema，并利用它来实现API对象的验证和版本管理。

## 1. CRD中的OpenAPI Schema

在CRD的`.spec.versions`字段中，每一个版本都可以内嵌一个`openAPIV3Schema`。这个schema定义了该版本自定义资源的结构、类型和验证规则。

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  # 名称必须符合 <plural>.<group> 的格式
  name: mycrds.example.com
spec:
  # group 和 names 用于在API中标识资源
  group: example.com
  names:
    plural: mycrds
    singular: mycrd
    kind: MyCRD
    shortNames:
    - mc
  # scope 可以是 Namespaced 或 Cluster
  scope: Namespaced
  
  versions:
    - name: v1
      # served 表示此版本是否通过API服务器提供服务
      served: true
      # storage 表示此版本是存储在etcd中的版本
      storage: true
      # additionalPrinterColumns 可以在 `kubectl get` 时显示额外列
      additionalPrinterColumns:
      - name: Replicas
        type: integer
        description: The number of desired replicas
        jsonPath: .spec.replicas
      - name: Age
        type: date
        jsonPath: .metadata.creationTimestamp
        
      # subresources 允许启用 /status 和 /scale 子资源
      subresources:
        status: {} # 启用 /status 子资源

      # OpenAPI v3 Schema 定义了资源的结构和验证规则
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
                  description: "副本数量，必须是正数"
                  minimum: 1
                image:
                  type: string
                  description: "要部署的容器镜像"
              required:
              - image
              - replicas
            status:
              type: object
              properties:
                availableReplicas:
                  type: integer
                  description: "当前可用的副本数量"
```

## 2. Schema如何实现验证

当用户尝试创建或更新一个`MyCRD`资源时，Kubernetes API Server会使用上面定义的`openAPIV3Schema`来验证提交的YAML/JSON对象：

-   **类型检查**: 确保`spec.replicas`是一个整数，`spec.image`是一个字符串。
-   **必需字段**: 检查`spec.image`和`spec.replicas`字段是否存在。
-   **值约束**: 验证`spec.replicas`的值是否大于等于1（`minimum: 1`）。
-   **结构完整性**: 确保只有在`spec`和`status`中定义的字段才被接受（除非配置了`x-kubernetes-preserve-unknown-fields`）。

如果验证失败，API Server将拒绝该请求并返回一个描述错误的详细信息。

## 3. 使用Schema支持API演进

CRD还支持在`versions`列表中定义多个版本的schema。这使得API可以随着时间平滑演进。

```yaml
# ... CRD 定义 ...
spec:
  # ...
  versions:
    - name: v1alpha1
      served: true
      storage: false # v1alpha1 不是存储版本
      schema:
        openAPIV3Schema:
          # ... v1alpha1 的 schema 定义 ...
    - name: v1
      served: true
      storage: true  # v1 是存储版本
      schema:
        openAPIV3Schema:
          # ... v1 的 schema 定义 ...
  
  # 定义版本间转换的策略
  conversion:
    strategy: Webhook # 或 None
    # ... webhook 配置 ...
```

在这个例子中：
-   Kubernetes API Server 会同时提供`v1alpha1`和`v1`两个版本的API端点。
-   所有`MyCRD`对象都将以`v1`版本的schema格式存储在etcd中（因为`storage: true`）。
-   当用户向`v1alpha1`端点写入数据时，可以通过一个**Conversion Webhook**自动将`v1alpha1`格式的对象转换为`v1`格式再进行存储。
-   当用户从`v1alpha1`端点读取数据时，Webhook会将存储的`v1`对象转换回`v1alpha1`格式再返回给用户。

这种机制充分利用了OpenAPI Schema的强大能力，为分布式系统的API提供了健壮的验证、清晰的文档和灵活的演进路径。 