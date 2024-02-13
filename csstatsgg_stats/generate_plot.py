import plotly.graph_objects as go


def generate_plot(stats_dicts, subject_title, subject_name):
    rank_axis = list(map(lambda x: x["rank"], stats_dicts))
    low_data = list(map(lambda x: x["minimum"], stats_dicts))
    open_data = list(map(lambda x: x["q1"], stats_dicts))
    close_data = list(map(lambda x: x["q3"], stats_dicts))
    high_data = list(map(lambda x: x["maximum"], stats_dicts))

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=rank_axis,
                open=open_data,
                high=high_data,
                low=low_data,
                close=close_data,
                increasing_line_color="#FF1A75",
            )
        ],
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        title=go.layout.Title(
            text=f"{subject_title} winrate by rank<br><sup>Players with >=10 tracked matches (via csstats.gg)</sup>",
            xref="paper",
            x=0,
        ),
        yaxis_title="Winrate",
        xaxis_title="Rank",
        plot_bgcolor="#222222",
        font=go.layout.Font(color="white"),
        paper_bgcolor="#222222",
    )
    fig.update_xaxes(
        mirror=True,  # draw top line
        showline=True,  # draw bottom line
        ticks="outside",  # bottom ticks
        linecolor="lightgrey",
        gridcolor="lightgrey",
        tickcolor="lightgrey",
        showgrid=False,  # hide vertical lines
    )
    fig.update_yaxes(
        showline=False,  # hide left line
        showgrid=True,  # draw horizontal lines
        ticks="",  # hide left side ticks
        gridcolor="lightgrey",
        dtick=0.25,  # space horizontal lines
        range=[0, 1],
    )

    fig.write_image(f"output/{subject_name}.svg")
