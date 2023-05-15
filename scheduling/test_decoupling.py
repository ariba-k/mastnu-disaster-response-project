import sys, os

from dc_checking.temporal_network import TemporalNetwork, SimpleTemporalConstraint, SimpleContingentTemporalConstraint
#  from dc_checker.dc_be import DCCheckerBE

from networks import MaSTNU
from solve_decoupling import solve_decoupling, solve_decoupling_milp, preprocess_networks
from decouple_milp import NONE, MIN_TIME_SPAN, MAX_FLEXIBILITY, MAX_FLEXIBILITY_NAIVE, MAX_FLEXIBILITY_NEG_CKJ, MIN_LB_TIME_SPAN, MIN_LB_UB_TIME_SPAN, MIN_BIJ

#  def test_compilation():
#      """Test compilation"""

#      #  A ========> (B) ----------> (C)
#      #  |                          /
#      #  D ===> E -----> F =====> G/

#      ctc1 = SimpleContingentTemporalConstraint('A', 'B', lb=10, ub=15)
#      ctc2 = SimpleContingentTemporalConstraint('D', 'E', lb=5, ub=10)
#      ctc3 = SimpleContingentTemporalConstraint('F', 'G', lb=5, ub=10)
#      stc1 = SimpleTemporalConstraint('A', 'D', lb=0, ub=30)
#      stc2 = SimpleTemporalConstraint('E', 'F', lb=0, ub=30)
#      stc3 = SimpleTemporalConstraint('G', 'C', lb=0, ub=30)
#      constraints = [ctc1, ctc2, ctc3, stc1, stc2, stc3]
#      network = AgentNetwork("agent", constraints=constraints, shared_events=['B', 'C'], ref_event='z')

#      # Compilation using consistency
#      stn = stnu_to_stn(network)
#      compiler = DCCheckerBE(stn)
#      assert(compiler.is_controllable())
#      shared_events = network.get_shared_events()
#      ref_event = network.get_ref_event()
#      all_events = network.get_all_events()
#      eliminate_nodes = [e for e in all_events if e not in shared_events and not e == ref_event]
#      assert(len(eliminate_nodes) == 5)
#      suc, compiled_stn = compiler.compile_out_nodes(eliminate_nodes)
#      assert(suc)
#      #  print(compiled_stn.get_constraints())
#      for tc in compiled_stn.get_constraints():
#          assert(isinstance(tc, SimpleTemporalConstraint))
#          if tc.s == 'B':
#              assert(tc.ub == 100)
#          elif tc.s == 'C':
#              assert(tc.ub == 5)
#          else:
#              raise ValueError

#      # Compilation using strong controllability
#      shared_events = network.get_shared_events()
#      ref_event = network.get_ref_event()
#      all_events = network.get_all_events()
#      eliminate_nodes = [e for e in all_events if e not in shared_events and not e == ref_event]
#      suc, compiled_stnu = compile_stnu_to_stn(network, eliminate_nodes)
#      # If suc is False, it may be that the compilation using strong controllability is too restrictive
#      assert(suc)
#      # Compile the rest of the contingent links to STCs
#      compiled_stn = stnu_to_stn(compiled_stnu)
#      # Project out eliminated nodes
#      compiler = DCCheckerBE(compiled_stn)
#      # If suc is False, it may be that the compilation using strong controllability is too restrictive
#      assert(compiler.is_controllable())
#      all_events = compiled_stn.get_events()
#      eliminate_nodes = [e for e in all_events if e not in shared_events and not e == ref_event]
#      assert(len(eliminate_nodes) == 3)
#      suc, compiled_stn = compiler.compile_out_nodes(eliminate_nodes)
#      assert(suc)
#      #  print(compiled_stn.get_constraints())
#      for tc in compiled_stn.get_constraints():
#          assert(isinstance(tc, SimpleTemporalConstraint))
#          if tc.s == 'B':
#              assert(tc.ub == 90)
#          elif tc.s == 'C':
#              assert(tc.ub == -5)
#          else:
#              raise ValueError

