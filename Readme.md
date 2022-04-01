# CompositeBridge

[![CN doc](https://img.shields.io/badge/文档-中文版-blue.svg)](README.md)


## 简介
CompositeBridge 是一个计算钢混组合梁的参数化工具。用于简化组合梁结构体系的建模过程，并应用于一些参数分析研究。

## 特点

- [x] 组合梁的参数化定义；
- [x] 组合梁的一维有限元模型生成和计算；
- [x] 组合梁的三维有限元模型生成；
- [x] 车道荷载的计算；
- [x] Mechanical的Batch Mode 调用；
- [ ] 还有什么？

## 示例

1. 导入有关包库。

   ```python
   from src.CompositeBridge import CompositeBridge
   from src.CompositeBridge import CrossArrangement, Span
   from src.CompositeBridge import Material, ShellSection, ISection
   ```
   
2. 配置跨径信息和截面布置。

   ```python
   g1 = [1.2] + [4, ] * 3 + [1.2]
   g2 = [1.2 + 2] + [4, ] * 2 + [2 + 1.2]
   ca = CrossArrangement(sum(g1), g1, g2, 0.25, 0.05, 0.3, 1.0)
   span1 = Span(0)
   span2 = Span(32)
   span3 = Span(68)
   span4 = Span(115)
   sps = [span1, span2, span3, span4]
   ```

3. 生成组合梁模型。

   ```python
   Bridge = CompositeBridge(sps, ca)
   ```

4. 配置材料——钢材、混凝土、刚性连接，并指定给模型

   ```python
   m1 = Material(1, 206000e6, 7850, 1.2e5, 0.3, 'Q420')
   m2 = Material(2, 206000e6, 7850, 1.2e5, 0.3, 'Q345')
   m3 = Material(3, 34500e6, 2500, 1.1e5, 0.2, 'Concrete')
   m184 = Material(184, 0, 0, 0, 0, 'MP184')
   
   Bridge.add_material(m1)
   Bridge.add_material(m2)
   Bridge.add_material(m3)
   Bridge.add_material(m184)
   ```

5. 配置截面，并指定给模型

   ```python
   s1 = ShellSection(1, 'T250', th=0.250, offset=(0, 0.25 * 0.5 + 0.05))
   s2 = ISection(2, "I2000", offset=(0, 1), 
                 w1=0.6, w2=0.6, w3=2.0, t1=0.060, t2=0.060, t3=0.020)
   s3 = ISection(3, "I300", offset=(0, 0.15), 
                 w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
   s4 = ISection(4, "I300", offset=(0, 0.3), 
                 w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
   s5 = ISection(5, "I300", offset=(0, 0.3), 
                 w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
   s6 = ISection(6, "I300", offset=(0, 0.2), 
                 w1=0.15, w2=0.15, w3=0.2, t1=0.010, t2=0.010, t3=0.008)
   
   Bridge.add_section(s1)
   Bridge.add_section(s2)
   Bridge.add_section(s3)
   Bridge.add_section(s4)
   Bridge.add_section(s5)
   Bridge.add_section(s6)
   ```

7. 有限元化，指定网格尺寸，配置车道，并写出数据库。

   ```python
   Bridge.generate_fem(2, 0.5)
   Bridge.def_lane_gb(loc=[4.2, 10, 12])  # 定义车道横向位置（左侧护栏外缘为0）
   Bridge.write_database(path=r".\bin\Model", projectname="TestModelA")
   ```

7. 执行运算

   ```python
   Bridge.run_ansys(path=r".\bin\Model")
   ```

   
