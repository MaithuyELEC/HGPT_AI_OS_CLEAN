from __future__ import annotations

import inspect
import os
import sys
import threading
from functools import wraps
from pathlib import Path
from types import ModuleType
from typing import Any

_trace_state = threading.local()


def _is_tracing() -> bool:
    return bool(getattr(_trace_state, "tracing", False))


def _write_runtime_trace(lines: list[str]) -> None:
    stream = getattr(sys, "__stdout__", None)
    if stream is None:
        return

    for line in lines:
        stream.write(f"{line}\n")
    stream.flush()


def _mtime(path: str | os.PathLike[str] | None) -> str:
    if not path:
        return "missing"
    try:
        return str(Path(path).stat().st_mtime)
    except OSError as exc:
        return f"unavailable: {exc}"


def _module(module_name: str) -> ModuleType | None:
    return sys.modules.get(module_name)


def module_loaded(module_name: str, file_path: str | None, class_obj: Any = None) -> None:
    class_name = getattr(class_obj, "__name__", str(class_obj or ""))
    print("========== MODULE LOADED ==========")
    print(f"module: {module_name}")
    print(f"absolute path: {Path(file_path).resolve() if file_path else 'missing'}")
    print(f"mtime: {_mtime(file_path)}")
    print(f"class: {class_name}")
    print("===================================")
    exact_source(module_name, class_obj)


def exact_source(module_name: str, obj: Any = None) -> None:
    module = _module(module_name)
    target = obj if obj is not None else module
    print("========== EXACT SOURCE ==========")
    print(f"module: {module_name}")
    if obj is not None:
        print(f"inspect.getfile(class): {inspect.getfile(obj)}")
        print(f"inspect.getsourcefile(class): {inspect.getsourcefile(obj)}")
    else:
        print("inspect.getfile(class): n/a")
        print("inspect.getsourcefile(class): n/a")
    print(f"__file__: {getattr(module, '__file__', 'missing')}")
    print(f"__cached__: {getattr(module, '__cached__', 'missing')}")
    print(f"object id: {id(target)}")
    print("==================================")


def trace_call(label: str, obj: Any = None, **values: Any) -> None:
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    module = inspect.getmodule(caller) if caller is not None else None
    function = caller.f_code.co_name if caller is not None else "unknown"
    line = caller.f_lineno if caller is not None else "unknown"
    class_name = obj.__class__.__name__ if obj is not None else ""
    print("========== RUNTIME TRACE ==========")
    print(f"step: {label}")
    print(f"FULL FILE PATH: {Path(module.__file__).resolve() if module and getattr(module, '__file__', None) else 'missing'}")
    print(f"CLASS: {class_name}")
    print(f"FUNCTION: {function}")
    print(f"LINE NUMBER: {line}")
    print(f"MODULE NAME: {module.__name__ if module else 'missing'}")
    print(f"OBJECT ID: {id(obj) if obj is not None else 'n/a'}")
    for key, value in values.items():
        print(f"{key}: {value}")
    print("===================================")


def _runtime_trace_event(
    event: str,
    *,
    label: str,
    obj: Any = None,
    module_name: str,
    class_name: str,
    function_name: str,
    line_number: int,
    **values: Any,
) -> None:
    if _is_tracing():
        return

    _trace_state.tracing = True
    try:
        lines = [
            "========== RUNTIME TRACE ==========",
            event,
            f"step: {label}",
            f"module: {module_name}",
            f"class: {class_name}",
            f"function: {function_name}",
            f"line: {line_number}",
            f"object_id: {id(obj) if obj is not None else 'n/a'}",
        ]
        lines.extend(f"{key}: {value}" for key, value in values.items())
        lines.append("===================================")
        _write_runtime_trace(lines)
    finally:
        _trace_state.tracing = False


