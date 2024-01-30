import bokeh.models as bkm
import holoviews as hv
import panel as pn

import numpy as np

from .. import config

def get_connected_edges(edges_parent, edges_child, node_id):
    is_parent = edges_parent == node_id
    is_child = edges_child == node_id
    children = edges_child[is_parent]
    parents = edges_parent[is_child]
    idx_one = np.flatnonzero(is_parent)
    col_one = np.zeros(idx_one.size, dtype=int)
    idx_two = np.flatnonzero(is_child)
    col_two = np.ones(idx_two.size, dtype=int)
    return np.concatenate((idx_one, idx_two)), np.concatenate((col_one, col_two))


def page(tsm):
    hv.extension("bokeh")
    edges_df = tsm.edges_df
    node_id_input = pn.widgets.TextInput(value="", name="Node ID")
    edges_df["parent_time_right"] = edges_df["parent_time"]
    tabulator = pn.widgets.Tabulator(show_index=False)

    def plot_data(node_id):
        if len(node_id) > 0:
            edges, degree = get_connected_edges(edges_df["parent"], edges_df["child"], int(node_id))
            filtered_df = edges_df.iloc[edges].copy()
            filtered_df["degree"] = degree
            #filtered_df = edges_df[edges_df["child"] == int(node_id)]
            segments = hv.Segments(
                filtered_df,
                kdims=["left", "parent_time", "right", "parent_time_right"],
                vdims=["child", "parent", "span", "branch_length", "degree"],
            )
            hover_tool = bkm.HoverTool(
                tooltips=[
                    ("child", "@child"),
                    ("parent", "@parent"),
                    ("span", "@span"),
                    ("branch_length", "@branch_length"),
                    ("num_mutations", "@num_mutations"),
                ]
            )
            segments = segments.opts(
                width=config.PLOT_WIDTH,
                height=config.PLOT_HEIGHT,
                tools=[hover_tool],
                xlabel="Position",
                ylabel="Time",
                color=hv.dim("degree"),
                cmap="bkr",
            )

            filtered_df = filtered_df.drop(columns=["parent_time_right"])
            tabulator.value = filtered_df

            return segments
        else:
            return pn.pane.Markdown("Please enter a Node ID.")

    dynamic_plot = pn.bind(plot_data, node_id=node_id_input)

    return pn.Column(node_id_input, dynamic_plot, tabulator)