def test_casanova_example(print_decoupling=False, plot=None):
    """Test example in Casanova's paper."""

    ext_conts = [SimpleContingentTemporalConstraint('a1', 'b1', 1, 4, 'c1'),
            SimpleContingentTemporalConstraint('b3', 'a3', 1, 5, 'c3')]
    ext_reqs = [SimpleTemporalConstraint('b2', 'a2', 6, 8, 'c2')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'a1', 0, 5, 'c4'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('a2', 'a3', 1, 10, 'c5'))
    agent_a_network.add_event('z')
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('b1', 'b2', 4, 6, 'c6'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('b2', 'b3', 6, 12, 'c7'))
    agent_b_network.add_event('z')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')


    ##################################
    # Distributed decoupling algorithm
    ##################################
    decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True)
    assert(decoupling)
    #  print(stats)

    if print_decoupling:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    #  if plot is not None:
    #      from plot import TNPlot, MaSTNUPlot
    #      ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
    #      ma_plt.plot()
    #      ma_plt.plot_with_decoupling(decoupling)
    #      ma_plt.plot_iterate_proof(decoupling)

    ################################
    # Centralized MILP method
    ################################
    decoupling, stats = solve_decoupling_milp(mastnu, output_stats=True)
    assert(decoupling)
    #  print(stats)

    if print_decoupling:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    #  if plot is not None:
    #      from plot import TNPlot, MaSTNUPlot
    #      ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
    #      ma_plt.plot()
    #      ma_plt.plot_with_decoupling(decoupling)
    #      ma_plt.plot_iterate_proof(decoupling)

def test_centralized_milp_preprocess_1():
    # Testcase1: Casanova's example, no preprocessing needed
    ext_conts = [SimpleContingentTemporalConstraint('a1', 'b1', 1, 4, 'c1'),
            SimpleContingentTemporalConstraint('b3', 'a3', 1, 5, 'c3')]
    ext_reqs = [SimpleTemporalConstraint('b2', 'a2', 6, 8, 'c2')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'a1', 0, 5, 'c4'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('a2', 'a3', 1, 10, 'c5'))
    agent_a_network.add_event('z')
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('b1', 'b2', 4, 6, 'c6'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('b2', 'b3', 6, 12, 'c7'))
    agent_b_network.add_event('z')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')

    new_mastnu, shared_events = preprocess_networks(mastnu)

    #  print(shared_events)
    assert(len(shared_events) == 7)
    #  print(new_mastnu.agent2network['agent-a'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-a'].get_constraints()) == 2)
    #  print(new_mastnu.agent2network['agent-a'].get_events())
    assert(len(new_mastnu.agent2network['agent-a'].get_events()) == 4)
    #  print(new_mastnu.agent2network['agent-b'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-b'].get_constraints()) == 2)
    #  print(new_mastnu.agent2network['agent-b'].get_events())
    assert(len(new_mastnu.agent2network['agent-b'].get_events()) == 4)

    decoupling = solve_decoupling_milp(mastnu)
    assert(decoupling)

