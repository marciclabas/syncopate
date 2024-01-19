from typing import TypeVar, Callable, Awaitable
from functools import wraps
import asyncio
import haskellian.asynch as hka
from .. import Executor

Action = TypeVar('Action')
Result = TypeVar('Result')

def parallelize(executor: Executor[Action, Result]) -> Executor[Action | list[Action], Result | list[Result]]:
    """Return an executor that accepts a list of actions and runs them concurrently"""
    @wraps(executor)
    async def _exec(action: Action | list[Action]) -> Result | list[Result]:
        if isinstance(action, list):
            return await asyncio.gather(*(
                hka.wait(executor(a)) for a in action
            ))
        else:
            return await hka.wait(executor(action))
    return _exec