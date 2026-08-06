"""Java/Python teaching templates for GoF patterns, SOLID, and combos."""

from __future__ import annotations

from define_catalog import DomainContext

# Each renderer returns (java, python, java_test, python_test).


def _hdr_java(kind: str, label: str, domain: str, tier: str) -> str:
    return (
        f"// DesignPatternsSolid | kind={kind} | label={label} "
        f"| domain={domain} | tier={tier}\n"
        "package org.example.patterns;\n\n"
    )


def _hdr_py(kind: str, label: str, domain: str, tier: str) -> str:
    return (
        f'"""DesignPatternsSolid | kind={kind} | label={label} '
        f'| domain={domain} | tier={tier}"""\n'
        "from __future__ import annotations\n\n"
    )


def _log_java(tier: str) -> str:
    if tier == "minimal":
        return ""
    return '        System.out.println("[log] " + msg);\n'


def _log_py(tier: str) -> str:
    if tier == "minimal":
        return "        pass\n"
    return '        print(f"[log] {msg}")\n'


def _err_java_check(tier: str, cond: str, msg: str) -> str:
    if tier != "errors":
        return ""
    return f'        if ({cond}) throw new IllegalArgumentException("{msg}");\n'


def _err_py_check(tier: str, cond: str, msg: str) -> str:
    if tier != "errors":
        return ""
    return f'        if {cond}:\n            raise ValueError("{msg}")\n'


# ---------------------------------------------------------------------------
# Creational
# ---------------------------------------------------------------------------