def test_centralized_milp_preprocess_2():
    # Testcase2:
    """
                (C) --> (Ds) ---> (E)
                 |      ||         |
    A ==> B ==> (C) --> (De) ---> (E)
    For agent-b, B, C should have copies
    """
    ext_conts = [SimpleContingentTemporalConstraint('aD', 'bD', 1, 5, 'c3')]
    ext_reqs = [SimpleTemporalConstraint('aC', 'bC', 1, 10, 'c1'),
            SimpleTemporalConstraint('bE', 'aE', 0, 8, 'c2')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleTemporalConstraint('aC', 'aD', 0, 5, 'c4'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('aD', 'aE', 1, 10, 'c5'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'aC', lb=0, name='ref_preceding_a'))
    agent_a_network.add_event('z')
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bA', 'bB', 6, 12, 'c6'))
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bB', 'bC', 6, 12, 'c7'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('bC', 'bD', 0, 5, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('bD', 'bE', 1, 10, 'c9'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('z', 'bA', lb=0, name='ref_preceding_b'))
    agent_b_network.add_event('z')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')

    new_mastnu, shared_events = preprocess_networks(mastnu)

    #  print(shared_events)
    assert(len(shared_events) == 7)
    #  print(new_mastnu.agent2network['agent-a'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-a'].get_constraints()) == 3)
    #  print(new_mastnu.agent2network['agent-a'].get_events())
    assert(len(new_mastnu.agent2network['agent-a'].get_events()) == 4)
    #  print(new_mastnu.agent2network['agent-b'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-b'].get_constraints()) == 7)
    #  print(new_mastnu.agent2network['agent-b'].get_events())
    assert(len(new_mastnu.agent2network['agent-b'].get_events()) == 8)
    assert(new_mastnu.agent2network['agent-b'].id2constraint['c6'].e == 'bB-copy')
    assert(new_mastnu.agent2network['agent-b'].id2constraint['c7'].e == 'bC-copy')

    decoupling, conflicts = solve_decoupling(mastnu)
    assert(decoupling is None)
    decoupling = solve_decoupling_milp(mastnu)
    assert(decoupling is None)

def test_centralized_milp_preprocess_3():
    # Testcase3:
    """
                (Ce) --> (Ds) ---> (Es)
                 ||       ||        ||
    A ==> B ==> (Cs) --> (De) ---> (Ee)
                            ===> G
    For agent-b, B, C, D, E should have copies
    """
    ext_reqs = []
    ext_conts = [SimpleContingentTemporalConstraint('bC', 'aC', 0, 1, 'c1'),
            SimpleContingentTemporalConstraint('aE', 'bE', 0, 1, 'c2'),
            SimpleContingentTemporalConstraint('aD', 'bD', 0, 1, 'c3')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleTemporalConstraint('aC', 'aD', 0, 5, 'c4'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('aD', 'aE', 1, 10, 'c5'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'aC', lb=0, name='ref_preceding_a'))
    agent_a_network.add_event('z')
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bA', 'bB', 6, 12, 'c6'))
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bB', 'bC', 6, 12, 'c7'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('bC', 'bD', 0, 5, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('bD', 'bE', 1, 10, 'c9'))
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bD', 'bG', 6, 12, 'c10'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('z', 'bA', lb=0, name='ref_preceding_b'))
    agent_b_network.add_event('z')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')

    new_mastnu, shared_events = preprocess_networks(mastnu)

    #  print(shared_events)
    assert(len(shared_events) == 9)
    #  print(new_mastnu.agent2network['agent-a'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-a'].get_constraints()) == 3)
    #  print(new_mastnu.agent2network['agent-a'].get_events())
    assert(len(new_mastnu.agent2network['agent-a'].get_events()) == 4)
    #  print(new_mastnu.agent2network['agent-b'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-b'].get_constraints()) == 10)
    #  print(new_mastnu.agent2network['agent-b'].get_events())
    assert(len(new_mastnu.agent2network['agent-b'].get_events()) == 11)
    assert(new_mastnu.agent2network['agent-b'].id2constraint['c10'].s == 'bD-copy')

    decoupling, conflicts = solve_decoupling(mastnu)
    assert(decoupling)
    print(decoupling.pprint())
    print(decoupling.pprint_proof(ext_reqs, ext_conts))
    decoupling = solve_decoupling_milp(mastnu)
    assert(decoupling)
    print(decoupling.pprint())
    print(decoupling.pprint_proof(ext_reqs, ext_conts))

def test_centralized_milp_preprocess_4():
    # Testcase4:
    """
                  ====> F
                (Ce) --> (Ds) ---> (E)
                 ||       |         ||
    A ==> B ==> (Cs) --> (De) ---> (E)
    For agent-a, C should have copy
    For agent-b, B, C should have copies
    """

    ext_reqs = [SimpleTemporalConstraint('aD', 'bD', 1, 5, 'c3')]
    ext_conts = [SimpleContingentTemporalConstraint('bC', 'aC', 1, 4, 'c1'),
            SimpleContingentTemporalConstraint('aE', 'bE', 6, 8, 'c2')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleTemporalConstraint('aC', 'aD', 0, 5, 'c4'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('aD', 'aE', 1, 10, 'c5'))
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('aC', 'aF', 0, 5, 'c10'))
    agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'aC', lb=0, name='ref_preceding_a'))
    agent_a_network.add_event('z')
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bA', 'bB', 6, 12, 'c6'))
    agent_b_network.add_constraint(SimpleContingentTemporalConstraint('bB', 'bC', 6, 12, 'c7'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('bC', 'bD', 4, 6, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('bD', 'bE', 6, 12, 'c9'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('z', 'bA', lb=0, name='ref_preceding_b'))
    agent_b_network.add_event('z')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'z')

    new_mastnu, shared_events = preprocess_networks(mastnu)

    #  print(shared_events)
    assert(len(shared_events) == 7)
    #  print(new_mastnu.agent2network['agent-a'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-a'].get_constraints()) == 5)
    #  print(new_mastnu.agent2network['agent-a'].get_events())
    assert(len(new_mastnu.agent2network['agent-a'].get_events()) == 6)
    #  print(new_mastnu.agent2network['agent-b'].get_constraints())
    assert(len(new_mastnu.agent2network['agent-b'].get_constraints()) == 7)
    #  print(new_mastnu.agent2network['agent-b'].get_events())
    assert(len(new_mastnu.agent2network['agent-b'].get_events()) == 8)

    decoupling, conflicts = solve_decoupling(mastnu)
    assert(decoupling)
    #  print(decoupling.pprint())
    decoupling = solve_decoupling_milp(mastnu)
    assert(decoupling)
    #  print(decoupling.pprint())

def test_nikhil_example_no_obs(print_decoupling=False, plot=None):
    # A ==> B (observable)
    #          C ---> D
    # A --> D and B ---> D

    ext_conts = []
    ext_reqs = [SimpleTemporalConstraint('B', 'D', 30, 45, 'c4')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('A', 'B', 20, 40, 'c1'))
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('C', 'D', 15, 15, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('A', 'D', 60, 75, 'c3'))
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'A')

    decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True, objective=NONE)
    assert(decoupling is None)

    decoupling, stats = solve_decoupling_milp(mastnu, output_stats=True, objective=NONE)
    assert(decoupling is None)

