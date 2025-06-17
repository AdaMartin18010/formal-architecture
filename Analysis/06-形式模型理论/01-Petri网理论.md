# 01-Petri网理论

## 目录

1. [1.0 Petri网基础](#10-petri网基础)
2. [2.0 Petri网结构](#20-petri网结构)
3. [3.0 可达性分析](#30-可达性分析)
4. [4.0 死锁检测](#40-死锁检测)
5. [5.0 不变性分析](#50-不变性分析)
6. [6.0 性能分析](#60-性能分析)
7. [7.0 高级Petri网](#70-高级petri网)
8. [8.0 实践应用](#80-实践应用)

## 1.0 Petri网基础

### 1.1 Petri网定义

**定义 1.1.1 (Petri网)**
Petri网是一个四元组 $N = (P, T, F, M_0)$，其中：

- $P$ 是库所集合 (Places)
- $T$ 是变迁集合 (Transitions)
- $F \subseteq (P \times T) \cup (T \times P)$ 是流关系 (Flow Relation)
- $M_0: P \to \mathbb{N}$ 是初始标识 (Initial Marking)

**定义 1.1.2 (标识)**
标识是一个函数 $M: P \to \mathbb{N}$，表示每个库所中的托肯数量。

**定义 1.1.3 (前集和后集)**
对于节点 $x \in P \cup T$：
- 前集：$^\bullet x = \{y \mid (y, x) \in F\}$
- 后集：$x^\bullet = \{y \mid (x, y) \in F\}$

### 1.2 发射规则

**定义 1.2.1 (变迁使能)**
变迁 $t \in T$ 在标识 $M$ 下使能，记为 $M[t>$，当且仅当：
$$\forall p \in ^\bullet t: M(p) \geq F(p, t)$$

**定义 1.2.2 (变迁发射)**
如果 $M[t>$，则变迁 $t$ 可以发射，产生新标识 $M'$，记为 $M[t>M'$，其中：
$$M'(p) = M(p) - F(p, t) + F(t, p)$$

**定义 1.2.3 (发射序列)**
发射序列是一个变迁序列 $\sigma = t_1t_2\ldots t_n$，使得：
$$M_0[t_1>M_1[t_2>M_2\ldots[t_n>M_n$$

```rust
// Rust实现：Petri网基础
#[derive(Debug, Clone)]
pub struct PetriNet {
    pub places: Vec<Place>,
    pub transitions: Vec<Transition>,
    pub flow_relation: HashMap<(String, String), u32>,
    pub initial_marking: HashMap<String, u32>,
}

#[derive(Debug, Clone)]
pub struct Place {
    pub id: String,
    pub name: String,
    pub capacity: Option<u32>,
}

#[derive(Debug, Clone)]
pub struct Transition {
    pub id: String,
    pub name: String,
    pub guard: Option<Guard>,
}

#[derive(Debug, Clone)]
pub enum Guard {
    Always,
    Condition(Box<dyn Fn(&HashMap<String, u32>) -> bool>),
}

impl PetriNet {
    pub fn new() -> Self {
        PetriNet {
            places: Vec::new(),
            transitions: Vec::new(),
            flow_relation: HashMap::new(),
            initial_marking: HashMap::new(),
        }
    }
    
    pub fn add_place(&mut self, id: String, name: String, capacity: Option<u32>) {
        self.places.push(Place { id: id.clone(), name, capacity });
        self.initial_marking.insert(id, 0);
    }
    
    pub fn add_transition(&mut self, id: String, name: String, guard: Option<Guard>) {
        self.transitions.push(Transition { id, name, guard });
    }
    
    pub fn add_flow(&mut self, from: String, to: String, weight: u32) {
        self.flow_relation.insert((from, to), weight);
    }
    
    pub fn set_initial_marking(&mut self, place_id: String, tokens: u32) {
        self.initial_marking.insert(place_id, tokens);
    }
    
    pub fn is_enabled(&self, transition_id: &str, marking: &HashMap<String, u32>) -> bool {
        let transition = self.transitions.iter()
            .find(|t| t.id == transition_id)
            .expect("Transition not found");
        
        // 检查输入库所的托肯数量
        for place in &self.places {
            let flow_key = (place.id.clone(), transition_id.to_string());
            if let Some(required_tokens) = self.flow_relation.get(&flow_key) {
                let available_tokens = marking.get(&place.id).unwrap_or(&0);
                if available_tokens < required_tokens {
                    return false;
                }
            }
        }
        
        // 检查守卫条件
        if let Some(ref guard) = transition.guard {
            match guard {
                Guard::Always => true,
                Guard::Condition(condition) => condition(marking),
            }
        } else {
            true
        }
    }
    
    pub fn fire(&self, transition_id: &str, marking: &mut HashMap<String, u32>) -> Result<(), String> {
        if !self.is_enabled(transition_id, marking) {
            return Err(format!("Transition {} is not enabled", transition_id));
        }
        
        // 移除输入托肯
        for place in &self.places {
            let flow_key = (place.id.clone(), transition_id.to_string());
            if let Some(required_tokens) = self.flow_relation.get(&flow_key) {
                let current_tokens = marking.get_mut(&place.id).unwrap();
                *current_tokens -= required_tokens;
            }
        }
        
        // 添加输出托肯
        for place in &self.places {
            let flow_key = (transition_id.to_string(), place.id.clone());
            if let Some(produced_tokens) = self.flow_relation.get(&flow_key) {
                let current_tokens = marking.get_mut(&place.id).unwrap();
                *current_tokens += produced_tokens;
            }
        }
        
        Ok(())
    }
}
```

## 2.0 Petri网结构

### 2.1 结构性质

**定义 2.1.1 (纯Petri网)**
Petri网是纯的，如果不存在自环，即：
$$\forall p \in P, t \in T: (p, t) \in F \Rightarrow (t, p) \notin F$$

**定义 2.1.2 (简单Petri网)**
Petri网是简单的，如果：
$$\forall p \in P, t \in T: F(p, t) \leq 1 \land F(t, p) \leq 1$$

**定义 2.1.3 (自由选择Petri网)**
Petri网是自由选择的，如果：
$$\forall t_1, t_2 \in T: ^\bullet t_1 \cap ^\bullet t_2 \neq \emptyset \Rightarrow ^\bullet t_1 = ^\bullet t_2$$

### 2.2 特殊结构

**定义 2.2.1 (状态机)**
状态机是一个Petri网，其中每个变迁恰好有一个输入库所和一个输出库所：
$$\forall t \in T: |^\bullet t| = 1 \land |t^\bullet| = 1$$

**定义 2.2.2 (标记图)**
标记图是一个Petri网，其中每个库所恰好有一个输入变迁和一个输出变迁：
$$\forall p \in P: |^\bullet p| = 1 \land |p^\bullet| = 1$$

**定义 2.2.3 (自由选择网)**
自由选择网是一个Petri网，其中共享输入库所的变迁要么共享所有输入库所，要么没有共享的输入库所。

```go
// Go实现：Petri网结构分析
type PetriNetStructure struct {
    net *PetriNet
}

func NewPetriNetStructure(net *PetriNet) *PetriNetStructure {
    return &PetriNetStructure{net: net}
}

func (pns *PetriNetStructure) IsPure() bool {
    for _, place := range pns.net.places {
        for _, transition := range pns.net.transitions {
            // 检查是否存在自环
            hasInput := pns.net.hasFlow(place.ID, transition.ID)
            hasOutput := pns.net.hasFlow(transition.ID, place.ID)
            if hasInput && hasOutput {
                return false
            }
        }
    }
    return true
}

func (pns *PetriNetStructure) IsSimple() bool {
    for _, place := range pns.net.places {
        for _, transition := range pns.net.transitions {
            // 检查权重是否不超过1
            if pns.net.getFlowWeight(place.ID, transition.ID) > 1 {
                return false
            }
            if pns.net.getFlowWeight(transition.ID, place.ID) > 1 {
                return false
            }
        }
    }
    return true
}

func (pns *PetriNetStructure) IsFreeChoice() bool {
    for i, t1 := range pns.net.transitions {
        for j, t2 := range pns.net.transitions {
            if i >= j {
                continue
            }
            
            // 检查是否有共享输入库所
            sharedInputs := pns.getSharedInputPlaces(t1, t2)
            if len(sharedInputs) > 0 {
                // 检查是否共享所有输入库所
                t1Inputs := pns.getInputPlaces(t1)
                t2Inputs := pns.getInputPlaces(t2)
                
                if !reflect.DeepEqual(t1Inputs, t2Inputs) {
                    return false
                }
            }
        }
    }
    return true
}

func (pns *PetriNetStructure) IsStateMachine() bool {
    for _, transition := range pns.net.transitions {
        inputCount := pns.getInputPlaceCount(transition)
        outputCount := pns.getOutputPlaceCount(transition)
        
        if inputCount != 1 || outputCount != 1 {
            return false
        }
    }
    return true
}

func (pns *PetriNetStructure) IsMarkedGraph() bool {
    for _, place := range pns.net.places {
        inputCount := pns.getInputTransitionCount(place)
        outputCount := pns.getOutputTransitionCount(place)
        
        if inputCount != 1 || outputCount != 1 {
            return false
        }
    }
    return true
}

func (pns *PetriNetStructure) getSharedInputPlaces(t1, t2 *Transition) []string {
    t1Inputs := pns.getInputPlaces(t1)
    t2Inputs := pns.getInputPlaces(t2)
    
    shared := make([]string, 0)
    for _, p1 := range t1Inputs {
        for _, p2 := range t2Inputs {
            if p1 == p2 {
                shared = append(shared, p1)
            }
        }
    }
    return shared
}

func (pns *PetriNetStructure) getInputPlaces(t *Transition) []string {
    inputs := make([]string, 0)
    for _, place := range pns.net.places {
        if pns.net.hasFlow(place.ID, t.ID) {
            inputs = append(inputs, place.ID)
        }
    }
    return inputs
}
```

## 3.0 可达性分析

### 3.1 可达性定义

**定义 3.1.1 (可达性)**
标识 $M$ 从标识 $M_0$ 可达，记为 $M_0 \xrightarrow{*} M$，如果存在发射序列 $\sigma$ 使得 $M_0 \xrightarrow{\sigma} M$。

**定义 3.1.2 (可达集)**
Petri网 $N$ 的可达集定义为：
$$R(N) = \{M \mid M_0 \xrightarrow{*} M\}$$

**定义 3.1.3 (可达性图)**
可达性图是一个有向图 $G = (V, E)$，其中：
- $V = R(N)$ 是可达标识集合
- $E = \{(M, M') \mid \exists t \in T: M[t>M'\}$ 是发射关系

### 3.2 可达性算法

**算法 3.2.1 (可达性分析算法)**
```
function ReachabilityAnalysis(N):
    R = {M₀}
    W = {M₀}
    while W ≠ ∅ do
        M = W.pop()
        for each t ∈ T do
            if M[t> then
                M' = fire(M, t)
                if M' ∉ R then
                    R = R ∪ {M'}
                    W = W ∪ {M'}
    return R
```

**算法 3.2.2 (覆盖性分析)**
```
function CoverabilityAnalysis(N):
    R = {M₀}
    W = {M₀}
    while W ≠ ∅ do
        M = W.pop()
        for each t ∈ T do
            if M[t> then
                M' = fire(M, t)
                M'' = accelerate(M, M')
                if not covered(M'', R) then
                    R = R ∪ {M''}
                    W = W ∪ {M''}
    return R
```

```rust
// Rust实现：可达性分析
#[derive(Debug, Clone)]
pub struct ReachabilityAnalyzer {
    pub net: PetriNet,
    pub reachable_markings: HashSet<Vec<u32>>,
    pub reachability_graph: HashMap<Vec<u32>, Vec<(String, Vec<u32>)>>,
}

impl ReachabilityAnalyzer {
    pub fn new(net: PetriNet) -> Self {
        ReachabilityAnalyzer {
            net,
            reachable_markings: HashSet::new(),
            reachability_graph: HashMap::new(),
        }
    }
    
    pub fn analyze(&mut self) {
        let initial_marking = self.get_marking_vector();
        self.reachable_markings.insert(initial_marking.clone());
        
        let mut worklist = vec![initial_marking.clone()];
        
        while let Some(current_marking) = worklist.pop() {
            let mut transitions = Vec::new();
            
            for transition in &self.net.transitions {
                if self.is_enabled_in_marking(&transition.id, &current_marking) {
                    let new_marking = self.fire_transition(&transition.id, &current_marking);
                    
                    if !self.reachable_markings.contains(&new_marking) {
                        self.reachable_markings.insert(new_marking.clone());
                        worklist.push(new_marking.clone());
                    }
                    
                    transitions.push((transition.id.clone(), new_marking));
                }
            }
            
            self.reachability_graph.insert(current_marking, transitions);
        }
    }
    
    pub fn is_reachable(&self, target_marking: &Vec<u32>) -> bool {
        self.reachable_markings.contains(target_marking)
    }
    
    pub fn get_reachability_path(&self, target_marking: &Vec<u32>) -> Option<Vec<String>> {
        if !self.is_reachable(target_marking) {
            return None;
        }
        
        // 使用BFS找到最短路径
        let mut visited = HashSet::new();
        let mut queue = VecDeque::new();
        let mut parent = HashMap::new();
        
        let initial_marking = self.get_marking_vector();
        queue.push_back(initial_marking.clone());
        visited.insert(initial_marking.clone());
        
        while let Some(current) = queue.pop_front() {
            if current == *target_marking {
                // 重建路径
                let mut path = Vec::new();
                let mut current_marking = target_marking.clone();
                
                while current_marking != initial_marking {
                    if let Some((transition, parent_marking)) = parent.get(&current_marking) {
                        path.push(transition.clone());
                        current_marking = parent_marking.clone();
                    } else {
                        break;
                    }
                }
                
                path.reverse();
                return Some(path);
            }
            
            if let Some(transitions) = self.reachability_graph.get(&current) {
                for (transition_id, next_marking) in transitions {
                    if !visited.contains(next_marking) {
                        visited.insert(next_marking.clone());
                        queue.push_back(next_marking.clone());
                        parent.insert(next_marking.clone(), (transition_id.clone(), current.clone()));
                    }
                }
            }
        }
        
        None
    }
    
    pub fn get_marking_vector(&self) -> Vec<u32> {
        let mut marking = Vec::new();
        for place in &self.net.places {
            marking.push(*self.net.initial_marking.get(&place.id).unwrap_or(&0));
        }
        marking
    }
    
    pub fn is_enabled_in_marking(&self, transition_id: &str, marking: &Vec<u32>) -> bool {
        for (i, place) in self.net.places.iter().enumerate() {
            let flow_key = (place.id.clone(), transition_id.to_string());
            if let Some(required_tokens) = self.net.flow_relation.get(&flow_key) {
                if marking[i] < *required_tokens {
                    return false;
                }
            }
        }
        true
    }
    
    pub fn fire_transition(&self, transition_id: &str, marking: &Vec<u32>) -> Vec<u32> {
        let mut new_marking = marking.clone();
        
        // 移除输入托肯
        for (i, place) in self.net.places.iter().enumerate() {
            let flow_key = (place.id.clone(), transition_id.to_string());
            if let Some(required_tokens) = self.net.flow_relation.get(&flow_key) {
                new_marking[i] -= required_tokens;
            }
        }
        
        // 添加输出托肯
        for (i, place) in self.net.places.iter().enumerate() {
            let flow_key = (transition_id.to_string(), place.id.clone());
            if let Some(produced_tokens) = self.net.flow_relation.get(&flow_key) {
                new_marking[i] += produced_tokens;
            }
        }
        
        new_marking
    }
}
```

## 4.0 死锁检测

### 4.1 死锁定义

**定义 4.1.1 (死锁)**
Petri网处于死锁状态，如果没有任何变迁可以发射。

**定义 4.1.2 (死锁标识)**
标识 $M$ 是死锁标识，如果：
$$\forall t \in T: \neg M[t>$$

**定义 4.1.3 (死锁自由)**
Petri网是死锁自由的，如果从任何可达标识都可以发射某个变迁。

### 4.2 死锁检测算法

**算法 4.2.1 (死锁检测算法)**
```
function DeadlockDetection(N):
    deadlocks = ∅
    for each M ∈ R(N) do
        if is_deadlock(M) then
            deadlocks = deadlocks ∪ {M}
    return deadlocks
```

**算法 4.2.2 (死锁预防)**
```
function DeadlockPrevention(N):
    for each M ∈ R(N) do
        if is_deadlock(M) then
            add_control_place(M)
    return modified_net
```

```go
// Go实现：死锁检测
type DeadlockAnalyzer struct {
    net *PetriNet
    reachabilityAnalyzer *ReachabilityAnalyzer
}

func NewDeadlockAnalyzer(net *PetriNet) *DeadlockAnalyzer {
    reachabilityAnalyzer := NewReachabilityAnalyzer(net)
    reachabilityAnalyzer.Analyze()
    
    return &DeadlockAnalyzer{
        net: net,
        reachabilityAnalyzer: reachabilityAnalyzer,
    }
}

func (da *DeadlockAnalyzer) DetectDeadlocks() []Marking {
    deadlocks := make([]Marking, 0)
    
    for marking := range da.reachabilityAnalyzer.reachable_markings {
        if da.isDeadlock(marking) {
            deadlocks = append(deadlocks, da.vectorToMarking(marking))
        }
    }
    
    return deadlocks
}

func (da *DeadlockAnalyzer) isDeadlock(marking []u32) bool {
    for _, transition := range da.net.transitions {
        if da.reachabilityAnalyzer.is_enabled_in_marking(&transition.ID, &marking) {
            return false
        }
    }
    return true
}

func (da *DeadlockAnalyzer) IsDeadlockFree() bool {
    return len(da.DetectDeadlocks()) == 0
}

func (da *DeadlockAnalyzer) GetDeadlockPaths() map[Marking][]string {
    deadlockPaths := make(map[Marking][]string)
    
    for marking := range da.reachabilityAnalyzer.reachable_markings {
        if da.isDeadlock(marking) {
            if path := da.reachabilityAnalyzer.get_reachability_path(&marking); path != nil {
                deadlockPaths[da.vectorToMarking(marking)] = path
            }
        }
    }
    
    return deadlockPaths
}

func (da *DeadlockAnalyzer) PreventDeadlocks() *PetriNet {
    modifiedNet := da.net.clone()
    deadlocks := da.DetectDeadlocks()
    
    for i, deadlock := range deadlocks {
        controlPlace := Place{
            ID: fmt.Sprintf("control_%d", i),
            Name: fmt.Sprintf("Control Place %d", i),
            Capacity: nil,
        }
        
        modifiedNet.addPlace(controlPlace)
        
        // 添加控制弧
        for _, transition := range modifiedNet.transitions {
            if da.canLeadToDeadlock(transition, deadlock) {
                modifiedNet.addFlow(controlPlace.ID, transition.ID, 1)
            }
        }
        
        // 设置初始托肯
        modifiedNet.setInitialMarking(controlPlace.ID, 1)
    }
    
    return modifiedNet
}

func (da *DeadlockAnalyzer) canLeadToDeadlock(transition Transition, deadlock Marking) bool {
    // 检查发射该变迁是否能导致死锁
    // 简化实现：检查是否减少了关键资源
    for placeID, tokens := range deadlock {
        if tokens == 0 {
            // 如果死锁时某个库所为空，检查该变迁是否消耗该库所的托肯
            if da.net.hasFlow(placeID, transition.ID) {
                return true
            }
        }
    }
    return false
}

func (da *DeadlockAnalyzer) vectorToMarking(vector []u32) Marking {
    marking := make(Marking)
    for i, place := range da.net.places {
        marking[place.ID] = vector[i]
    }
    return marking
}
```

## 5.0 不变性分析

### 5.1 不变性定义

**定义 5.1.1 (P-不变性)**
P-不变性是一个向量 $I: P \to \mathbb{Z}$，使得对于任何可达标识 $M$：
$$\sum_{p \in P} I(p) \cdot M(p) = \sum_{p \in P} I(p) \cdot M_0(p)$$

**定义 5.1.2 (T-不变性)**
T-不变性是一个向量 $J: T \to \mathbb{Z}$，使得对于任何发射序列 $\sigma$：
$$\sum_{t \in T} J(t) \cdot \#(t, \sigma) = 0$$
其中 $\#(t, \sigma)$ 是变迁 $t$ 在序列 $\sigma$ 中的出现次数。

### 5.2 不变性计算

**算法 5.2.1 (P-不变性计算)**
```
function PInvariants(N):
    A = incidence_matrix(N)
    solve A^T * I = 0
    return basis_solutions
```

**算法 5.2.2 (T-不变性计算)**
```
function TInvariants(N):
    A = incidence_matrix(N)
    solve A * J = 0
    return basis_solutions
```

```rust
// Rust实现：不变性分析
#[derive(Debug, Clone)]
pub struct InvariantAnalyzer {
    pub net: PetriNet,
    pub incidence_matrix: Vec<Vec<i32>>,
}

impl InvariantAnalyzer {
    pub fn new(net: PetriNet) -> Self {
        let incidence_matrix = Self::compute_incidence_matrix(&net);
        InvariantAnalyzer {
            net,
            incidence_matrix,
        }
    }
    
    pub fn compute_incidence_matrix(net: &PetriNet) -> Vec<Vec<i32>> {
        let mut matrix = vec![vec![0; net.transitions.len()]; net.places.len()];
        
        for (i, place) in net.places.iter().enumerate() {
            for (j, transition) in net.transitions.iter().enumerate() {
                let input_weight = net.flow_relation.get(&(place.id.clone(), transition.id.clone())).unwrap_or(&0);
                let output_weight = net.flow_relation.get(&(transition.id.clone(), place.id.clone())).unwrap_or(&0);
                matrix[i][j] = *output_weight as i32 - *input_weight as i32;
            }
        }
        
        matrix
    }
    
    pub fn compute_p_invariants(&self) -> Vec<Vec<i32>> {
        // 计算P-不变性：A^T * I = 0
        let transpose = self.transpose_matrix(&self.incidence_matrix);
        self.solve_homogeneous_system(&transpose)
    }
    
    pub fn compute_t_invariants(&self) -> Vec<Vec<i32>> {
        // 计算T-不变性：A * J = 0
        self.solve_homogeneous_system(&self.incidence_matrix)
    }
    
    pub fn verify_p_invariant(&self, invariant: &Vec<i32>, marking: &Vec<u32>) -> bool {
        let initial_marking = self.get_initial_marking_vector();
        
        let initial_sum: i32 = invariant.iter().zip(initial_marking.iter())
            .map(|(i, m)| i * (*m as i32))
            .sum();
        
        let current_sum: i32 = invariant.iter().zip(marking.iter())
            .map(|(i, m)| i * (*m as i32))
            .sum();
        
        initial_sum == current_sum
    }
    
    pub fn verify_t_invariant(&self, invariant: &Vec<i32>, firing_count: &Vec<u32>) -> bool {
        let mut result = vec![0; self.net.places.len()];
        
        for (j, count) in firing_count.iter().enumerate() {
            for (i, _) in self.net.places.iter().enumerate() {
                result[i] += self.incidence_matrix[i][j] * (*count as i32);
            }
        }
        
        result.iter().all(|&x| x == 0)
    }
    
    pub fn transpose_matrix(&self, matrix: &Vec<Vec<i32>>) -> Vec<Vec<i32>> {
        let rows = matrix.len();
        let cols = matrix[0].len();
        let mut transpose = vec![vec![0; rows]; cols];
        
        for i in 0..rows {
            for j in 0..cols {
                transpose[j][i] = matrix[i][j];
            }
        }
        
        transpose
    }
    
    pub fn solve_homogeneous_system(&self, matrix: &Vec<Vec<i32>>) -> Vec<Vec<i32>> {
        // 使用高斯消元法求解齐次方程组
        let mut augmented = matrix.clone();
        let rows = augmented.len();
        let cols = augmented[0].len();
        
        // 高斯消元
        for i in 0..rows.min(cols) {
            // 寻找主元
            let mut max_row = i;
            for k in i + 1..rows {
                if augmented[k][i].abs() > augmented[max_row][i].abs() {
                    max_row = k;
                }
            }
            
            if augmented[max_row][i] == 0 {
                continue;
            }
            
            // 交换行
            if max_row != i {
                augmented.swap(i, max_row);
            }
            
            // 消元
            for k in i + 1..rows {
                let factor = augmented[k][i] / augmented[i][i];
                for j in i..cols {
                    augmented[k][j] -= factor * augmented[i][j];
                }
            }
        }
        
        // 回代求解
        let mut solutions = Vec::new();
        let mut free_vars = Vec::new();
        
        for i in 0..cols {
            let mut is_free = true;
            for j in 0..rows {
                if augmented[j][i] != 0 {
                    is_free = false;
                    break;
                }
            }
            if is_free {
                free_vars.push(i);
            }
        }
        
        // 为每个自由变量生成一个基础解
        for &free_var in &free_vars {
            let mut solution = vec![0; cols];
            solution[free_var] = 1;
            
            // 回代计算其他变量
            for i in (0..rows).rev() {
                let mut sum = 0;
                for j in i + 1..cols {
                    sum += augmented[i][j] * solution[j];
                }
                if augmented[i][i] != 0 {
                    solution[i] = -sum / augmented[i][i];
                }
            }
            
            solutions.push(solution);
        }
        
        solutions
    }
    
    pub fn get_initial_marking_vector(&self) -> Vec<u32> {
        let mut marking = Vec::new();
        for place in &self.net.places {
            marking.push(*self.net.initial_marking.get(&place.id).unwrap_or(&0));
        }
        marking
    }
}
```

## 6.0 性能分析

### 6.1 性能指标

**定义 6.1.1 (吞吐量)**
吞吐量是单位时间内发射的变迁数量。

**定义 6.1.2 (响应时间)**
响应时间是从输入到输出所需的时间。

**定义 6.1.3 (资源利用率)**
资源利用率是资源被使用的比例。

### 6.2 性能分析方法

**方法 6.2.1 (仿真分析)**
通过仿真运行Petri网，收集性能数据。

**方法 6.2.2 (马尔可夫链分析)**
将Petri网转换为马尔可夫链，进行数学分析。

**方法 6.2.3 (排队网络分析)**
将Petri网建模为排队网络。

```go
// Go实现：性能分析
type PerformanceAnalyzer struct {
    net *PetriNet
    simulation *PetriNetSimulator
}

type PetriNetSimulator struct {
    net *PetriNet
    currentMarking Marking
    firingTimes map[string]float64
    statistics map[string]*TransitionStatistics
}

type TransitionStatistics struct {
    firingCount int
    totalTime float64
    averageTime float64
    throughput float64
}

func NewPerformanceAnalyzer(net *PetriNet) *PerformanceAnalyzer {
    simulator := NewPetriNetSimulator(net)
    return &PerformanceAnalyzer{
        net: net,
        simulation: simulator,
    }
}

func (pa *PerformanceAnalyzer) AnalyzeThroughput(simulationTime float64) map[string]float64 {
    pa.simulation.Run(simulationTime)
    
    throughput := make(map[string]float64)
    for transitionID, stats := range pa.simulation.statistics {
        throughput[transitionID] = float64(stats.firingCount) / simulationTime
    }
    
    return throughput
}

func (pa *PerformanceAnalyzer) AnalyzeResponseTime() map[string]float64 {
    responseTimes := make(map[string]float64)
    
    for transitionID, stats := range pa.simulation.statistics {
        if stats.firingCount > 0 {
            responseTimes[transitionID] = stats.averageTime
        }
    }
    
    return responseTimes
}

func (pa *PerformanceAnalyzer) AnalyzeResourceUtilization() map[string]float64 {
    utilization := make(map[string]float64)
    
    // 计算每个库所的利用率
    for _, place := range pa.net.places {
        if capacity, exists := place.Capacity; exists {
            averageTokens := pa.simulation.getAverageTokens(place.ID)
            utilization[place.ID] = averageTokens / float64(capacity)
        }
    }
    
    return utilization
}

func (ps *PetriNetSimulator) Run(simulationTime float64) {
    currentTime := 0.0
    
    for currentTime < simulationTime {
        // 找到可以发射的变迁
        enabledTransitions := ps.getEnabledTransitions()
        
        if len(enabledTransitions) == 0 {
            break // 死锁
        }
        
        // 选择下一个要发射的变迁（随机选择）
        selectedTransition := ps.selectNextTransition(enabledTransitions)
        
        // 计算发射时间
        firingTime := ps.getFiringTime(selectedTransition)
        
        if currentTime + firingTime > simulationTime {
            break
        }
        
        // 发射变迁
        ps.fireTransition(selectedTransition)
        currentTime += firingTime
        
        // 更新统计信息
        ps.updateStatistics(selectedTransition, firingTime)
    }
}

func (ps *PetriNetSimulator) getEnabledTransitions() []string {
    enabled := make([]string, 0)
    
    for _, transition := range ps.net.transitions {
        if ps.isEnabled(&transition) {
            enabled = append(enabled, transition.ID)
        }
    }
    
    return enabled
}

func (ps *PetriNetSimulator) selectNextTransition(enabled []string) string {
    // 随机选择
    return enabled[rand.Intn(len(enabled))]
}

func (ps *PetriNetSimulator) getFiringTime(transitionID string) float64 {
    // 简化的时间模型：指数分布
    return rand.ExpFloat64()
}

func (ps *PetriNetSimulator) fireTransition(transitionID string) {
    // 执行变迁发射
    ps.net.fire(transitionID, &mut ps.currentMarking)
}

func (ps *PetriNetSimulator) updateStatistics(transitionID string, firingTime float64) {
    if stats, exists := ps.statistics[transitionID]; exists {
        stats.firingCount++
        stats.totalTime += firingTime
        stats.averageTime = stats.totalTime / float64(stats.firingCount)
    } else {
        ps.statistics[transitionID] = &TransitionStatistics{
            firingCount: 1,
            totalTime: firingTime,
            averageTime: firingTime,
            throughput: 0,
        }
    }
}
```

## 7.0 高级Petri网

### 7.1 时间Petri网

**定义 7.1.1 (时间Petri网)**
时间Petri网是一个六元组 $N = (P, T, F, M_0, I, D)$，其中：
- $I: T \to \mathbb{R}^+ \times \mathbb{R}^+$ 是时间间隔函数
- $D: T \to \mathbb{R}^+$ 是延迟函数

**定义 7.1.2 (时间发射)**
变迁 $t$ 在时间 $\tau$ 发射，如果：
1. $t$ 在标识 $M$ 下使能
2. $\tau \in [\text{earliest}(t), \text{latest}(t)]$

### 7.2 着色Petri网

**定义 7.2.1 (着色Petri网)**
着色Petri网是一个七元组 $N = (P, T, F, M_0, C, G, E)$，其中：
- $C: P \cup T \to \text{ColorSet}$ 是颜色集函数
- $G: T \to \text{Guard}$ 是守卫函数
- $E: F \to \text{Expression}$ 是表达式函数

### 7.3 层次Petri网

**定义 7.3.1 (层次Petri网)**
层次Petri网允许子网嵌套，形成层次结构。

```rust
// Rust实现：高级Petri网
#[derive(Debug, Clone)]
pub struct TimedPetriNet {
    pub places: Vec<Place>,
    pub transitions: Vec<TimedTransition>,
    pub flow_relation: HashMap<(String, String), u32>,
    pub initial_marking: HashMap<String, u32>,
    pub time_intervals: HashMap<String, (f64, f64)>,
}

#[derive(Debug, Clone)]
pub struct TimedTransition {
    pub id: String,
    pub name: String,
    pub earliest_time: f64,
    pub latest_time: f64,
    pub delay: f64,
}

impl TimedPetriNet {
    pub fn new() -> Self {
        TimedPetriNet {
            places: Vec::new(),
            transitions: Vec::new(),
            flow_relation: HashMap::new(),
            initial_marking: HashMap::new(),
            time_intervals: HashMap::new(),
        }
    }
    
    pub fn add_timed_transition(&mut self, id: String, name: String, earliest: f64, latest: f64, delay: f64) {
        self.transitions.push(TimedTransition {
            id: id.clone(),
            name,
            earliest_time: earliest,
            latest_time: latest,
            delay,
        });
        self.time_intervals.insert(id, (earliest, latest));
    }
    
    pub fn is_enabled_at_time(&self, transition_id: &str, marking: &HashMap<String, u32>, current_time: f64) -> bool {
        // 检查基本使能条件
        if !self.is_basic_enabled(transition_id, marking) {
            return false;
        }
        
        // 检查时间约束
        if let Some((earliest, latest)) = self.time_intervals.get(transition_id) {
            return current_time >= *earliest && current_time <= *latest;
        }
        
        true
    }
}

#[derive(Debug, Clone)]
pub struct ColoredPetriNet {
    pub places: Vec<ColoredPlace>,
    pub transitions: Vec<ColoredTransition>,
    pub flow_relation: HashMap<(String, String), Expression>,
    pub initial_marking: HashMap<String, Vec<Color>>,
    pub color_sets: HashMap<String, ColorSet>,
}

#[derive(Debug, Clone)]
pub struct ColoredPlace {
    pub id: String,
    pub name: String,
    pub color_set: String,
    pub capacity: Option<u32>,
}

#[derive(Debug, Clone)]
pub struct ColoredTransition {
    pub id: String,
    pub name: String,
    pub guard: Option<Guard>,
}

#[derive(Debug, Clone)]
pub enum Color {
    Int(i32),
    String(String),
    Tuple(Vec<Color>),
}

#[derive(Debug, Clone)]
pub enum ColorSet {
    Int,
    String,
    Product(Vec<ColorSet>),
}

#[derive(Debug, Clone)]
pub enum Expression {
    Variable(String),
    Constant(Color),
    Tuple(Vec<Expression>),
    Function(String, Vec<Expression>),
}

impl ColoredPetriNet {
    pub fn new() -> Self {
        ColoredPetriNet {
            places: Vec::new(),
            transitions: Vec::new(),
            flow_relation: HashMap::new(),
            initial_marking: HashMap::new(),
            color_sets: HashMap::new(),
        }
    }
    
    pub fn add_colored_place(&mut self, id: String, name: String, color_set: String, capacity: Option<u32>) {
        self.places.push(ColoredPlace {
            id: id.clone(),
            name,
            color_set,
            capacity,
        });
        self.initial_marking.insert(id, Vec::new());
    }
    
    pub fn add_colored_transition(&mut self, id: String, name: String, guard: Option<Guard>) {
        self.transitions.push(ColoredTransition {
            id,
            name,
            guard,
        });
    }
    
    pub fn is_enabled_with_binding(&self, transition_id: &str, binding: &HashMap<String, Color>) -> bool {
        // 检查守卫条件
        if let Some(transition) = self.transitions.iter().find(|t| t.id == transition_id) {
            if let Some(ref guard) = transition.guard {
                if !self.evaluate_guard(guard, binding) {
                    return false;
                }
            }
        }
        
        // 检查输入库所的托肯
        for place in &self.places {
            let flow_key = (place.id.clone(), transition_id.to_string());
            if let Some(expression) = self.flow_relation.get(&flow_key) {
                let required_tokens = self.evaluate_expression(expression, binding);
                let available_tokens = self.get_available_tokens(&place.id, &required_tokens);
                
                if available_tokens < required_tokens {
                    return false;
                }
            }
        }
        
        true
    }
    
    pub fn evaluate_expression(&self, expression: &Expression, binding: &HashMap<String, Color>) -> Vec<Color> {
        match expression {
            Expression::Variable(name) => {
                if let Some(color) = binding.get(name) {
                    vec![color.clone()]
                } else {
                    vec![]
                }
            }
            Expression::Constant(color) => vec![color.clone()],
            Expression::Tuple(expressions) => {
                let mut result = Vec::new();
                for expr in expressions {
                    result.extend(self.evaluate_expression(expr, binding));
                }
                result
            }
            Expression::Function(_, _) => vec![], // 简化实现
        }
    }
    
    pub fn evaluate_guard(&self, guard: &Guard, binding: &HashMap<String, Color>) -> bool {
        // 简化实现：总是返回true
        true
    }
    
    pub fn get_available_tokens(&self, place_id: &str, required_tokens: &Vec<Color>) -> u32 {
        if let Some(tokens) = self.initial_marking.get(place_id) {
            // 简化的匹配逻辑
            tokens.len() as u32
        } else {
            0
        }
    }
}
```

## 8.0 实践应用

### 8.1 工作流建模

**应用 8.1.1 (工作流Petri网)**
工作流Petri网用于建模业务流程：
1. **活动建模**：将业务活动建模为变迁
2. **状态建模**：将业务状态建模为库所
3. **流程控制**：使用Petri网控制流程执行

### 8.2 并发系统分析

**应用 8.2.1 (并发控制)**
Petri网用于分析并发系统：
1. **死锁检测**：检测并发系统中的死锁
2. **资源管理**：管理共享资源
3. **同步分析**：分析进程同步

### 8.3 性能评估

**应用 8.3.1 (系统性能)**
Petri网用于评估系统性能：
1. **吞吐量分析**：分析系统吞吐量
2. **响应时间分析**：分析系统响应时间
3. **资源利用率分析**：分析资源利用情况

### 8.4 总结

Petri网理论为并发系统建模和分析提供了强大的数学工具。

**关键要点**：
1. **基础概念**：库所、变迁、标识、发射
2. **结构分析**：纯网、简单网、自由选择网
3. **可达性分析**：可达集、可达性图
4. **死锁检测**：死锁识别、死锁预防
5. **不变性分析**：P-不变性、T-不变性
6. **性能分析**：吞吐量、响应时间、资源利用率
7. **高级扩展**：时间Petri网、着色Petri网、层次Petri网

**下一步工作**：
1. 完善更多Petri网类型
2. 增加性能优化算法
3. 开发更多实践工具
4. 建立完整的测试体系 