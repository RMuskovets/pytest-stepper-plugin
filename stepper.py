import traceback
from typing import Optional, Literal, Union

from _pytest._code import ExceptionInfo
from _pytest._code.code import TerminalRepr
from _pytest._io import TerminalWriter
from _pytest.outcomes import Failed
from pytest import Item, hookimpl
from _pytest.python import PyCollector

_TracebackStyle = Literal["long", "short", "line", "no", "native", "value", "auto"]
# shamelessly copied from _pytest._code


class StepperException(Exception):
    """
    Custom exception for reporting.

    Includes step number (``step_n``), type of failure (explicit ``fail()``, assertion fail, exception)
    and the failed test in form of a ``pytest.Item``.
    """

    def __init__(self, item: "StepperItem", step_n: int, reason: str, *args):
        super().__init__(item, step_n, reason, *args)
        self.item, self.step_n, self.reason, self.other_args = item, step_n, reason, args


class StepperFailureTRepr(TerminalRepr):
    """
    Representation of a test failure.
    """

    def __init__(self, excinfo: ExceptionInfo[BaseException], style: Optional[_TracebackStyle]):
        self.excinfo = excinfo
        self.style = style

    def format_traceback(self):
        """
        Format traceback of ``self.excinfo`` in traditional Python style, removing hidden frames.

        To hide a frame from traceback, set ``__tracebackhide__`` to ``True``.
        """
        filtered_traceback = self.excinfo.traceback.filter()

        entry_generator = ((entry._rawentry.tb_frame, entry._rawentry.tb_lineno) for entry in filtered_traceback)

        stack_summary = traceback.StackSummary.extract(entry_generator)
        tb = stack_summary.format()
        return tb

    def toterminal(self, tw: TerminalWriter) -> None:
        """
        Write the failure summary to given ``TerminalWriter``.

        Text includes failed step number (starting from ``1``), type of failure (explicit fail(), assertion failure, exception)
        and a traceback formatted in traditional Python style with hidden frames removed.
        """
        exc: StepperException = self.excinfo.value
        tw.line(f"test execution failed at step #{exc.step_n}, reason: {exc.reason}", red=True)

        tb = self.format_traceback()

        tw.line("traceback:")
        tw.line("\n".join(map(lambda x: str(x).strip(), tb)))


class StepperItem(Item):
    """
    Custom ``Item`` designed for running ``stepper`` tests.
    """

    def __init__(self, name: str, parent, spec: list):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        __tracebackhide__ = True
        vars = {}
        step_n = 1
        for step in self.spec:
            try:
                step(vars)
                step_n += 1
            except BaseException as exc:
                if isinstance(exc, Failed):
                    reason = "step failure"
                elif isinstance(exc, AssertionError):
                    reason = "assertion failure"
                else:
                    reason = f"exception: {exc}"
                raise StepperException(self, step_n, reason, *exc.args).with_traceback(exc.__traceback__)
                # modify traceback to include the original one

    def repr_failure(self, excinfo: ExceptionInfo[BaseException], style: "Optional[_TracebackStyle]" = None) \
            -> Union[str, TerminalRepr]:
        return StepperFailureTRepr(excinfo, style)

    def reportinfo(self):
        return self.fspath, 0, f"test: {self.name}"


@hookimpl
def pytest_pycollect_makeitem(collector: PyCollector, name: str, obj: object) -> Optional[Item]:
    if isinstance(obj, list) and name.startswith("test_"):
        return StepperItem.from_parent(collector, name=name, spec=obj)