def test_nikhil_example_delay_5(print_decoupling=False, plot=None):
    # NOTE: delay should be [5, 5+epsilon]
    # A ==> B (observable)
    #          C ---> D
    # A --> D and B ---> D

    ext_conts = [SimpleContingentTemporalConstraint('B', 'B-obs', 5, 5.1, 'c2')]
    ext_reqs = [SimpleTemporalConstraint('B', 'D', 30, 45, 'c4')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('A', 'B', 20, 40, 'c1'))
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('C', 'D', 15, 15, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('A', 'D', 60, 75, 'c3'))
    agent_b_network.add_event('B-obs')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'A')

    decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True, objective=NONE)
    assert(decoupling)

    if print_decoupling:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    decoupling, stats = solve_decoupling_milp(mastnu, output_stats=True, objective=NONE)
    assert(decoupling)

    if print_decoupling:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    #  if plot is not None:
    #      from plot import TNPlot, MaSTNUPlot
    #      ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
    #      ma_plt.plot()
    #      ma_plt.plot_with_decoupling(decoupling)
    #      ma_plt.plot_iterate_proof(decoupling)

def test_nikhil_example_delay_40(print_decoupling=False, plot=None):
    # NOTE: delay should be [40, 40+epsilon]
    # A ==> B (observable)
    #          C ---> D
    # A --> D and B ---> D

    ext_conts = [SimpleContingentTemporalConstraint('B', 'B-obs', 40, 40.1, 'c2')]
    ext_reqs = [SimpleTemporalConstraint('B', 'D', 30, 45, 'c4')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('A', 'B', 20, 40, 'c1'))
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('C', 'D', 15, 15, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('A', 'D', 60, 75, 'c3'))
    agent_b_network.add_event('B-obs')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'A')

    decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True, objective=NONE)
    assert(decoupling is None)

    decoupling, stats = solve_decoupling_milp(mastnu, output_stats=True, objective=NONE)
    assert(decoupling is None)


def test_nikhil_example_obs_or_not(print_decoupling=False, plot=None):
    # Test under max flex metric, whether obs is taken or not, when w or w/o obs are both feasible. Seems that it would prefer using the comm link is uncertainty is low in this case.
    # AB is now [20, 30] instead of [20, 40]
    # A ==> B (observable)
    #          C ---> D
    # A --> D and B ---> D

    ext_conts = [SimpleContingentTemporalConstraint('B', 'B-obs', 0, 5, 'c2')]
    ext_reqs = [SimpleTemporalConstraint('B', 'D', 30, 45, 'c4')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('A', 'B', 20, 30, 'c1'))
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('C', 'D', 15, 15, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('A', 'D', 60, 75, 'c3'))
    agent_b_network.add_event('B-obs')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'A')

    decoupling, conflicts, stats = solve_decoupling(mastnu, output_stats=True, objective=MAX_FLEXIBILITY)
    assert(decoupling)

    decoupling, stats = solve_decoupling_milp(mastnu, output_stats=True, objective=MAX_FLEXIBILITY)
    assert(decoupling)

    if print_decoupling:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    #  if plot is not None:
    #      from plot import TNPlot, MaSTNUPlot
    #      ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
    #      ma_plt.plot()
    #      ma_plt.plot_with_decoupling(decoupling)
    #      ma_plt.plot_iterate_proof(decoupling)

#  def test_observations(print_decoupling=False, plot=None, output_stats=False):
#      # Should observe that vanilla takes longest, compilation methods take
#      # shorter time (but strong controllability one makes no difference than
#      # the consistency one, if all events are shared). And MILP is fastest.

#      # Test the impact of adding observations
#      #                b1====>b2
#      # z--->a1====>a2/        \a3====>a4

#      # deadline < 60
#      CONSIDER_DEADLINE = True
#      CONSIDER_INTERNAL = True

