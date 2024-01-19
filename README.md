# Syncopate

> Tools for higher-order, pure orchestrations

## Usage

1. Define actions:

    ```python
    @dataclass
    class Greet:
        name: str
        
    @dataclass
    class Fetch:
        container: str
        num_items: int
        
    Action = Greet | Fetch
    ```

2. Define orchestration:

    ```python
    def orchestration() -> Generator[Action, Any, list[str]]:
        users = yield Fetch(container='users', num_items=3)
        for user in users:
            yield Greet(user)
        return users
    ```

3. Define executor:

   ```python
    def executor(action: Action):
        match action:
            case Greet():
                print(f"Hi, {action.name}!")
            case Fetch():
                print(f"Fetching {action.num_items} from '{action.container}'")
                return [f"User{i}" for i in range(action.num_items)]
   ```

4. Run!:

    ```python
    import syncopate

    await syncopate.run(orchestration, executor)
    # Fetching 3 from 'users'
    # Hi, User0!
    # Hi, User1!
    # Hi, User2!
    ```

## Installation

```bash
pip install syncopate
```

## Orchestrations and Executors

An executor is just a function of type

```python
Executor = Callable[[Action], Result | Awaitable[Result]]
```

`Action` and `Result` can be anything, as long as the orchestration you pair it with can handle them. An orchestration is just a generator function with type

```python
Orchestration = Generator[Action, Result, Return] # sends Action, receives Result, returns Return
```

## Combinators

Complexer behavior can be easily injected via `syncopate.combinators`. A combinator is just a higher-order function of type

```python
Combinator = Callable[Executor[Action, Result], Executor[Action2, Result2]]
```

### Example

For instance, parallel execution can be achieved using `combinators.parallelize`, roughly implemented as:

```python
def parallelize(executor: Executor[Action, Result]) -> Executor[Action | list[Action], Result | list[Result]]:
    async def _executor(actions):
        if isinstance(actions, list):
            return await asyncio.gather(*map(executor, actions))
        else:
            return await executor(action)
    
    return _executor
```

You can then use the same simple action executor but yield multiple actions to it for simultaneous execution:

```python
def parallel_orchestration() -> Generator[Action | list[Action], Any, list[str]]:
    users = yield Fetch(container='users', num_items=3)
    yield [Greet(user) for user in users]
    return users

syncopate.run(parallel_orchestration(), parallelize(executor))
```

### Composition

Multiple combinators (both in `syncopate.combinators` and custom) can be composed to create a new executor:

```python
from syncopate.combinators import parallel, logged

def custom_combinator(executor: Executor[...]) -> Executor[...]:
    ...

def executor(action: Action) -> Result:
    ...

custom_logged_parallel_executor = custom_combinator(logged(parallel(executor))) # please don't give variables such long names :)
```