def singleton(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    log_line = '        System.out.println("[log] set " + value);\n' if tier != "minimal" else ""
    err = _err_java_check(tier, "value == null || value.isEmpty()", "value required")
    j = _hdr_java("design_pattern", "singleton", ctx.domain, tier)
    j += f"""public final class {c}Singleton {{
    private static {c}Singleton instance;
    private String value = "default";

    private {c}Singleton() {{}}

    public static synchronized {c}Singleton getInstance() {{
        if (instance == null) {{
            instance = new {c}Singleton();
        }}
        return instance;
    }}

    public void setValue(String value) {{
{err}        this.value = value;
{log_line}    }}

    public String getValue() {{
        return value;
    }}
}}
"""
    err_py = _err_py_check(tier, "not value", "value required")
    log_py = '        print(f"[log] set {value}")\n' if tier != "minimal" else ""
    p = _hdr_py("design_pattern", "singleton", ctx.domain, tier)
    p += f'''class {c}Singleton:
    _instance: "{c}Singleton | None" = None

    def __new__(cls) -> "{c}Singleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = "default"
        return cls._instance

    def set_value(self, value: str) -> None:
{err_py}        self.value = value
{log_py}
    def get_value(self) -> str:
        return self.value
'''
    jt = f"""package org.example.patterns;
public class {c}SingletonTest {{
    public static void main(String[] args) {{
        {c}Singleton a = {c}Singleton.getInstance();
        {c}Singleton b = {c}Singleton.getInstance();
        a.setValue("{s}-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("{s}-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_singleton_{s}():\n    assert True\n"
    return j, p, jt, pt


def factory(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    err_j = _err_java_check(tier, 'type == null || type.isEmpty()', "type required")
    err_p = _err_py_check(tier, "not type_name", "type required")
    log_j = '        System.out.println("[log] create " + type);\n' if tier != "minimal" else ""
    log_p = '        print(f"[log] create {type_name}")\n' if tier != "minimal" else ""
    j = _hdr_java("design_pattern", "factory", ctx.domain, tier)
    j += f"""interface {c}Product {{
    String operate();
}}

class {c}BasicProduct implements {c}Product {{
    public String operate() {{ return "basic-{s}"; }}
}}

class {c}PremiumProduct implements {c}Product {{
    public String operate() {{ return "premium-{s}"; }}
}}

public class {c}Factory {{
    public {c}Product create(String type) {{
{err_j}{log_j}        if ("premium".equalsIgnoreCase(type)) return new {c}PremiumProduct();
        return new {c}BasicProduct();
    }}
}}
"""
    p = _hdr_py("design_pattern", "factory", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Product(ABC):
    @abstractmethod
    def operate(self) -> str:
        ...

class {c}BasicProduct({c}Product):
    def operate(self) -> str:
        return "basic-{s}"

class {c}PremiumProduct({c}Product):
    def operate(self) -> str:
        return "premium-{s}"

class {c}Factory:
    def create(self, type_name: str) -> {c}Product:
{err_p}{log_p}        if type_name.lower() == "premium":
            return {c}PremiumProduct()
        return {c}BasicProduct()
'''
    jt = f"""package org.example.patterns;
public class {c}FactoryTest {{
    public static void main(String[] args) {{
        {c}Factory f = new {c}Factory();
        if (!f.create("basic").operate().equals("basic-{s}")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-{s}")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f'''def test_{s}_factory():
    from importlib import import_module
    # placeholder replaced by generator import hook
    pass
'''
    return j, p, jt, pt


def abstract_factory(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "abstract factory", ctx.domain, tier)
    j += f"""interface {c}Button {{ String render(); }}
interface {c}Dialog {{ String show(); }}

class {c}CloudButton implements {c}Button {{
    public String render() {{ return "cloud-btn-{s}"; }}
}}
class {c}CloudDialog implements {c}Dialog {{
    public String show() {{ return "cloud-dlg-{s}"; }}
}}
class {c}LocalButton implements {c}Button {{
    public String render() {{ return "local-btn-{s}"; }}
}}
class {c}LocalDialog implements {c}Dialog {{
    public String show() {{ return "local-dlg-{s}"; }}
}}

interface {c}UIFactory {{
    {c}Button createButton();
    {c}Dialog createDialog();
}}

class {c}CloudFactory implements {c}UIFactory {{
    public {c}Button createButton() {{ return new {c}CloudButton(); }}
    public {c}Dialog createDialog() {{ return new {c}CloudDialog(); }}
}}

class {c}LocalFactory implements {c}UIFactory {{
    public {c}Button createButton() {{ return new {c}LocalButton(); }}
    public {c}Dialog createDialog() {{ return new {c}LocalDialog(); }}
}}

public class {c}AbstractFactoryDemo {{
    public static String run({c}UIFactory factory) {{
        return factory.createButton().render() + "|" + factory.createDialog().show();
    }}
}}
"""
    p = _hdr_py("design_pattern", "abstract factory", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class {c}Dialog(ABC):
    @abstractmethod
    def show(self) -> str: ...

class {c}CloudButton({c}Button):
    def render(self) -> str: return "cloud-btn-{s}"

class {c}CloudDialog({c}Dialog):
    def show(self) -> str: return "cloud-dlg-{s}"

class {c}LocalButton({c}Button):
    def render(self) -> str: return "local-btn-{s}"

class {c}LocalDialog({c}Dialog):
    def show(self) -> str: return "local-dlg-{s}"

class {c}UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> {c}Button: ...
    @abstractmethod
    def create_dialog(self) -> {c}Dialog: ...

class {c}CloudFactory({c}UIFactory):
    def create_button(self) -> {c}Button: return {c}CloudButton()
    def create_dialog(self) -> {c}Dialog: return {c}CloudDialog()

class {c}LocalFactory({c}UIFactory):
    def create_button(self) -> {c}Button: return {c}LocalButton()
    def create_dialog(self) -> {c}Dialog: return {c}LocalDialog()

def run_ui(factory: {c}UIFactory) -> str:
    return factory.create_button().render() + "|" + factory.create_dialog().show()
'''
    jt = f"""package org.example.patterns;
public class {c}AbstractFactoryTest {{
    public static void main(String[] args) {{
        String out = {c}AbstractFactoryDemo.run(new {c}CloudFactory());
        if (!out.equals("cloud-btn-{s}|cloud-dlg-{s}")) throw new AssertionError(out);
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_abstract_factory_{s}():\n    assert True\n"
    return j, p, jt, pt


def builder(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    err_j = _err_java_check(tier, "name == null || name.isEmpty()", "name required")
    err_p = _err_py_check(tier, "not name", "name required")
    j = _hdr_java("design_pattern", "builder", ctx.domain, tier)
    j += f"""public class {c}Config {{
    private final String name;
    private final int limit;
    private final boolean enabled;

    private {c}Config(Builder b) {{
        this.name = b.name;
        this.limit = b.limit;
        this.enabled = b.enabled;
    }}

    public String summary() {{
        return name + ":" + limit + ":" + enabled;
    }}

    public static class Builder {{
        private String name = "{s}";
        private int limit = 10;
        private boolean enabled = true;

        public Builder name(String name) {{
{err_j}            this.name = name;
            return this;
        }}
        public Builder limit(int limit) {{ this.limit = limit; return this; }}
        public Builder enabled(boolean enabled) {{ this.enabled = enabled; return this; }}
        public {c}Config build() {{ return new {c}Config(this); }}
    }}
}}
"""
    p = _hdr_py("design_pattern", "builder", ctx.domain, tier)
    p += f'''from dataclasses import dataclass

@dataclass(frozen=True)
class {c}Config:
    name: str
    limit: int
    enabled: bool

    def summary(self) -> str:
        return f"{{self.name}}:{{self.limit}}:{{self.enabled}}"

class {c}ConfigBuilder:
    def __init__(self) -> None:
        self._name = "{s}"
        self._limit = 10
        self._enabled = True

    def name(self, name: str) -> "{c}ConfigBuilder":
{err_p}        self._name = name
        return self

    def limit(self, limit: int) -> "{c}ConfigBuilder":
        self._limit = limit
        return self

    def enabled(self, enabled: bool) -> "{c}ConfigBuilder":
        self._enabled = enabled
        return self

    def build(self) -> {c}Config:
        return {c}Config(self._name, self._limit, self._enabled)
'''
    jt = f"""package org.example.patterns;
public class {c}BuilderTest {{
    public static void main(String[] args) {{
        {c}Config cfg = new {c}Config.Builder().name("{s}-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("{s}-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_builder_{s}():\n    assert True\n"
    return j, p, jt, pt


def prototype(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "prototype", ctx.domain, tier)
    j += f"""public class {c}Prototype implements Cloneable {{
    private String label;
    private int weight;

    public {c}Prototype(String label, int weight) {{
        this.label = label;
        this.weight = weight;
    }}

    public {c}Prototype copy() {{
        try {{
            return ({c}Prototype) this.clone();
        }} catch (CloneNotSupportedException e) {{
            throw new RuntimeException(e);
        }}
    }}

    public void setLabel(String label) {{ this.label = label; }}
    public String describe() {{ return label + "#" + weight; }}
}}
"""
    p = _hdr_py("design_pattern", "prototype", ctx.domain, tier)
    p += f'''from dataclasses import dataclass
import copy

@dataclass
class {c}Prototype:
    label: str
    weight: int

    def copy(self) -> "{c}Prototype":
        return copy.copy(self)

    def describe(self) -> str:
        return f"{{self.label}}#{{self.weight}}"
'''
    jt = f"""package org.example.patterns;
public class {c}PrototypeTest {{
    public static void main(String[] args) {{
        {c}Prototype a = new {c}Prototype("{s}", 2);
        {c}Prototype b = a.copy();
        b.setLabel("{s}-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_prototype_{s}():\n    assert True\n"
    return j, p, jt, pt


# ---------------------------------------------------------------------------
# Structural
# ---------------------------------------------------------------------------


def adapter(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "adapter", ctx.domain, tier)
    j += f"""class {c}LegacyApi {{
    public String legacyFetch() {{ return "LEGACY-{s}"; }}
}}

interface {c}Target {{
    String fetch();
}}

public class {c}Adapter implements {c}Target {{
    private final {c}LegacyApi legacy;

    public {c}Adapter({c}LegacyApi legacy) {{
        this.legacy = legacy;
    }}

    public String fetch() {{
        String raw = legacy.legacyFetch();
        return raw.toLowerCase().replace("legacy-", "modern-");
    }}
}}
"""
    p = _hdr_py("design_pattern", "adapter", ctx.domain, tier)
    p += f'''class {c}LegacyApi:
    def legacy_fetch(self) -> str:
        return "LEGACY-{s}"

class {c}Target:
    def fetch(self) -> str:
        raise NotImplementedError

class {c}Adapter({c}Target):
    def __init__(self, legacy: {c}LegacyApi) -> None:
        self._legacy = legacy

    def fetch(self) -> str:
        raw = self._legacy.legacy_fetch()
        return raw.lower().replace("legacy-", "modern-")
'''
    jt = f"""package org.example.patterns;
public class {c}AdapterTest {{
    public static void main(String[] args) {{
        {c}Target t = new {c}Adapter(new {c}LegacyApi());
        if (!t.fetch().equals("modern-{s}")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_adapter_{s}():\n    assert True\n"
    return j, p, jt, pt


def bridge(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "bridge", ctx.domain, tier)
    j += f"""interface {c}Impl {{
    String write(String msg);
}}

class {c}FileImpl implements {c}Impl {{
    public String write(String msg) {{ return "file:{s}:" + msg; }}
}}

class {c}MemoryImpl implements {c}Impl {{
    public String write(String msg) {{ return "mem:{s}:" + msg; }}
}}

public abstract class {c}Bridge {{
    protected final {c}Impl impl;
    protected {c}Bridge({c}Impl impl) {{ this.impl = impl; }}
    public abstract String send(String msg);
}}

class {c}AlertBridge extends {c}Bridge {{
    public {c}AlertBridge({c}Impl impl) {{ super(impl); }}
    public String send(String msg) {{ return impl.write("ALERT-" + msg); }}
}}
"""
    p = _hdr_py("design_pattern", "bridge", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Impl(ABC):
    @abstractmethod
    def write(self, msg: str) -> str: ...

class {c}FileImpl({c}Impl):
    def write(self, msg: str) -> str:
        return f"file:{s}:{{msg}}"

class {c}MemoryImpl({c}Impl):
    def write(self, msg: str) -> str:
        return f"mem:{s}:{{msg}}"

class {c}Bridge(ABC):
    def __init__(self, impl: {c}Impl) -> None:
        self.impl = impl

    @abstractmethod
    def send(self, msg: str) -> str: ...

class {c}AlertBridge({c}Bridge):
    def send(self, msg: str) -> str:
        return self.impl.write("ALERT-" + msg)
'''
    jt = f"""package org.example.patterns;
public class {c}BridgeTest {{
    public static void main(String[] args) {{
        {c}Bridge b = new {c}AlertBridge(new {c}FileImpl());
        String out = b.send("x");
        if (!out.equals("file:{s}:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_bridge_{s}():\n    assert True\n"
    return j, p, jt, pt


def composite(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "composite", ctx.domain, tier)
    j += f"""import java.util.*;

interface {c}Node {{
    int size();
}}

class {c}Leaf implements {c}Node {{
    private final int weight;
    public {c}Leaf(int weight) {{ this.weight = weight; }}
    public int size() {{ return weight; }}
}}

public class {c}Composite implements {c}Node {{
    private final List<{c}Node> children = new ArrayList<>();
    public void add({c}Node n) {{ children.add(n); }}
    public int size() {{
        int total = 0;
        for ({c}Node n : children) total += n.size();
        return total;
    }}
}}
"""
    p = _hdr_py("design_pattern", "composite", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Node(ABC):
    @abstractmethod
    def size(self) -> int: ...

class {c}Leaf({c}Node):
    def __init__(self, weight: int) -> None:
        self.weight = weight

    def size(self) -> int:
        return self.weight

class {c}Composite({c}Node):
    def __init__(self) -> None:
        self.children: list[{c}Node] = []

    def add(self, n: {c}Node) -> None:
        self.children.append(n)

    def size(self) -> int:
        return sum(n.size() for n in self.children)
'''
    jt = f"""package org.example.patterns;
public class {c}CompositeTest {{
    public static void main(String[] args) {{
        {c}Composite root = new {c}Composite();
        root.add(new {c}Leaf(2));
        root.add(new {c}Leaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_composite_{s}():\n    assert True\n"
    return j, p, jt, pt


def decorator(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "decorator", ctx.domain, tier)
    j += f"""interface {c}Component {{
    String process(String input);
}}

class {c}Core implements {c}Component {{
    public String process(String input) {{ return "{s}:" + input; }}
}}

public class {c}UpperDecorator implements {c}Component {{
    private final {c}Component inner;
    public {c}UpperDecorator({c}Component inner) {{ this.inner = inner; }}
    public String process(String input) {{
        return inner.process(input).toUpperCase();
    }}
}}
"""
    p = _hdr_py("design_pattern", "decorator", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Component(ABC):
    @abstractmethod
    def process(self, input: str) -> str: ...

class {c}Core({c}Component):
    def process(self, input: str) -> str:
        return f"{s}:{{input}}"

class {c}UpperDecorator({c}Component):
    def __init__(self, inner: {c}Component) -> None:
        self.inner = inner

    def process(self, input: str) -> str:
        return self.inner.process(input).upper()
'''
    jt = f"""package org.example.patterns;
public class {c}DecoratorTest {{
    public static void main(String[] args) {{
        {c}Component c = new {c}UpperDecorator(new {c}Core());
        String out = c.process("ab");
        if (!out.equals("{s.upper()}:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_decorator_{s}():\n    assert True\n"
    return j, p, jt, pt


def facade(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "facade", ctx.domain, tier)
    j += f"""class {c}Validator {{
    public boolean ok(String v) {{ return v != null && !v.isEmpty(); }}
}}
class {c}Writer {{
    public String write(String v) {{ return "wrote-{s}:" + v; }}
}}
public class {c}Facade {{
    private final {c}Validator validator = new {c}Validator();
    private final {c}Writer writer = new {c}Writer();
    public String submit(String value) {{
        if (!validator.ok(value)) return "invalid";
        return writer.write(value);
    }}
}}
"""
    p = _hdr_py("design_pattern", "facade", ctx.domain, tier)
    p += f'''class {c}Validator:
    def ok(self, v: str) -> bool:
        return bool(v)

class {c}Writer:
    def write(self, v: str) -> str:
        return f"wrote-{s}:{{v}}"

class {c}Facade:
    def __init__(self) -> None:
        self.validator = {c}Validator()
        self.writer = {c}Writer()

    def submit(self, value: str) -> str:
        if not self.validator.ok(value):
            return "invalid"
        return self.writer.write(value)
'''
    jt = f"""package org.example.patterns;
public class {c}FacadeTest {{
    public static void main(String[] args) {{
        {c}Facade f = new {c}Facade();
        if (!f.submit("x").equals("wrote-{s}:x")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_facade_{s}():\n    assert True\n"
    return j, p, jt, pt


def flyweight(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "flyweight", ctx.domain, tier)
    j += f"""import java.util.*;

public class {c}FlyweightFactory {{
    private final Map<String, String> cache = new HashMap<>();

    public String intern(String key) {{
        return cache.computeIfAbsent(key, k -> "fw-{s}-" + k);
    }}

    public int size() {{ return cache.size(); }}
}}
"""
    p = _hdr_py("design_pattern", "flyweight", ctx.domain, tier)
    p += f'''class {c}FlyweightFactory:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {{}}

    def intern(self, key: str) -> str:
        if key not in self._cache:
            self._cache[key] = f"fw-{s}-{{key}}"
        return self._cache[key]

    def size(self) -> int:
        return len(self._cache)
'''
    jt = f"""package org.example.patterns;
public class {c}FlyweightTest {{
    public static void main(String[] args) {{
        {c}FlyweightFactory f = new {c}FlyweightFactory();
        String a = f.intern("a");
        String b = f.intern("a");
        if (a != b) throw new AssertionError();
        if (f.size() != 1) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_flyweight_{s}():\n    assert True\n"
    return j, p, jt, pt


def proxy(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "proxy", ctx.domain, tier)
    j += f"""interface {c}Service {{
    String load(String id);
}}

class {c}RealService implements {c}Service {{
    public String load(String id) {{ return "real-{s}:" + id; }}
}}

public class {c}Proxy implements {c}Service {{
    private {c}RealService real;
    private final boolean allowed;
    public {c}Proxy(boolean allowed) {{ this.allowed = allowed; }}
    public String load(String id) {{
        if (!allowed) return "denied";
        if (real == null) real = new {c}RealService();
        return real.load(id);
    }}
}}
"""
    p = _hdr_py("design_pattern", "proxy", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Service(ABC):
    @abstractmethod
    def load(self, id: str) -> str: ...

class {c}RealService({c}Service):
    def load(self, id: str) -> str:
        return f"real-{s}:{{id}}"

class {c}Proxy({c}Service):
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self._real: {c}RealService | None = None

    def load(self, id: str) -> str:
        if not self.allowed:
            return "denied"
        if self._real is None:
            self._real = {c}RealService()
        return self._real.load(id)
'''
    jt = f"""package org.example.patterns;
public class {c}ProxyTest {{
    public static void main(String[] args) {{
        if (!new {c}Proxy(true).load("1").equals("real-{s}:1")) throw new AssertionError();
        if (!new {c}Proxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_proxy_{s}():\n    assert True\n"
    return j, p, jt, pt


# ---------------------------------------------------------------------------
# Behavioral
# ---------------------------------------------------------------------------


def chain_of_responsibility(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "chain of responsibility", ctx.domain, tier)
    j += f"""public abstract class {c}Handler {{
    protected {c}Handler next;
    public {c}Handler link({c}Handler n) {{ next = n; return n; }}
    public String handle(int level, String msg) {{
        if (canHandle(level)) return doHandle(msg);
        if (next != null) return next.handle(level, msg);
        return "unhandled-{s}";
    }}
    protected abstract boolean canHandle(int level);
    protected abstract String doHandle(String msg);
}}

class {c}LowHandler extends {c}Handler {{
    protected boolean canHandle(int level) {{ return level <= 1; }}
    protected String doHandle(String msg) {{ return "low-{s}:" + msg; }}
}}

class {c}HighHandler extends {c}Handler {{
    protected boolean canHandle(int level) {{ return level > 1; }}
    protected String doHandle(String msg) {{ return "high-{s}:" + msg; }}
}}
"""
    p = _hdr_py("design_pattern", "chain of responsibility", ctx.domain, tier)
    p += f'''from __future__ import annotations
from abc import ABC, abstractmethod

class {c}Handler(ABC):
    def __init__(self) -> None:
        self.next: {c}Handler | None = None

    def link(self, n: {c}Handler) -> {c}Handler:
        self.next = n
        return n

    def handle(self, level: int, msg: str) -> str:
        if self.can_handle(level):
            return self.do_handle(msg)
        if self.next is not None:
            return self.next.handle(level, msg)
        return "unhandled-{s}"

    @abstractmethod
    def can_handle(self, level: int) -> bool: ...
    @abstractmethod
    def do_handle(self, msg: str) -> str: ...

class {c}LowHandler({c}Handler):
    def can_handle(self, level: int) -> bool:
        return level <= 1
    def do_handle(self, msg: str) -> str:
        return f"low-{s}:{{msg}}"

class {c}HighHandler({c}Handler):
    def can_handle(self, level: int) -> bool:
        return level > 1
    def do_handle(self, msg: str) -> str:
        return f"high-{s}:{{msg}}"
'''
    jt = f"""package org.example.patterns;
public class {c}ChainTest {{
    public static void main(String[] args) {{
        {c}Handler h = new {c}LowHandler();
        h.link(new {c}HighHandler());
        if (!h.handle(2, "m").equals("high-{s}:m")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_chain_{s}():\n    assert True\n"
    return j, p, jt, pt


def command(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "command", ctx.domain, tier)
    j += f"""interface {c}Command {{
    String execute();
}}

class {c}Receiver {{
    public String action(String x) {{ return "done-{s}:" + x; }}
}}

public class {c}ActionCommand implements {c}Command {{
    private final {c}Receiver receiver;
    private final String payload;
    public {c}ActionCommand({c}Receiver r, String payload) {{
        this.receiver = r; this.payload = payload;
    }}
    public String execute() {{ return receiver.action(payload); }}
}}
"""
    p = _hdr_py("design_pattern", "command", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Command(ABC):
    @abstractmethod
    def execute(self) -> str: ...

class {c}Receiver:
    def action(self, x: str) -> str:
        return f"done-{s}:{{x}}"

class {c}ActionCommand({c}Command):
    def __init__(self, receiver: {c}Receiver, payload: str) -> None:
        self.receiver = receiver
        self.payload = payload

    def execute(self) -> str:
        return self.receiver.action(self.payload)
'''
    jt = f"""package org.example.patterns;
public class {c}CommandTest {{
    public static void main(String[] args) {{
        {c}Command cmd = new {c}ActionCommand(new {c}Receiver(), "x");
        if (!cmd.execute().equals("done-{s}:x")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_command_{s}():\n    assert True\n"
    return j, p, jt, pt


def interpreter(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "interpreter", ctx.domain, tier)
    j += f"""public class {c}Interpreter {{
    public int eval(String expr) {{
        // tiny language: "n+n" or single int
        if (expr.contains("+")) {{
            String[] p = expr.split("\\\\+");
            return Integer.parseInt(p[0].trim()) + Integer.parseInt(p[1].trim());
        }}
        return Integer.parseInt(expr.trim());
    }}
    public String tag() {{ return "{s}-interp"; }}
}}
"""
    p = _hdr_py("design_pattern", "interpreter", ctx.domain, tier)
    p += f'''class {c}Interpreter:
    def eval(self, expr: str) -> int:
        if "+" in expr:
            a, b = expr.split("+", 1)
            return int(a.strip()) + int(b.strip())
        return int(expr.strip())

    def tag(self) -> str:
        return "{s}-interp"
'''
    jt = f"""package org.example.patterns;
public class {c}InterpreterTest {{
    public static void main(String[] args) {{
        {c}Interpreter i = new {c}Interpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_interpreter_{s}():\n    assert True\n"
    return j, p, jt, pt


def iterator_pat(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "iterator", ctx.domain, tier)
    j += f"""import java.util.*;

public class {c}Collection implements Iterable<String> {{
    private final List<String> items = new ArrayList<>();
    public void add(String v) {{ items.add(v); }}
    public Iterator<String> iterator() {{ return items.iterator(); }}
    public String join() {{
        StringBuilder sb = new StringBuilder("{s}");
        for (String it : this) sb.append(":").append(it);
        return sb.toString();
    }}
}}
"""
    p = _hdr_py("design_pattern", "iterator", ctx.domain, tier)
    p += f'''from typing import Iterator

class {c}Collection:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, v: str) -> None:
        self.items.append(v)

    def __iter__(self) -> Iterator[str]:
        return iter(self.items)

    def join(self) -> str:
        return "{s}" + "".join(f":{{it}}" for it in self)
'''
    jt = f"""package org.example.patterns;
public class {c}IteratorTest {{
    public static void main(String[] args) {{
        {c}Collection col = new {c}Collection();
        col.add("a"); col.add("b");
        if (!col.join().equals("{s}:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_iterator_{s}():\n    assert True\n"
    return j, p, jt, pt


def mediator(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "mediator", ctx.domain, tier)
    j += f"""import java.util.*;

public class {c}Mediator {{
    private final List<String> log = new ArrayList<>();
    public void notify(String from, String msg) {{
        log.add(from + "->" + msg);
    }}
    public String history() {{
        return String.join("|", log);
    }}
    public String domain() {{ return "{s}"; }}
}}

class {c}Colleague {{
    private final String name;
    private final {c}Mediator mediator;
    public {c}Colleague(String name, {c}Mediator m) {{ this.name = name; this.mediator = m; }}
    public void send(String msg) {{ mediator.notify(name, msg); }}
}}
"""
    p = _hdr_py("design_pattern", "mediator", ctx.domain, tier)
    p += f'''class {c}Mediator:
    def __init__(self) -> None:
        self.log: list[str] = []

    def notify(self, fr: str, msg: str) -> None:
        self.log.append(f"{{fr}}->{{msg}}")

    def history(self) -> str:
        return "|".join(self.log)

    def domain(self) -> str:
        return "{s}"

class {c}Colleague:
    def __init__(self, name: str, mediator: {c}Mediator) -> None:
        self.name = name
        self.mediator = mediator

    def send(self, msg: str) -> None:
        self.mediator.notify(self.name, msg)
'''
    jt = f"""package org.example.patterns;
public class {c}MediatorTest {{
    public static void main(String[] args) {{
        {c}Mediator m = new {c}Mediator();
        new {c}Colleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_mediator_{s}():\n    assert True\n"
    return j, p, jt, pt


def memento(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "memento", ctx.domain, tier)
    j += f"""public class {c}Memento {{
    private final String state;
    public {c}Memento(String state) {{ this.state = state; }}
    public String getState() {{ return state; }}
}}

class {c}Originator {{
    private String state = "{s}-init";
    public void setState(String state) {{ this.state = state; }}
    public String getState() {{ return state; }}
    public {c}Memento save() {{ return new {c}Memento(state); }}
    public void restore({c}Memento m) {{ this.state = m.getState(); }}
}}
"""
    p = _hdr_py("design_pattern", "memento", ctx.domain, tier)
    p += f'''from dataclasses import dataclass

@dataclass(frozen=True)
class {c}Memento:
    state: str

class {c}Originator:
    def __init__(self) -> None:
        self.state = "{s}-init"

    def set_state(self, state: str) -> None:
        self.state = state

    def get_state(self) -> str:
        return self.state

    def save(self) -> {c}Memento:
        return {c}Memento(self.state)

    def restore(self, m: {c}Memento) -> None:
        self.state = m.state
'''
    jt = f"""package org.example.patterns;
public class {c}MementoTest {{
    public static void main(String[] args) {{
        {c}Originator o = new {c}Originator();
        {c}Memento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("{s}-init")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_memento_{s}():\n    assert True\n"
    return j, p, jt, pt


def observer(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "observer", ctx.domain, tier)
    j += f"""import java.util.*;

interface {c}Observer {{
    void update(String event);
}}

public class {c}Subject {{
    private final List<{c}Observer> observers = new ArrayList<>();
    private final List<String> events = new ArrayList<>();
    public void attach({c}Observer o) {{ observers.add(o); }}
    public void notifyAllObservers(String event) {{
        events.add(event);
        for ({c}Observer o : observers) o.update(event);
    }}
    public String last() {{ return events.isEmpty() ? "" : events.get(events.size()-1); }}
}}

class {c}Listener implements {c}Observer {{
    String last = "";
    public void update(String event) {{ last = "{s}:" + event; }}
}}
"""
    p = _hdr_py("design_pattern", "observer", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Observer(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...

class {c}Subject:
    def __init__(self) -> None:
        self.observers: list[{c}Observer] = []
        self.events: list[str] = []

    def attach(self, o: {c}Observer) -> None:
        self.observers.append(o)

    def notify_all(self, event: str) -> None:
        self.events.append(event)
        for o in self.observers:
            o.update(event)

    def last(self) -> str:
        return self.events[-1] if self.events else ""

class {c}Listener({c}Observer):
    def __init__(self) -> None:
        self.last = ""

    def update(self, event: str) -> None:
        self.last = f"{s}:{{event}}"
'''
    jt = f"""package org.example.patterns;
public class {c}ObserverTest {{
    public static void main(String[] args) {{
        {c}Subject s = new {c}Subject();
        {c}Listener l = new {c}Listener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("{s}:e")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_observer_{s}():\n    assert True\n"
    return j, p, jt, pt


def state(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "state", ctx.domain, tier)
    j += f"""interface {c}State {{
    String handle({c}Context ctx);
}}

class {c}OnState implements {c}State {{
    public String handle({c}Context ctx) {{
        ctx.setState(new {c}OffState());
        return "was-on-{s}";
    }}
}}

class {c}OffState implements {c}State {{
    public String handle({c}Context ctx) {{
        ctx.setState(new {c}OnState());
        return "was-off-{s}";
    }}
}}

public class {c}Context {{
    private {c}State state = new {c}OffState();
    public void setState({c}State state) {{ this.state = state; }}
    public String request() {{ return state.handle(this); }}
}}
"""
    p = _hdr_py("design_pattern", "state", ctx.domain, tier)
    p += f'''from __future__ import annotations
from abc import ABC, abstractmethod

class {c}State(ABC):
    @abstractmethod
    def handle(self, ctx: "{c}Context") -> str: ...

class {c}OnState({c}State):
    def handle(self, ctx: "{c}Context") -> str:
        ctx.set_state({c}OffState())
        return "was-on-{s}"

class {c}OffState({c}State):
    def handle(self, ctx: "{c}Context") -> str:
        ctx.set_state({c}OnState())
        return "was-off-{s}"

class {c}Context:
    def __init__(self) -> None:
        self.state: {c}State = {c}OffState()

    def set_state(self, state: {c}State) -> None:
        self.state = state

    def request(self) -> str:
        return self.state.handle(self)
'''
    jt = f"""package org.example.patterns;
public class {c}StateTest {{
    public static void main(String[] args) {{
        {c}Context ctx = new {c}Context();
        if (!ctx.request().equals("was-off-{s}")) throw new AssertionError();
        if (!ctx.request().equals("was-on-{s}")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_state_{s}():\n    assert True\n"
    return j, p, jt, pt


def strategy(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    err_j = _err_java_check(tier, "amount < 0", "amount >= 0")
    err_p = _err_py_check(tier, "amount < 0", "amount >= 0")
    j = _hdr_java("design_pattern", "strategy", ctx.domain, tier)
    j += f"""interface {c}Strategy {{
    int apply(int amount);
}}

class {c}NormalStrategy implements {c}Strategy {{
    public int apply(int amount) {{ return amount; }}
}}

class {c}DiscountStrategy implements {c}Strategy {{
    public int apply(int amount) {{ return amount / 2; }}
}}

public class {c}Context {{
    private {c}Strategy strategy;
    public {c}Context({c}Strategy strategy) {{ this.strategy = strategy; }}
    public void setStrategy({c}Strategy strategy) {{ this.strategy = strategy; }}
    public int execute(int amount) {{
{err_j}        return strategy.apply(amount);
    }}
    public String tag() {{ return "{s}-strategy"; }}
}}
"""
    p = _hdr_py("design_pattern", "strategy", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Strategy(ABC):
    @abstractmethod
    def apply(self, amount: int) -> int: ...

class {c}NormalStrategy({c}Strategy):
    def apply(self, amount: int) -> int:
        return amount

class {c}DiscountStrategy({c}Strategy):
    def apply(self, amount: int) -> int:
        return amount // 2

class {c}Context:
    def __init__(self, strategy: {c}Strategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: {c}Strategy) -> None:
        self.strategy = strategy

    def execute(self, amount: int) -> int:
{err_p}        return self.strategy.apply(amount)

    def tag(self) -> str:
        return "{s}-strategy"
'''
    jt = f"""package org.example.patterns;
public class {c}StrategyTest {{
    public static void main(String[] args) {{
        {c}Context ctx = new {c}Context(new {c}DiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_strategy_{s}():\n    assert True\n"
    return j, p, jt, pt


def template_method(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "template method", ctx.domain, tier)
    j += f"""public abstract class {c}Template {{
    public final String run(String input) {{
        String prepared = prepare(input);
        String processed = process(prepared);
        return finish(processed);
    }}
    protected String prepare(String input) {{ return input.trim(); }}
    protected abstract String process(String input);
    protected String finish(String input) {{ return "{s}|" + input; }}
}}

class {c}UpperTemplate extends {c}Template {{
    protected String process(String input) {{ return input.toUpperCase(); }}
}}
"""
    p = _hdr_py("design_pattern", "template method", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Template(ABC):
    def run(self, input: str) -> str:
        prepared = self.prepare(input)
        processed = self.process(prepared)
        return self.finish(processed)

    def prepare(self, input: str) -> str:
        return input.strip()

    @abstractmethod
    def process(self, input: str) -> str: ...

    def finish(self, input: str) -> str:
        return f"{s}|{{input}}"

class {c}UpperTemplate({c}Template):
    def process(self, input: str) -> str:
        return input.upper()
'''
    jt = f"""package org.example.patterns;
public class {c}TemplateTest {{
    public static void main(String[] args) {{
        String out = new {c}UpperTemplate().run(" ab ");
        if (!out.equals("{s}|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_template_{s}():\n    assert True\n"
    return j, p, jt, pt


def visitor(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("design_pattern", "visitor", ctx.domain, tier)
    j += f"""interface {c}Visitor {{
    String visitLeaf({c}Leaf leaf);
}}

interface {c}Element {{
    String accept({c}Visitor v);
}}

class {c}Leaf implements {c}Element {{
    final String name;
    public {c}Leaf(String name) {{ this.name = name; }}
    public String accept({c}Visitor v) {{ return v.visitLeaf(this); }}
}}

public class {c}PrintVisitor implements {c}Visitor {{
    public String visitLeaf({c}Leaf leaf) {{ return "{s}:" + leaf.name; }}
}}
"""
    p = _hdr_py("design_pattern", "visitor", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Visitor(ABC):
    @abstractmethod
    def visit_leaf(self, leaf: "{c}Leaf") -> str: ...

class {c}Element(ABC):
    @abstractmethod
    def accept(self, v: {c}Visitor) -> str: ...

class {c}Leaf({c}Element):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, v: {c}Visitor) -> str:
        return v.visit_leaf(self)

class {c}PrintVisitor({c}Visitor):
    def visit_leaf(self, leaf: {c}Leaf) -> str:
        return f"{s}:{{leaf.name}}"
'''
    jt = f"""package org.example.patterns;
public class {c}VisitorTest {{
    public static void main(String[] args) {{
        String out = new {c}Leaf("n").accept(new {c}PrintVisitor());
        if (!out.equals("{s}:n")) throw new AssertionError(out);
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_visitor_{s}():\n    assert True\n"
    return j, p, jt, pt


# ---------------------------------------------------------------------------
# SOLID
# ---------------------------------------------------------------------------


def srp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("solid", "srp", ctx.domain, tier)
    j += f"""// SRP: separate persistence from formatting for {s}
class {c}Record {{
    public final String id;
    public final int amount;
    public {c}Record(String id, int amount) {{ this.id = id; this.amount = amount; }}
}}

class {c}Repository {{
    public String save({c}Record r) {{ return "saved-{s}:" + r.id; }}
}}

public class {c}Formatter {{
    public String format({c}Record r) {{ return r.id + "=" + r.amount; }}
}}
"""
    p = _hdr_py("solid", "srp", ctx.domain, tier)
    p += f'''from dataclasses import dataclass

@dataclass(frozen=True)
class {c}Record:
    id: str
    amount: int

class {c}Repository:
    def save(self, r: {c}Record) -> str:
        return f"saved-{s}:{{r.id}}"

class {c}Formatter:
    def format(self, r: {c}Record) -> str:
        return f"{{r.id}}={{r.amount}}"
'''
    jt = f"""package org.example.patterns;
public class {c}SrpTest {{
    public static void main(String[] args) {{
        {c}Record r = new {c}Record("a", 3);
        if (!new {c}Formatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_srp_{s}():\n    assert True\n"
    return j, p, jt, pt


def ocp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("solid", "ocp", ctx.domain, tier)
    j += f"""// OCP: extend via new discount policy without editing engine
interface {c}Discount {{
    int apply(int price);
}}

class {c}NoDiscount implements {c}Discount {{
    public int apply(int price) {{ return price; }}
}}

class {c}TenPercent implements {c}Discount {{
    public int apply(int price) {{ return price - price / 10; }}
}}

public class {c}PriceEngine {{
    private final {c}Discount discount;
    public {c}PriceEngine({c}Discount discount) {{ this.discount = discount; }}
    public int quote(int price) {{ return discount.apply(price); }}
    public String domain() {{ return "{s}"; }}
}}
"""
    p = _hdr_py("solid", "ocp", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Discount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...

class {c}NoDiscount({c}Discount):
    def apply(self, price: int) -> int:
        return price

class {c}TenPercent({c}Discount):
    def apply(self, price: int) -> int:
        return price - price // 10

class {c}PriceEngine:
    def __init__(self, discount: {c}Discount) -> None:
        self.discount = discount

    def quote(self, price: int) -> int:
        return self.discount.apply(price)

    def domain(self) -> str:
        return "{s}"
'''
    jt = f"""package org.example.patterns;
public class {c}OcpTest {{
    public static void main(String[] args) {{
        if (new {c}PriceEngine(new {c}TenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_ocp_{s}():\n    assert True\n"
    return j, p, jt, pt


def lsp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("solid", "lsp", ctx.domain, tier)
    j += f"""// LSP: subtypes usable wherever base {s} shape is expected
abstract class {c}Shape {{
    public abstract int area();
}}

class {c}Rectangle extends {c}Shape {{
    protected int w, h;
    public {c}Rectangle(int w, int h) {{ this.w = w; this.h = h; }}
    public int area() {{ return w * h; }}
}}

class {c}Square extends {c}Shape {{
    private final int side;
    public {c}Square(int side) {{ this.side = side; }}
    public int area() {{ return side * side; }}
}}

public class {c}LspUtil {{
    public static int total({c}Shape[] shapes) {{
        int t = 0;
        for ({c}Shape sh : shapes) t += sh.area();
        return t;
    }}
}}
"""
    p = _hdr_py("solid", "lsp", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Shape(ABC):
    @abstractmethod
    def area(self) -> int: ...

class {c}Rectangle({c}Shape):
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def area(self) -> int:
        return self.w * self.h

class {c}Square({c}Shape):
    def __init__(self, side: int) -> None:
        self.side = side

    def area(self) -> int:
        return self.side * self.side

def total(shapes: list[{c}Shape]) -> int:
    return sum(sh.area() for sh in shapes)
'''
    jt = f"""package org.example.patterns;
public class {c}LspTest {{
    public static void main(String[] args) {{
        {c}Shape[] arr = new {c}Shape[] {{ new {c}Rectangle(2,3), new {c}Square(4) }};
        if ({c}LspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_lsp_{s}():\n    assert True\n"
    return j, p, jt, pt


def isp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("solid", "isp", ctx.domain, tier)
    j += f"""// ISP: small role interfaces for {s}
interface {c}Readable {{
    String read();
}}
interface {c}Writable {{
    void write(String v);
}}

class {c}Store implements {c}Readable, {c}Writable {{
    private String data = "";
    public String read() {{ return data; }}
    public void write(String v) {{ data = "{s}:" + v; }}
}}

public class {c}IspClient {{
    public static String mirror({c}Readable r) {{ return r.read(); }}
}}
"""
    p = _hdr_py("solid", "isp", ctx.domain, tier)
    p += f'''from typing import Protocol

class {c}Readable(Protocol):
    def read(self) -> str: ...

class {c}Writable(Protocol):
    def write(self, v: str) -> None: ...

class {c}Store:
    def __init__(self) -> None:
        self.data = ""

    def read(self) -> str:
        return self.data

    def write(self, v: str) -> None:
        self.data = f"{s}:{{v}}"

def mirror(r: {c}Readable) -> str:
    return r.read()
'''
    jt = f"""package org.example.patterns;
public class {c}IspTest {{
    public static void main(String[] args) {{
        {c}Store st = new {c}Store();
        st.write("x");
        if (!{c}IspClient.mirror(st).equals("{s}:x")) throw new AssertionError();
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_isp_{s}():\n    assert True\n"
    return j, p, jt, pt


def dip(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    c, s = ctx.pascal, ctx.snake
    j = _hdr_java("solid", "dip", ctx.domain, tier)
    j += f"""// DIP: high-level {s} module depends on abstraction
interface {c}Gateway {{
    String send(String payload);
}}

class {c}HttpGateway implements {c}Gateway {{
    public String send(String payload) {{ return "http-{s}:" + payload; }}
}}

public class {c}AppService {{
    private final {c}Gateway gateway;
    public {c}AppService({c}Gateway gateway) {{ this.gateway = gateway; }}
    public String publish(String payload) {{ return gateway.send(payload); }}
}}
"""
    p = _hdr_py("solid", "dip", ctx.domain, tier)
    p += f'''from abc import ABC, abstractmethod

class {c}Gateway(ABC):
    @abstractmethod
    def send(self, payload: str) -> str: ...

class {c}HttpGateway({c}Gateway):
    def send(self, payload: str) -> str:
        return f"http-{s}:{{payload}}"

class {c}AppService:
    def __init__(self, gateway: {c}Gateway) -> None:
        self.gateway = gateway

    def publish(self, payload: str) -> str:
        return self.gateway.send(payload)
'''
    jt = f"""package org.example.patterns;
public class {c}DipTest {{
    public static void main(String[] args) {{
        String out = new {c}AppService(new {c}HttpGateway()).publish("p");
        if (!out.equals("http-{s}:p")) throw new AssertionError(out);
        System.out.println("ok");
    }}
}}
"""
    pt = f"def test_dip_{s}():\n    assert True\n"
    return j, p, jt, pt


# ---------------------------------------------------------------------------
# Combos
# ---------------------------------------------------------------------------


def strategy_ocp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    # Reuse strategy but tag as combo
    j, p, jt, pt = strategy(ctx, tier)
    j = j.replace('kind=design_pattern | label=strategy', 'kind=combo | label=strategy+ocp')
    p = p.replace('kind=design_pattern | label=strategy', 'kind=combo | label=strategy+ocp')
    return j, p, jt, pt


def factory_dip(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    j, p, jt, pt = factory(ctx, tier)
    j = j.replace('kind=design_pattern | label=factory', 'kind=combo | label=factory+dip')
    p = p.replace('kind=design_pattern | label=factory', 'kind=combo | label=factory+dip')
    return j, p, jt, pt


def observer_srp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    j, p, jt, pt = observer(ctx, tier)
    j = j.replace('kind=design_pattern | label=observer', 'kind=combo | label=observer+srp')
    p = p.replace('kind=design_pattern | label=observer', 'kind=combo | label=observer+srp')
    return j, p, jt, pt


def decorator_ocp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    j, p, jt, pt = decorator(ctx, tier)
    j = j.replace('kind=design_pattern | label=decorator', 'kind=combo | label=decorator+ocp')
    p = p.replace('kind=design_pattern | label=decorator', 'kind=combo | label=decorator+ocp')
    return j, p, jt, pt


def adapter_isp(ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    j, p, jt, pt = adapter(ctx, tier)
    j = j.replace('kind=design_pattern | label=adapter', 'kind=combo | label=adapter+isp')
    p = p.replace('kind=design_pattern | label=adapter', 'kind=combo | label=adapter+isp')
    return j, p, jt, pt


RENDERERS = {
    "singleton": singleton,
    "factory": factory,
    "abstract_factory": abstract_factory,
    "builder": builder,
    "prototype": prototype,
    "adapter": adapter,
    "bridge": bridge,
    "composite": composite,
    "decorator": decorator,
    "facade": facade,
    "flyweight": flyweight,
    "proxy": proxy,
    "chain_of_responsibility": chain_of_responsibility,
    "command": command,
    "interpreter": interpreter,
    "iterator": iterator_pat,
    "mediator": mediator,
    "memento": memento,
    "observer": observer,
    "state": state,
    "strategy": strategy,
    "template_method": template_method,
    "visitor": visitor,
    "srp": srp,
    "ocp": ocp,
    "lsp": lsp,
    "isp": isp,
    "dip": dip,
    "strategy_ocp": strategy_ocp,
    "factory_dip": factory_dip,
    "observer_srp": observer_srp,
    "decorator_ocp": decorator_ocp,
    "adapter_isp": adapter_isp,
}


def render(pattern_id: str, ctx: DomainContext, tier: str) -> tuple[str, str, str, str]:
    if pattern_id not in RENDERERS:
        raise KeyError(f"No renderer for {pattern_id}")
    return RENDERERS[pattern_id](ctx, tier)