#      # Possibly useful options: a2, b1, b2
#      # ADD_OBS_EVENTS = []
#      # ADD_OBS_EVENTS = ['b1','b2']
#      ADD_OBS_EVENTS = ['a2', 'b1', 'b2']
#      # ADD_OBS_EVENTS = ['a2', 'b1', 'b2', 'a3']

#      OBS_DELAY = 1
#      objectives = [MIN_LB_UB_TIME_SPAN]
#      # objectives = [NONE, MIN_TIME_SPAN, MAX_FLEXIBILITY, MAX_FLEXIBILITY_NAIVE, MAX_FLEXIBILITY_NEG_CKJ, MIN_LB_TIME_SPAN, MIN_LB_UB_TIME_SPAN]

#      for objective in objectives:
#          if output_stats:
#              print("Objective: {}".format(objective))

#          task_network = TaskNetwork()
#          task_network.set_ref_event('z')
#          task_network.add_constraint(SimpleTemporalConstraint('a2', 'b1', lb=0, name='c1'))
#          task_network.add_constraint(SimpleTemporalConstraint('b2', 'a3', lb=0, name='c2'))
#          task_network.add_event_to_agent({'a2': 'agent-a', 'a3': 'agent-a',
#                                           'b1': 'agent-b', 'b2': 'agent-b'})

#          # Agent networks
#          agent_a_network = AgentNetwork('agent-a')
#          agent_a_network.set_ref_event('z')
#          agent_a_network.add_shared_events(['a2', 'a3'])
#          agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'a1', lb=0, name='c3'))
#          agent_a_network.add_constraint(SimpleTemporalConstraint('z', 'a3', lb=0, name='c4'))
#          agent_a_network.add_constraint(SimpleContingentTemporalConstraint('a1', 'a2', 5, 10, 'c5'))
#          agent_a_network.add_constraint(SimpleContingentTemporalConstraint('a3', 'a4', 5, 10, 'c6'))
#          agent_a_network.add_constraint(SimpleTemporalConstraint('a2', 'a3', lb=0, name='c14'))
#          agent_b_network = AgentNetwork('agent-b')
#          agent_b_network.set_ref_event('z')
#          agent_b_network.add_shared_events(['b1', 'b2'])
#          agent_b_network.add_constraint(SimpleTemporalConstraint('z', 'b1', lb=0, name='c7'))
#          agent_b_network.add_constraint(SimpleContingentTemporalConstraint('b1', 'b2', 5, 10, 'c8'))

#          # The algorithm should consider other local requirement constraints in master
#          if CONSIDER_INTERNAL:
#              task_network.add_constraint(SimpleTemporalConstraint('z', 'a2', lb=0, name='c9'))
#              # task_network.add_constraint(SimpleTemporalConstraint('z', 'b2', lb=0, name='c10'))
#              task_network.add_constraint(SimpleTemporalConstraint('b1', 'b2', lb=0, name='c11'))
#          if CONSIDER_DEADLINE:
#              task_network.add_constraint(SimpleTemporalConstraint('a3', 'a4', lb=0, name='c12'))
#              task_network.add_constraint(SimpleTemporalConstraint('z', 'a4', ub=60, name='c13'))
#              task_network.add_event_to_agent({'a4': 'agent-a'})
#              agent_a_network.add_shared_events(['a4'])

#          # Add observable events
#          if ADD_OBS_EVENTS:
#              event2agent = task_network.event2agent
#              for e in ADD_OBS_EVENTS:
#                  agent = event2agent[e]
#                  if agent == 'agent-a':
#                      copy_e = '{}-copy-at-{}'.format(e, 'agent-b')
#                      task_network.add_event_to_agent({copy_e: 'agent-b'})
#                      agent_b_network.add_shared_events([copy_e])
#                      task_network.add_constraint(SimpleContingentTemporalConstraint(e, copy_e, lb=0, ub=OBS_DELAY, name='obs({},{})'.format(e, copy_e)))
#                      task_network.add_constraint(SimpleTemporalConstraint('z', copy_e, lb=0, name='ref->{}'.format(copy_e)))
#                  if agent == 'agent-b':
#                      copy_e = '{}-copy-at-{}'.format(e, 'agent-a')
#                      task_network.add_event_to_agent({copy_e: 'agent-a'})
#                      agent_a_network.add_shared_events([copy_e])
#                      task_network.add_constraint(SimpleContingentTemporalConstraint(e, copy_e, lb=0, ub=OBS_DELAY, name='obs({},{})'.format(e, copy_e)))
#                      task_network.add_constraint(SimpleTemporalConstraint('z', copy_e, lb=0, name='ref->{}'.format(copy_e)))

