from typing import TypeVar, Generic

from .. import Executor

Action = TypeVar('Action')
Result = TypeVar('Result')

class Collector(Generic[Action, Result]):
    """Collects actions yielded by an orchestration.
    
    Usage:
    ```
    collector = Collector(executor)
    await syncopate.run(orchestration, collector)
    collector.actions # list[Action]
    ```
    
    """
    _executor: Executor[Action, Result]
    actions: list[Action]
    
    def __init__(self, executor: Executor[Action, Result]):
        self._executor = executor
        self.actions = []
        
    def __call__(self, action: Action) -> Result:
        self.actions += [action]
        return self._executor(action)