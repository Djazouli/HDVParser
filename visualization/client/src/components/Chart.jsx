import React, {Component} from "react";
import {TimeSeries} from "pondjs";
import {Charts, ChartContainer, ChartRow, YAxis, ScatterChart, Legend} from "react-timeseries-charts";

const Chart = ({data}) => {
    if (Object.keys(data).length === 0) {
        return <div>No data</div>;
    }
    const index = ["price1", "price10", "price100"];

    const points = [];
    for (let [timestamp, values] of Object.entries(data)) {
        const point = [timestamp, values[1] ? values[1] : null, values[10] ? values[10] / 10 : null, values[100] ? values[100] / 100 : null];
        points.push(point);
    }

    const timeserieData = {
        name: "Price",
        "columns": ["time", ...index],
        points,
    };
    console.log(timeserieData);
    const style = {
        "price1": {normal: {stroke: "#E3C81C", fill: "none", strokeWidth: 1}},
        "price10": {normal: {stroke: "#F68B24", fill: "none", strokeWidth: 1}},
        "price100": {normal: {stroke: "#691130", fill: "none", strokeWidth: 1}},
    };
    const timeserie = new TimeSeries(timeserieData);
    const max = Math.max(...index.map(index => timeserie.max(index) ? timeserie.max(index) : 0));
    const min = Math.min(...index.map(index => timeserie.min(index) ? timeserie.min(index) : 0));
    return <div>
        <ChartContainer
            timeRange={timeserie.timerange()}
            enablePanZoom
            enableDragZoom
            width={1600}
        >
            <ChartRow height={400} >
                <YAxis
                    id="axis1"
                    label="Kamousse"
                    width="60"
                    type="linear"
                    max={max + 10}
                    min={Math.max(0, min-5)}
                    format=".2f"/>
                <Charts>
                    <ScatterChart
                        axis="axis1"
                        series={timeserie}
                        style={style}
                        columns={["price1", "price10", "price100"]}
                    />

                </Charts>
            </ChartRow>
        </ChartContainer>
        <Legend
            type="dot"
            align="right"
            style={style}
            categories={[
                {key: "price1", label: "1",},
                {key: "price10", label: "10",},
                {key: "price100", label: "100",},
            ]}/>
    </div>

};

export default Chart;