import pytest

from statemachine import State
from statemachine import StateMachine


class MinimalMachine(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b) | b.to(a)


class MachineWithNoArgCallbacks(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b)

    def on_enter_b(self):
        pass

    def on_exit_a(self):
        pass

    def on_go(self):
        pass


class MachineWithKwargsCallbacks(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b)

    def on_enter_b(self, event, source, target):
        pass

    def on_exit_a(self, machine, model):
        pass

    def on_go(self, event_data, transition):
        pass


class MachineWithVarKwargsCallbacks(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b)

    def on_enter_b(self, **kwargs):
        pass

    def on_exit_a(self, *args, **kwargs):
        pass

    def on_go(self, *args, **kwargs):
        pass


class MachineWithConditions(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b, cond="can_go")

    def can_go(self):
        return True

    def on_go(self):
        pass


class MachineWithManyCallbacks(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b)

    def on_enter_b(self):
        pass

    def on_exit_a(self):
        pass

    def before_go(self):
        pass

    def on_go(self):
        pass

    def after_go(self):
        pass


class CyclicMachine(StateMachine):
    a = State(initial=True)
    b = State()

    forward = a.to(b)
    backward = b.to(a)

    def on_enter_a(self):
        pass

    def on_enter_b(self):
        pass


def run_transitions_minimal(sm, n):
    for _ in range(n):
        sm.go()


def run_transitions_cyclic(sm, n):
    for _ in range(n):
        sm.forward()
        sm.backward()


@pytest.mark.slow()
def test_bench_minimal_machine(benchmark):
    def setup():
        return (MinimalMachine(),), {}

    benchmark.pedantic(
        lambda sm: sm.go(),
        setup=setup,
        rounds=50,
        iterations=1000,
    )


@pytest.mark.slow()
def test_bench_no_arg_callbacks(benchmark):
    def target():
        sm = MachineWithNoArgCallbacks()
        sm.go()

    benchmark.pedantic(target, rounds=50, iterations=1000)


@pytest.mark.slow()
def test_bench_kwargs_callbacks(benchmark):
    def target():
        sm = MachineWithKwargsCallbacks()
        sm.go()

    benchmark.pedantic(target, rounds=50, iterations=1000)


@pytest.mark.slow()
def test_bench_varkwargs_callbacks(benchmark):
    def target():
        sm = MachineWithVarKwargsCallbacks()
        sm.go()

    benchmark.pedantic(target, rounds=50, iterations=1000)


@pytest.mark.slow()
def test_bench_conditions(benchmark):
    def target():
        sm = MachineWithConditions()
        sm.go()

    benchmark.pedantic(target, rounds=50, iterations=1000)


@pytest.mark.slow()
def test_bench_many_callbacks(benchmark):
    def target():
        sm = MachineWithManyCallbacks()
        sm.go()

    benchmark.pedantic(target, rounds=50, iterations=1000)


@pytest.mark.slow()
def test_bench_cyclic_transitions(benchmark):
    sm = CyclicMachine()

    def target():
        sm.forward()
        sm.backward()

    benchmark.pedantic(target, rounds=50, iterations=1000)


@pytest.mark.slow()
def test_bench_high_frequency_transitions(benchmark):
    sm = CyclicMachine()

    def target():
        for _ in range(100):
            sm.forward()
            sm.backward()

    benchmark.pedantic(target, rounds=10, iterations=100)


from statemachine.dispatcher import skip_signature_validation


class MachineWithVarKwargsOnly(StateMachine):
    a = State(initial=True)
    b = State()

    go = a.to(b) | b.to(a)

    def on_enter_a(self, **kwargs):
        pass

    def on_enter_b(self, **kwargs):
        pass

    def on_go(self, **kwargs):
        pass


@pytest.mark.slow()
def test_bench_optimized_cyclic(benchmark):
    sm = MachineWithVarKwargsOnly()

    def target():
        with skip_signature_validation():
            for _ in range(100):
                sm.go()

    benchmark.pedantic(target, rounds=10, iterations=100)


@pytest.mark.slow()
def test_bench_baseline_cyclic(benchmark):
    sm = MachineWithVarKwargsOnly()

    def target():
        for _ in range(100):
            sm.go()

    benchmark.pedantic(target, rounds=10, iterations=100)