#          # Vanilla version of distributed temporal decoupling
#          if output_stats:
#              decoupling, conflicts, stats = solve_decoupling(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#          else:
#              decoupling, conflicts = solve_decoupling(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#          assert(decoupling)
#          if output_stats:
#              print("Vanilla version:")
#              print("Stats: {}".format(stats))
#              print("Num conflicts: {}".format(len(conflicts)))

#          if print_decoupling:
#              print("Objective: {}".format(objective))
#              print(decoupling.pprint())
#              print("Objective value: {}".format(decoupling.objective_value))
#              print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#              print("")

#          #  # Distributed temporal decoupling with consistency compilation
#          #  if output_stats:
#          #      decoupling, conflicts, stats = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STN)
#          #  else:
#          #      decoupling, conflicts = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STN)
#          #  assert(decoupling)
#          #  if output_stats:
#          #      print("Compilation using consistency:")
#          #      print("Stats: {}".format(stats))
#          #      print("Num conflicts: {}".format(len(conflicts)))

#          #  if print_decoupling:
#          #      print("Objective: {}".format(objective))
#          #      print(decoupling.pprint())
#          #      print("Objective value: {}".format(decoupling.objective_value))
#          #      print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#          #      print("")

#          #  # Distributed temporal decoupling with strong controllability compilation
#          #  if output_stats:
#          #      decoupling, conflicts, stats = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STRONG_STNU)
#          #  else:
#          #      decoupling, conflicts = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STRONG_STNU)
#          #  assert(decoupling)
#          #  if output_stats:
#          #      print("Compilation using strong controllability:")
#          #      print("Stats: {}".format(stats))
#          #      print("Num conflicts: {}".format(len(conflicts)))

#          #  if print_decoupling:
#          #      print("Objective: {}".format(objective))
#          #      print(decoupling.pprint())
#          #      print("Objective value: {}".format(decoupling.objective_value))
#          #      print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#          #      print("")

#          # Centralized temporal decoupling using MILP
#          if output_stats:
#              decoupling, stats = solve_decoupling_milp(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#          else:
#              decoupling = solve_decoupling_milp(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#          assert(decoupling)
#          if output_stats:
#              print("Centralized MILP:")
#              print("Stats: {}".format(stats))

#          if print_decoupling:
#              print("Objective: {}".format(objective))
#              print(decoupling.pprint())
#              print("Objective value: {}".format(decoupling.objective_value))
#              print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#              print("")

#          # Search queue
#          #  decoupling, conflicts, stats = solve_decoupling(task_network, [agent_a_network, agent_b_network], objective=objective, search=True, qtype='priority', output_stats=True)
#          #  assert(decoupling)
#          #  if output_stats:
#              #  print("Stats: {}".format(stats))
#              #  print("Num conflicts: {}".format(len(conflicts)))

#          #  if print_decoupling:
#              #  print("Objective: {}".format(objective))
#              #  print(decoupling.pprint())
#              #  print("Objective value: {}".format(decoupling.objective_value))
#              #  print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints(), warn=True))
#              #  print("")

#  def test_compilation_with_observations(print_decoupling=False, plot=None, output_stats=False):
#      # In this example, vanilla version speed < consistency compilation
#      # < strong controllability compilation. And MILP takes longest.

#      # Assume two agents have symmetric network as follows:

#      #  A ========> (B) ----------> (C)
#      #  |                          /
#      #  D ===> E -----> F =====> G/

#      # And the external constraints are:
#      # The end events (C) should be [10, 50]
#      # The two events (B) are observable with [0, 5] delay

#      agent2network = {}
#      for agent in ['agent-a', 'agent-b']:
#          A = '{}-A'.format(agent)
#          B = '{}-B'.format(agent)
#          C = '{}-C'.format(agent)
#          D = '{}-D'.format(agent)
#          E = '{}-E'.format(agent)
#          F = '{}-F'.format(agent)
#          G = '{}-G'.format(agent)
#          ctc1 = SimpleContingentTemporalConstraint(A, B, lb=10, ub=15)
#          ctc2 = SimpleContingentTemporalConstraint(D, E, lb=5, ub=10)
#          ctc3 = SimpleContingentTemporalConstraint(F, G, lb=5, ub=10)
#          stc1 = SimpleTemporalConstraint(A, D, lb=0, ub=30)
#          stc2 = SimpleTemporalConstraint(E, F, lb=0, ub=30)
#          stc3 = SimpleTemporalConstraint(G, C, lb=0, ub=30)
#          stc_z = SimpleTemporalConstraint('z', A, lb=0)
#          constraints = [ctc1, ctc2, ctc3, stc1, stc2, stc3, stc_z]
#          network = AgentNetwork(agent, constraints=constraints, shared_events=[B, C], ref_event='z')
#          agent2network[agent] = network
#      agent2network['agent-a'].shared_events.append('agent-b-B-copy')
#      agent2network['agent-b'].shared_events.append('agent-a-B-copy')

