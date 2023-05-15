import sys, os
sys.path.insert(0, os.path.join(sys.path[0], os.pardir))

from definitions.temporal_network import TemporalNetwork, SimpleTemporalConstraint, SimpleContingentTemporalConstraint
import matplotlib.pyplot as plt
import networkx as nx
import math
import numpy as np

LAYOUT_BY_DISTANCE = 0
PLANER_LAYOUT = 1
SPRING_LAYOUT = 2
RANDOM_LAYOUT = 3
LAYOUT_EQUAL_DISTANCE = 4

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

class TNPlot():
    '''
    Given a reference to a temporal network,
    plot the network in distance graph (DG) form or (TN) form.
    '''
    def __init__(self, network, form='DG', layout=LAYOUT_BY_DISTANCE):
        self.tn = network
        self.form = form

        # Find uncontrollable nodes
        self.u_nodes = set()
        for c in self.tn.get_constraints():
            if isinstance(c, SimpleContingentTemporalConstraint):
                self.u_nodes.add(c.e)
        self.c_nodes = set(self.tn.get_events()).difference(self.u_nodes)

        if self.form == 'DG':
            self.dg = self.to_dg()
        elif self.form == 'TN':
            self.dg = self.to_tn()
        else:
            raise ValueError

        # Compute layout
        self.pos = None
        if layout == LAYOUT_BY_DISTANCE:
            self.pos = self.compute_layout_by_distance()
        elif layout == PLANER_LAYOUT:
            self.pos = nx.planar_layout(self.dg)
        elif layout == SPRING_LAYOUT:
            self.pos = nx.spring_layout(self.dg)
        elif layout == RANDOM_LAYOUT:
            self.pos = nx.random_layout(self.dg)
        elif layout == LAYOUT_EQUAL_DISTANCE:
            self.pos = self.customer_layout()
        else:
            raise ValueError

        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

        # Parameters
        self.curve_ratio = 0.2

    def customer_layout(self):
        pos = {}
        ref_event = self.task_network.get_ref_event()
        pos[ref_event] = np.array([0, 0])
        len_networks = len(self.agent_networks)
        v_delta = 1.0/len_networks
        for i in range(len_networks):
            a = self.agent_networks[i]
            agent_events = a.get_all_events()
            agent_events.remove(a.get_ref_event())
            agent_events.sort()
            len_events = len(agent_events)
            h_delta = 1.0/(len_events + 1)
            for j in range(len_events):
                e = agent_events[j]
                pos[e] = np.array([h_delta * (j + 1), v_delta * i])
        return pos

    def compute_layout_by_distance(self):
        dg = self.to_dg()
        ref_event = self.task_network.get_ref_event()

        # print(dg.nodes())
        # mynodes = list(dg.nodes)
        # print(dg.adj)
        # print(nx.johnson(dg))
        # print(nx.single_source_bellman_ford(dg, ref_event, mynodes[1]))

        pos = {}
        length = nx.single_source_bellman_ford_path_length(dg, ref_event)
        # for node in length:
        #     print('{}: {}'.format(node, length[node]))

        pos[ref_event] = np.array([length[ref_event], 0])
        len_networks = len(self.agent_networks)
        v_delta = (max(length.values()) - min(length.values()))/len_networks
        for i in range(len_networks):
            a = self.agent_networks[i]
            agent_events = a.get_all_events()
            agent_events.remove(ref_event)
            len_events = len(agent_events)
            for j in range(len_events):
                e = agent_events[j]
                # TODO should assert e in length
                if e in length:
                    pos[e] = np.array([length[e], v_delta * i])
                else:
                    pos[e] = np.array([0, v_delta * i])

        return pos

    def to_dg(self):
        '''
        Convert the temporal network into distance graph.
        Return:
        + Distance graph: DG
        '''
        g = nx.MultiDiGraph()

        constraints = self.tn.get_constraints()
        for c in constraints:
            if isinstance(c, SimpleTemporalConstraint):
                if c.ub is not None:
                    g.add_edges_from([(c.s, c.e, {'is_cont': False, 'weight': c.ub, 'constraint': [c, 'UB+']})])
                if c.lb is not None:
                    g.add_edges_from([(c.e, c.s, {'is_cont': False, 'weight': -c.lb, 'constraint': [c, 'LB-']})])
            elif isinstance(c, SimpleContingentTemporalConstraint):
                # We allow c.ub == c.lb
                g.add_edges_from([(c.s, c.e, {'is_cont': True, 'weight': c.ub, 'constraint': [c, 'UB+']}),
                                  (c.e, c.s, {'is_cont': True, 'weight': -c.lb, 'constraint': [c, 'LB-']})])
        return g

    def to_tn(self):
        '''
        Convert the temporal network into TN form using networkx.
        Return:
        + DiGraph in TN form
        '''
        g = nx.MultiDiGraph()

        constraints = self.tn.get_constraints()
        for c in constraints:
            if isinstance(c, SimpleTemporalConstraint):
                g.add_edges_from([(c.s, c.e, {'is_cont': False, 'weight': [c.lb, c.ub], 'constraint': c})])
            elif isinstance(c, SimpleContingentTemporalConstraint):
                g.add_edges_from([(c.s, c.e, {'is_cont': True, 'weight': [c.lb, c.ub], 'constraint': c})])
        return g

    def plot(self, savefig=False, filename=None, name_map=None):
        '''
        Plot the current network in DG or TN form.
        Notice that a node can have attributes 'color'.
        And an edge can have attributes 'color', 'linewidth' and 'linestyle'.
        '''

        # Clear any old figure from plt
        # plt.cla()
        plt.clf()
        pos = self.pos

        c_nodes = list(self.c_nodes)
        u_nodes = list(self.u_nodes)

        labels = {}
        node2data = {}
        for v, data in self.dg.nodes(data=True):
            labels[v] = v
            node2data[v] = data

        node_color = [node2data[v]['color'] if 'color' in node2data[v] else 'w' for v in c_nodes]
        nx.draw_networkx_nodes(self.dg, pos, nodelist=c_nodes, node_shape = 'o', node_color = node_color, node_size = 250, alpha = 1, linewidths=1, edgecolors= 'black')
        node_color = [node2data[v]['color'] if 'color' in node2data[v] else 'w' for v in u_nodes]
        nx.draw_networkx_nodes(self.dg, pos, nodelist=u_nodes, node_shape = 's', node_color = node_color, node_size = 250, alpha = 1, linewidths=1, edgecolors= 'black')
        nx.draw_networkx_labels(self.dg, pos, labels, font_size=10)

        ax = plt.gca()
        ax.axis('off')

        for e in self.dg.edges(data=True, keys=True):
            s, t, key, data = e
            linestyle = '-'
            if 'linestyle' in data:
                linestyle = data['linestyle']
            color = 'black'
            if 'color' in data:
                color = data['color']
            linewidth = 1
            if 'linewidth' in data:
                linewidth = data['linewidth']
            ax.annotate("",
                        xy=pos[t], xycoords='data',
                        xytext=pos[s], textcoords='data',
                        arrowprops=dict(arrowstyle="->", color=color,
                                        linestyle=linestyle,
                                        linewidth=linewidth,
                                        shrinkA=8, shrinkB=8,
                                        patchA=None, patchB=None,
                                        connectionstyle="arc3,rad=rrr".replace('rrr',str(self.curve_ratio*key + self.curve_ratio)
                                        ),
                                        ),
                        )
            weight = data['weight']
            label = ""
            if data['is_cont']:
                label = "c:"
            pos_distance = distance(pos[s], pos[t])
            pos_delta = pos[t] - pos[s]
            pos_label = (pos[s] + pos[t]) /2
            sine = pos_delta[1] / pos_distance
            cosine = pos_delta[0] / pos_distance
            half_distance = (self.curve_ratio * key + self.curve_ratio)/2
            pos_offset = [sine * half_distance * pos_distance, -cosine * half_distance * pos_distance]
            ax.annotate("{}{}".format(label, weight),
                        xy=pos_label + pos_offset, xycoords='data')

            # TODOTODO: Hack: should create a plot class for QSP, or TNPlot should take form=='QSP'
            # Add activity name
            if name_map:
                if (s, t) in name_map:
                    name = name_map[(s, t)]
                    curve_ratio = 0
                    pos_distance = distance(pos[s], pos[t])
                    pos_delta = pos[t] - pos[s]
                    pos_label = (pos[s] + pos[t]) /2
                    sine = pos_delta[1] / pos_distance
                    cosine = pos_delta[0] / pos_distance
                    half_distance = (curve_ratio * key + curve_ratio)/2
                    pos_offset = [sine * half_distance * pos_distance - 15, -cosine * half_distance * pos_distance - 15]
                    ax.annotate(name,
                                xy= pos_label + pos_offset, xycoords='data')

        if self.xmin is not None:
            plt.axis('equal')
            ax.set(xlim=(self.xmin, self.xmax), ylim=(self.ymin, self.ymax))
        else:
            self.xmin, self.xmax, self.ymin, self.ymax = plt.axis('equal')
        if savefig:
            assert(filename is not None)
            plt.savefig(filename)
        else:
            plt.show()