def trace_enter(label: str, obj: Any = None, **values: Any) -> None:
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    module = inspect.getmodule(caller) if caller is not None else None
    _runtime_trace_event(
        "ENTER",
        label=label,
        obj=obj,
        module_name=module.__name__ if module else "missing",
        class_name=obj.__class__.__name__ if obj is not None else "",
        function_name=caller.f_code.co_name if caller is not None else "unknown",
        line_number=caller.f_lineno if caller is not None else -1,
        **values,
    )


def trace_exit(label: str, obj: Any = None, **values: Any) -> None:
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    module = inspect.getmodule(caller) if caller is not None else None
    _runtime_trace_event(
        "EXIT",
        label=label,
        obj=obj,
        module_name=module.__name__ if module else "missing",
        class_name=obj.__class__.__name__ if obj is not None else "",
        function_name=caller.f_code.co_name if caller is not None else "unknown",
        line_number=caller.f_lineno if caller is not None else -1,
        **values,
    )


def trace_function(func: Any) -> Any:
    if getattr(func, "__runtime_trace_wrapped__", False) or getattr(func, "__runtime_trace_exempt__", False):
        return func

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if _is_tracing():
            return func(*args, **kwargs)

        obj = args[0] if args and "." in getattr(func, "__qualname__", "") else None
        class_name = obj.__class__.__name__ if obj is not None else ""
        label = f"{func.__module__}.{func.__qualname__}"
        _runtime_trace_event(
            "ENTER",
            label=label,
            obj=obj,
            module_name=func.__module__,
            class_name=class_name,
            function_name=func.__name__,
            line_number=func.__code__.co_firstlineno,
        )
        try:
            return func(*args, **kwargs)
        finally:
            _runtime_trace_event(
                "EXIT",
                label=label,
                obj=obj,
                module_name=func.__module__,
                class_name=class_name,
                function_name=func.__name__,
                line_number=func.__code__.co_firstlineno,
            )

    wrapper.__runtime_trace_wrapped__ = True
    return wrapper


def instrument_runtime_tracing(module_globals: dict[str, Any]) -> None:
    module_name = module_globals.get("__name__", "")
    for name, value in list(module_globals.items()):
        if inspect.isfunction(value) and value.__module__ == module_name:
            module_globals[name] = trace_function(value)
            continue

        if not inspect.isclass(value) or value.__module__ != module_name:
            continue

        for attr_name, attr_value in list(vars(value).items()):
            if inspect.isfunction(attr_value):
                setattr(value, attr_name, trace_function(attr_value))


def engine_loaded(
    obj: Any,
    *,
    selected_topic: str,
    selected_playbook: str,
    knowledge_count: int,
    selected_writer: str,
    output_folder: Any,
) -> None:
    cls = obj.__class__ if obj is not None else None
    module = inspect.getmodule(cls) if cls is not None else None
    file_path = inspect.getfile(cls) if cls is not None else None
    source_path = inspect.getsourcefile(cls) if cls is not None else None
    print("=" * 52)
    print("ENGINE LOADED")
    print(f"file: {getattr(module, '__file__', 'missing')}")
    print(f"cached: {getattr(module, '__cached__', 'missing')}")
    print(f"inspect.getfile(...): {file_path or 'missing'}")
    print(f"inspect.getsourcefile(...): {source_path or 'missing'}")
    print(f"mtime: {_mtime(source_path or file_path)}")
    print(f"Writer class: {cls.__name__ if cls is not None else 'missing'}")
    print(f"Selected Topic: {selected_topic}")
    print(f"Selected Playbook: {selected_playbook or 'None'}")
    print(f"Knowledge count: {knowledge_count}")
    print(f"Selected Writer: {selected_writer}")
    print(f"Output Folder: {output_folder}")
    print("=" * 52)


def fallback(reason: str) -> None:
    frame = inspect.currentframe()
    caller = frame.f_back if frame is not None else None
    function = caller.f_code.co_name if caller is not None else "unknown"
    print("******** FALLBACK ********")
    print(f"reason: {reason}")
    print(f"function: {function}")
    print(f"line: {caller.f_lineno if caller is not None else 'unknown'}")
    print("**************************")
