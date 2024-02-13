from typing import TypeVar, Generator, Callable, Awaitable
import haskellian.asynch as hka

Action = TypeVar('Action')
Result = TypeVar('Result')
Return = TypeVar('Return')

Orchestration = Generator[Action, Result, Return]
Executor = Callable[[Action], Result | Awaitable[Result]]

async def run(
    orchestration: Generator[Action, Result, Return],
    executor: Callable[[Action], Result | Awaitable[Result]]
) -> Return:
    """Run an `orchestration` by passing actions to `executor`"""
    try:
        action = next(orchestration)
        while True:
            result = await hka.wait(executor(action))
            action = orchestration.send(result)
    except StopIteration as s:
        return s.value
