Created this repo while learning LangGraph. 

# LangGraph

Type annotations are very important. We use typedict to write classes with defined types. And there are options like 
Optional, Union, ..

- Dictionary
- Union, Optional, Any
- lambda function

------------------------
## Different elements in LangGraph

- State
- Node
- Graph
- Edges, Conditional Edges
- Start Node, end Node
- tools
- toolNode
- State Graph
- Runnable

## Different types of messages

Human message, AI message, System message, tool message, function message

## Graph 1

Main aim is to understand how data flows throgh a single node in langgraph.

### Hello World Graph
- Understand and define the AgentSTate structure.
- Create a simple node functions to process and update state.
- Set up a basic LangGraph structure.
- Compile and invoke a LangGraph graph.
- Understand how data flows through a single-node in LangGraph.
            
            | Start |--->(Node)--->| End |

## Graph 2
- More complex Agent State
- Create a processing node that performs operations on list data.
- Set up a LangGraph that processes and outputs computed results.
- Invoke the graph with structured inputs and retrieve outputs.
           
## Graph 3 - Sequential Graph
- Create multiple Nodes that sequentially process and update different part of the state.
- Connect Nodes together in a graph.
- Invoke the Graph and see how the state is transformed step-by-step
- **Main Goal:** Create and handle multiple Nodes.

## Graph 4 - Conditional Graph
- Implement conditional logic to route the flow of data to different nodes.
- Use start and end nodes to manage entry and exit points explicitly.
- Design multiple nodes to perform different operations (addition, subtraction).
- Create a router node to handle decision-making and control graph flow.
- **Main Goal:** How to use "add_conditional_edges()"

## Graph 5 - Looping Graph
- Implement looping logic to route the flow of data back to the nodes.
- Create a single conditional edges to handle decision-making and control graph flow.
- **Main Goal:** Coding up Looping Logic.