class MaSTNUPlot(TNPlot):
    '''
    Given a reference to a temporal network,
    plot the network in distance graph (DG) form.
    '''
    def __init__(self, task_network, agent_networks, form='DG', layout=LAYOUT_EQUAL_DISTANCE):
        self.task_network = task_network
        self.agent_networks = agent_networks

        tn = self.merge_networks()
        super().__init__(tn, form, layout)

    def merge_networks(self):
        network = TemporalNetwork()

        for c in self.task_network.get_constraints():
            network.add_constraint(c)
        for a in self.agent_networks:
            for c in a.get_constraints():
                network.add_constraint(c)

        return network

    def plot(self):
        """
        High light external constraints with blue
        """
        event2agent = self.task_network.event_to_agent

        for e in self.dg.edges(data=True, keys=True):
            s, t, key, data = e
            if event2agent(s) is not None and event2agent(t) is not None and event2agent(s) != event2agent(t):
                self.dg.edges[s, t, key]['color'] = 'b'

        # Plot
        super().plot()

        for e in self.dg.edges(data=True, keys=True):
            s, t, key, data = e
            if 'color' in self.dg.edges[s, t, key]:
                del self.dg.edges[s, t, key]['color']

    def plot_with_decoupling(self, decoupling):
        """
        Plot decoupling with the DG.
        """

        # Add decoupling constraints to graph
        for network in self.agent_networks:
            agent_name = network.get_agent_name()
            decoupling_constraints = decoupling.agent_to_decoupling(agent_name)
            for c in decoupling_constraints:
                if isinstance(c, SimpleTemporalConstraint):
                    if self.form == 'DG':
                        if c.ub is not None:
                            self.dg.add_edges_from([(c.s, c.e, {'color':'r', 'is_decoupling': True, 'is_cont': False, 'weight': c.ub, 'constraint': [c, 'UB+']})])
                        if c.lb is not None:
                            self.dg.add_edges_from([(c.e, c.s, {'color':'r', 'is_decoupling': True, 'is_cont': False, 'weight': -c.lb, 'constraint': [c, 'LB-']})])
                    elif self.form == 'TN':
                        self.dg.add_edges_from([(c.s, c.e, {'color':'r', 'is_decoupling': True, 'is_cont': False, 'weight': [c.lb, c.ub], 'constraint': c})])
                    else:
                        raise ValueError
                elif isinstance(c, SimpleContingentTemporalConstraint):
                    if self.form == 'DG':
                        # We allow c.ub == c.lb
                        self.dg.add_edges_from([(c.s, c.e, {'color':'r', 'is_decoupling': True, 'is_cont': True, 'weight': c.ub, 'constraint': [c, 'UB+']}),
                                                (c.e, c.s, {'color':'r', 'is_decoupling': True, 'is_cont': True, 'weight': -c.lb, 'constraint': [c, 'LB-']})])
                    elif self.form == 'TN':
                        self.dg.add_edges_from([(c.s, c.e, {'color':'r', 'is_decoupling': True, 'is_cont': True, 'weight': [c.lb, c.ub], 'constraint': c})])
                    else:
                        raise ValueError

        # Plot
        self.plot()

        # Remove decoupling constraints from graph
        to_remove = []
        for e in self.dg.edges(data=True, keys=True):
            s, t, key, data = e
            if 'is_decoupling' in self.dg.edges[s, t, key]:
                to_remove.append((s, t, key))

        for (s, t, key) in to_remove:
            self.dg.remove_edge(s, t, key=key)

    def plot_iterate_proof(self, decoupling):
        """
        Iterate over all external constraints and show proof for each
        """
        ext_reqs = self.task_network.get_ext_req_constraints()
        ext_conts  = self.task_network.get_ext_cont_constraints()
        for c in ext_reqs:
            self.plot_with_proof(decoupling, [c], [])
        for c in ext_conts:
            self.plot_with_proof(decoupling, [], [c])

    def plot_with_proof(self, decoupling, ext_reqs, ext_conts):
        """
        Show the proof for ext_reqs and ext_conts
        """
        # Change ext_reqs and ext_conts to bold
        to_revert = []
        for e in self.dg.edges(data=True, keys=True):
            s, t, key, data = e
            if 'constraint' in data:
                if self.form == 'DG':
                    c = data['constraint'][0]
                elif self.form == 'TN':
                    c = data['constraint']
                else:
                    raise ValueError
                if c in ext_reqs or c in ext_conts:
                    self.dg.edges[s, t, key]['linewidth'] = 2
                    to_revert.append((s, t, key))

        # Add proof to graph
        proof_reqs, proof_conts = decoupling.obtain_proof(ext_reqs, ext_conts)
        if proof_reqs:
            for (vi, vj) in proof_reqs:
                justification = proof_reqs[(vi, vj)]
                # Justification path
                for pair in justification:
                    self.dg.add_edges_from([(pair[1], pair[2], {'color':'r', 'linewidth': 2, 'is_proof': True, 'is_cont': False, 'weight': pair[3]})])

        if proof_conts:
            for (vi, vj) in proof_conts:
                justification = proof_conts[(vi, vj)]
                for (i, j) in justification:
                    jus = justification[(i, j)]
                    for pair in jus:
                        self.dg.add_edges_from([(pair[1], pair[2], {'color':'r', 'linewidth': 2, 'is_proof': True, 'is_cont': False, 'weight': pair[3]})])

        # Plot
        self.plot()

        # Remove proof from graph
        to_remove = []
        for e in self.dg.edges(data=True, keys=True):
            s, t, key, data = e
            if 'is_proof' in self.dg.edges[s, t, key]:
                to_remove.append((s, t, key))

        for (s, t, key) in to_remove:
            self.dg.remove_edge(s, t, key=key)

        # Revert bolded external constraints
        for (s, t, key) in to_revert:
            del self.dg.edges[s, t, key]['linewidth']