#      # Create task network
#      event2agent = {'agent-a-B': 'agent-a', 'agent-a-C': 'agent-a', 'agent-b-B-copy': 'agent-a',
#              'agent-b-B': 'agent-b', 'agent-b-C': 'agent-b', 'agent-a-B-copy': 'agent-b'}
#      stc = SimpleTemporalConstraint('agent-a-C', 'agent-b-C', lb=10, ub=50)
#      obs1 = SimpleContingentTemporalConstraint('agent-a-B', 'agent-a-B-copy', lb=0, ub=5)
#      obs2 = SimpleContingentTemporalConstraint('agent-b-B', 'agent-b-B-copy', lb=0, ub=5)
#      stc_z1 = SimpleTemporalConstraint('z', 'agent-a-B', lb=0)
#      stc_z2 = SimpleTemporalConstraint('z', 'agent-b-B', lb=0)
#      constraints = [stc, obs1, obs2, stc_z1, stc_z2]
#      task_network = TaskNetwork(constraints=constraints, event2agent=event2agent, ref_event='z')


#      agent_a_network = agent2network['agent-a']
#      agent_b_network = agent2network['agent-b']
#      objective = MIN_LB_UB_TIME_SPAN

#      # Vanilla version of distributed temporal decoupling
#      if output_stats:
#          decoupling, conflicts, stats = solve_decoupling(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#      else:
#          decoupling, conflicts = solve_decoupling(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#      assert(decoupling)
#      if output_stats:
#          print("Vanilla version:")
#          print("Stats: {}".format(stats))
#          print("Num conflicts: {}".format(len(conflicts)))

#      if print_decoupling:
#          print("Objective: {}".format(objective))
#          print(decoupling.pprint())
#          print("Objective value: {}".format(decoupling.objective_value))
#          print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#          print("")

#      if plot is not None:
#          from plot import TNPlot, MaSTNUPlot
#          ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
#          ma_plt.plot()
#          ma_plt.plot_with_decoupling(decoupling)
#          ma_plt.plot_iterate_proof(decoupling)

#      #  # Distributed temporal decoupling with consistency compilation
#      #  if output_stats:
#      #      decoupling, conflicts, stats = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STN)
#      #  else:
#      #      decoupling, conflicts = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STN)
#      #  assert(decoupling)
#      #  if output_stats:
#      #      print("Compilation using consistency:")
#      #      print("Stats: {}".format(stats))
#      #      print("Num conflicts: {}".format(len(conflicts)))

#      #  if print_decoupling:
#      #      print("Objective: {}".format(objective))
#      #      print(decoupling.pprint())
#      #      print("Objective value: {}".format(decoupling.objective_value))
#      #      print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#      #      print("")

#      #  if plot is not None:
#      #      from distributed_decoupling import TNPlot, MaSTNUPlot
#      #      ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
#      #      ma_plt.plot()
#      #      ma_plt.plot_with_decoupling(decoupling)
#      #      ma_plt.plot_iterate_proof(decoupling)

#      #  # Distributed temporal decoupling with strong controllability compilation
#      #  if output_stats:
#      #      decoupling, conflicts, stats = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STRONG_STNU)
#      #  else:
#      #      decoupling, conflicts = solve_decoupling_wrapper(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats, compilation=COMPILE_STRONG_STNU)
#      #  assert(decoupling)
#      #  if output_stats:
#      #      print("Compilation using strong controllability:")
#      #      print("Stats: {}".format(stats))
#      #      print("Num conflicts: {}".format(len(conflicts)))

#      #  if print_decoupling:
#      #      print("Objective: {}".format(objective))
#      #      print(decoupling.pprint())
#      #      print("Objective value: {}".format(decoupling.objective_value))
#      #      print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#      #      print("")

#      #  if plot is not None:
#      #      from distributed_decoupling import TNPlot, MaSTNUPlot
#      #      ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
#      #      ma_plt.plot()
#      #      ma_plt.plot_with_decoupling(decoupling)
#      #      ma_plt.plot_iterate_proof(decoupling)

#      # Centralized temporal decoupling using MILP
#      if output_stats:
#          decoupling, stats = solve_decoupling_milp(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#      else:
#          decoupling = solve_decoupling_milp(task_network, [agent_a_network, agent_b_network], objective=objective, output_stats=output_stats)
#      assert(decoupling)
#      if output_stats:
#          print("Centralized MILP:")
#          print("Stats: {}".format(stats))

