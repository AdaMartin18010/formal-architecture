# Rust图形与底层开发：Wgpu与Vulkan

Rust 凭借其性能、内存安全和对底层的精细控制，在图形编程和底层开发领域表现出色。`wgpu`提供了一个现代、跨平台的图形API抽象，而`ash`等库则提供了对Vulkan等底层API的直接绑定。

## `wgpu`：现代跨平台图形API

`wgpu`是基于WebGPU API标准的纯Rust实现，它可以在Vulkan、Metal、DirectX 12/11和OpenGL上运行，为开发者提供了一个统一、安全的图形编程接口。

```rust
// 一个简化的wgpu初始化和渲染管线示例
// 依赖：wgpu = "0.13", pollster = "0.2"

use wgpu::util::DeviceExt;

async fn wgpu_example() {
    // 初始化wgpu
    let instance = wgpu::Instance::new(wgpu::Backends::all());
    let adapter = instance
        .request_adapter(&wgpu::RequestAdapterOptions::default())
        .await
        .unwrap();
    
    let (device, queue) = adapter
        .request_device(
            &wgpu::DeviceDescriptor {
                features: wgpu::Features::empty(),
                limits: wgpu::Limits::default(),
                label: None,
            },
            None,
        )
        .await
        .unwrap();

    // 加载WGSL着色器代码
    let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
        label: Some("Shader"),
        source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
    });

    // 创建渲染管线
    let render_pipeline_layout =
        device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("Render Pipeline Layout"),
            bind_group_layouts: &[],
            push_constant_ranges: &[],
        });

    let render_pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
        label: Some("Render Pipeline"),
        layout: Some(&render_pipeline_layout),
        vertex: wgpu::VertexState {
            module: &shader,
            entry_point: "vs_main",
            buffers: &[],
        },
        fragment: Some(wgpu::FragmentState {
            module: &shader,
            entry_point: "fs_main",
            targets: &[Some(wgpu::ColorTargetState {
                format: wgpu::TextureFormat::Bgra8UnormSrgb, // 假设这是交换链的格式
                blend: Some(wgpu::BlendState::REPLACE),
                write_mask: wgpu::ColorWrites::ALL,
            })],
        }),
        primitive: wgpu::PrimitiveState::default(),
        depth_stencil: None,
        multisample: wgpu::MultisampleState::default(),
        multiview: None,
    });
    
    // 后续需要设置交换链、顶点缓冲、绘制指令等来完成渲染...
}
```

```wgsl
// file: shader.wgsl
@vertex
fn vs_main(@builtin(vertex_index) in_vertex_index: u32) -> @builtin(position) vec4<f32> {
    var pos = array<vec2<f32>, 3>(
        vec2<f32>(0.0, 0.5),
        vec2<f32>(-0.5, -0.5),
        vec2<f32>(0.5, -0.5)
    );
    
    return vec4<f32>(pos[in_vertex_index], 0.0, 1.0);
}

@fragment
fn fs_main() -> @location(0) vec4<f32> {
    return vec4<f32>(1.0, 0.0, 0.0, 1.0);
}
```

## `ash`：Vulkan的底层绑定

对于需要极致性能和控制的场景，可以直接使用`ash`库来操作Vulkan API。

```rust
// 使用ash库初始化Vulkan实例的示例
// 依赖: ash = "0.37"
use ash::{vk, Entry, Instance};
use std::ffi::CString;

fn vulkan_example() -> Result<(), Box<dyn std::error::Error>> {
    // 初始化Vulkan
    let entry = Entry::linked();
    
    // 创建实例
    let app_name = CString::new("Rust Vulkan App")?;
    let engine_name = CString::new("No Engine")?;
    
    let app_info = vk::ApplicationInfo::builder()
        .application_name(&app_name)
        .application_version(vk::make_api_version(0, 1, 0, 0))
        .engine_name(&engine_name)
        .engine_version(vk::make_api_version(0, 1, 0, 0))
        .api_version(vk::make_api_version(0, 1, 0, 0));
    
    let layer_names = [CString::new("VK_LAYER_KHRONOS_validation")?];
    let layer_name_ptrs: Vec<*const i8> = layer_names
        .iter()
        .map(|name| name.as_ptr())
        .collect();
    
    let instance_create_info = vk::InstanceCreateInfo::builder()
        .application_info(&app_info)
        .enabled_layer_names(&layer_name_ptrs);
    
    let instance = unsafe { entry.create_instance(&instance_create_info, None)? };
    
    // 列出物理设备
    let physical_devices = unsafe { instance.enumerate_physical_devices()? };
    println!("找到 {} 个物理设备", physical_devices.len());
    
    // 清理资源
    unsafe {
        instance.destroy_instance(None);
    }
    
    Ok(())
}
```

## Rust图形和渲染生态

- **wgpu**: 跨平台图形API
- **gfx-rs**: 低级图形抽象
- **ash**: Vulkan绑定
- **gl**: OpenGL绑定
- **metal-rs**: Metal绑定
- **luminance**: 类型安全图形框架
- **rend3**: 3D渲染器
- **vello**: 2D渲染器
- **raqote**: 软件渲染器
- **pixels**: 像素缓冲区
- **egui**: 即时模式GUI
- **winit**: 窗口处理
- **glam**: 图形数学库
- **nalgebra**: 数学库
