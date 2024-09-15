import "bootstrap/dist/css/bootstrap.css";
import bootstrap from "bootstrap";
import "./style.css";

import React from "react";
import { createRoot } from "react-dom/client";

import * as echarts from "echarts/core";
import { EChartsOption, LineSeriesOption } from "echarts";
import { LineChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from "echarts/components";

import Graph from "echarts/types/src/data/Graph.js";
import { graphic_d } from "echarts/types/dist/shared.js";

import { roundToNearestMinutes } from "date-fns";

echarts.use([
  LineChart,
  CanvasRenderer,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

interface GraphData {
  temperature: LineSeriesOption[];
  humidity: LineSeriesOption[];
}

// Updating the data into a global variable with a publish/subscribe mechanism
let global_graph_data: GraphData | null = null;
const pubSub = () => {
  const callbacks: { () }[] = [];

  const publish = () => {
    callbacks.forEach((callback) => {
      console.log(`publishing to ${callback}`);
      callback();
    });
  };

  const subscribe = (callback: { () }) => {
    console.log(`subscribed ${callback}`);
    callbacks.push(callback);
  };

  return { publish, subscribe };
};
const pub_sub = pubSub();

async function getData(): Promise<GraphData> {
  // Fetch the data, set the global variable, and call "publish" to notify subscribers
  console.log("start of getData()");
  const now = new Date();
  const one_day_ago = new Date(+now - 24 * 60 * 60 * 1000);
  const url = encodeURI(
    `/api/readings/?fields=device_name,mac,timestamp,temperature,humidity&timestamp__gt=${one_day_ago.toISOString()}&ordering=timestamp&limit=2000`,
  );
  const data = await fetch(url).then((response) => response.json()!);
  const temperature_series_data = new Map();
  const humidity_series_data = new Map();

  for (const reading of data.results) {
    if (reading.temperature === null) {
      continue;
    }
    const name = reading.device_name;
    const ts = roundToNearestMinutes(reading.timestamp);
    if (!temperature_series_data.has(name)) {
      temperature_series_data.set(name, {
        name: name,
        type: "line",
        showSymbol: false,
        data: [],
      });
      humidity_series_data.set(name, {
        name: name,
        type: "line",
        showSymbol: false,
        data: [],
      });
    }
    temperature_series_data.get(name).data.push({
      name: name,
      value: [ts, reading.temperature],
    });
    humidity_series_data.get(name).data.push({
      name: name,
      value: [ts, reading.humidity],
    });
  }
  const temperature_series_array = Array.from(
    temperature_series_data,
    ([name, value]) => value,
  );
  const humidity_series_array = Array.from(
    humidity_series_data,
    ([name, value]) => value,
  );
  temperature_series_array.sort((a, b) => (a.name < b.name ? -1 : 1));
  humidity_series_array.sort((a, b) => (a.name < b.name ? -1 : 1));
  const result = {
    temperature: temperature_series_array,
    humidity: humidity_series_array,
  };
  global_graph_data = result;
  pub_sub.publish();
  console.log("end of getData()");
  return result;
}

const defaultOption: EChartsOption = {
  title: {
    text: "Default Title",
  },
  legend: {
    orient: "horizontal",
    bottom: 5,
  },
  tooltip: {
    trigger: "axis",
    axisPointer: {
      animation: false,
    },
  },
  xAxis: {
    type: "time",
    splitLine: {
      show: false,
    },
  },
  yAxis: {
    type: "value",
    position: "right",
    //boundaryGap: [0, '100%'],
    splitLine: {
      show: true,
    },
    min: "dataMin",
    max: "dataMax",
    axisLabel: {
      formatter: "{value} °C",
    },
    minInterval: 1,
  },
};

// Fetch the data on an interval
const update_data_interval = 1000 * 300;
getData();
setInterval(() => {
  getData();
}, update_data_interval);

const Chart = ({ title, aspect, formatter }) => {
  console.log(`aspect=${aspect}`);
  const id = `${aspect}_chart`;
  const chartDomRef = React.useRef(null);

  React.useEffect(() => {
    console.log(`executing chart useEffect ref=${chartDomRef.current}`);
    const chart = echarts.init(chartDomRef.current, "dark");
    const option = { ...defaultOption };
    option.yAxis.axisLabel.formatter = formatter;
    option.title.text = title;
    window.addEventListener("resize", () => {
      chart.resize();
    });
    chart.setOption(option);

    pub_sub.subscribe(() => {
      // "subscribe" to the global variable to update the chart.
      console.log("got data?");
      chart.setOption({ series: global_graph_data[aspect] });
    });
  }, []);

  return (
    <>
      <div id={id} ref={chartDomRef}></div>
    </>
  );
};

const App = () => {
  return (
    <>
      <Chart title="Temperature" aspect="temperature" formatter="{value}°C" />
      <Chart title="Humidity" aspect="humidity" formatter="{value}%" />
    </>
  );
};

const root = createRoot(document.getElementById("app"));
root.render(<App />);