#      if print_decoupling:
#          print("Objective: {}".format(objective))
#          print(decoupling.pprint())
#          print("Objective value: {}".format(decoupling.objective_value))
#          print(decoupling.pprint_proof(task_network.get_ext_req_constraints(), task_network.get_ext_cont_constraints()))
#          print("")

#      if plot is not None:
#          from plot import TNPlot, MaSTNUPlot
#          ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
#          ma_plt.plot()
#          ma_plt.plot_with_decoupling(decoupling)
#          ma_plt.plot_iterate_proof(decoupling)

def test_nikhil_example_no_comm_icaps(print_decoupling=False, plot=None):
    # delay should be [0, 5]
    # A ==> B (not observable)
    #          C ---> D
    # A --> D and B ---> D

    ext_conts = []
    ext_reqs = [SimpleTemporalConstraint('B', 'D', 30, 45, 'c4')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('A', 'B', 20, 40, 'c1'))
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('C', 'D', 15, 15, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('A', 'D', 60, 75, 'c3'))
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'A')

    decoupling, conflicts, stats = solve_decoupling(mastnu, objective=MAX_FLEXIBILITY, output_stats=True)
    assert(decoupling is None)
    print(stats)

def test_nikhil_example_delay_5_icaps(print_decoupling=False, plot=None):
    # delay should be [0, 5]
    # A ==> B (observable)
    #          C ---> D
    # A --> D and B ---> D

    ext_conts = [SimpleContingentTemporalConstraint('B', 'B-obs', 0, 5, 'c2')]
    ext_reqs = [SimpleTemporalConstraint('B', 'D', 30, 45, 'c4')]

    agent2network = {}

    agent_a_network = TemporalNetwork()
    agent_a_network.add_constraint(SimpleContingentTemporalConstraint('A', 'B', 20, 40, 'c1'))
    agent2network['agent-a'] = agent_a_network

    agent_b_network = TemporalNetwork()
    agent_b_network.add_constraint(SimpleTemporalConstraint('C', 'D', 15, 15, 'c8'))
    agent_b_network.add_constraint(SimpleTemporalConstraint('A', 'D', 60, 75, 'c3'))
    agent_b_network.add_event('B-obs')
    agent2network['agent-b'] = agent_b_network

    mastnu = MaSTNU(agent2network, ext_reqs, ext_conts, 'A')

    decoupling, conflicts, stats = solve_decoupling(mastnu, objective=MAX_FLEXIBILITY, output_stats=True)
    assert(decoupling)
    print(stats)

    #  decoupling = solve_decoupling_milp(task_network, [agent_a_network, agent_b_network], objective=NONE)
    #  assert(decoupling)

    if print_decoupling:
        print(decoupling.pprint())
        print(decoupling.pprint_proof(ext_reqs, ext_conts))
        print("Objective value: {}".format(decoupling.objective_value))

    #  if plot is not None:
        #  from distributed_decoupling import TNPlot, MaSTNUPlot
        #  ma_plt = MaSTNUPlot(task_network, [agent_a_network, agent_b_network], form=plot)
        #  ma_plt.plot()
        #  ma_plt.plot_with_decoupling(decoupling)
        #  ma_plt.plot_iterate_proof(decoupling)

#  print("# Test compilation")
#  Commented out, needs to update to MaSTNU representation
#  test_compilation()

print("# Test centralized MILP preprocessing and finding decoupling")
#  test_centralized_milp_preprocess_1()
#  test_centralized_milp_preprocess_2()
test_centralized_milp_preprocess_3()
#  test_centralized_milp_preprocess_4()

#  print("# Test casanova example")
#  test_casanova_example(print_decoupling=False, plot=None)

#  print("# Test Nikhil's example with different obs delay")
#  test_nikhil_example_no_obs(print_decoupling=False, plot=None)
#  test_nikhil_example_delay_5(print_decoupling=False, plot=None)
#  test_nikhil_example_delay_40(print_decoupling=False, plot=None)
#  test_nikhil_example_obs_or_not(print_decoupling=False, plot=None)

#  print("# Test observations")
#  Commented out, needs to update to MaSTNU representation
#  test_observations(print_decoupling=False, plot=None, output_stats=False)
#  test_compilation_with_observations(print_decoupling=False, plot=None, output_stats=False)

#  print("# Test ICAPS examples")
#  test_nikhil_example_no_comm_icaps(print_decoupling=False)
#  test_nikhil_example_delay_5_icaps(print_decoupling=True)

print("All tests passed.")
