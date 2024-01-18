from typing import TypeVar, Callable, Awaitable
from functools import wraps
import haskellian.asynch as hka
from .. import Executor

Action = TypeVar('Action')
Result = TypeVar('Result')
Return = TypeVar('Return')

def pre(executor: Executor[Action, Result], f: Callable[[Action], None]) -> Executor[Action, Result]:
    """Executor that runs `f(action)` before `executor(action)`"""
    @wraps(executor)
    def _exec(action: Action) -> Result:
        f(action)
        return executor(action)
    return _exec

def post(executor: Executor[Action, Result], f: Callable[[Action, Result], None]) -> Executor[Action, Result]:
    """Executor that runs `f(action, result)` after `result = executor(action)"""
    @wraps(executor)
    async def _exec(action: Action) -> Result:
        result = await hka.wait(executor(action))
        f(action, result)
        return result
    return _exec

def logged(executor: Executor[Action, Result], logger: Callable[[str], None] = print) -> Executor[Action, Result]:
    """Executor that logs action pre-`executor` and result post-`executor`"""
    @wraps(executor)
    async def _exec(action: Action) -> Result:
        logger(f"[LOG] Executing {action}")
        result = await hka.wait(executor(action))
        logger(f"[LOG] Executed -> {result}")
        return result
    return _exec
