import * as echarts from 'echarts/core';
import { EChartsOption, LineSeriesOption } from 'echarts';
import { LineChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components';
import Graph from 'echarts/types/src/data/Graph.js';
import { graphic_d } from 'echarts/types/dist/shared.js';

import { roundToNearestMinutes } from 'date-fns';

echarts.use([
  LineChart,
  CanvasRenderer,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])


const temperatureChartDom = document.getElementById('temperature_chart')!
const temperatureChart = echarts.init(temperatureChartDom);
const humidityChartDom = document.getElementById('humidity_chart')!
const humidityChart = echarts.init(humidityChartDom);


interface GraphData {
  temperature: LineSeriesOption[]
  humidity: LineSeriesOption[]
}



async function getData(): Promise<GraphData> {
  const now = new Date()
  const one_day_ago = new Date(+now - (24 * 60 * 60 * 1000))
  const url = encodeURI(`/api/readings/?fields=device_name,mac,timestamp,temperature,humidity&timestamp__gt=${one_day_ago.toISOString()}&ordering=timestamp&limit=2000`)
  const data = await fetch(url).then((response) => response.json()!)
  const temperature_series_data = new Map()
  const humidity_series_data = new Map()

  for (const reading of data.results) {
    if (reading.temperature === null) {
      continue
    }
    const name = reading.device_name
    const ts = roundToNearestMinutes(reading.timestamp)
    if (!temperature_series_data.has(name)) {
      temperature_series_data.set(name, 
        {
          name: name,
          type: 'line',
          showSymbol: false,
          data: []
        }
      )
      humidity_series_data.set(name, 
        {
          name: name,
          type: 'line',
          showSymbol: false,
          data: []
        }
      )
    }
    temperature_series_data.get(name).data.push(
      {
        name: name,
        value: [ts, reading.temperature]
      }
    )
    humidity_series_data.get(name).data.push(
      {
        name: name,
        value: [ts, reading.humidity]
      }
    )
  }
  const temperature_series_array = Array.from(temperature_series_data, ([name, value]) => value)
  const humidity_series_array = Array.from(humidity_series_data, ([name, value]) => value)
  temperature_series_array.sort((a, b) => a.name < b.name ? -1: 1)
  humidity_series_array.sort((a, b) => a.name < b.name ? -1: 1)
  return {
    "temperature": temperature_series_array,
    "humidity": humidity_series_array
  }
}

temperatureChart.showLoading()
temperatureChart.setOption<EChartsOption>({
  title: {
    text: "Temperature"
  },
  legend: {    
    orient: 'horizontal',
    bottom: 5
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      animation: false
    }
  },
  xAxis: {
    type: 'time',
    splitLine: {
      show: false
    }
  },
  yAxis: {
    type: 'value',
    position: 'right',
    //boundaryGap: [0, '100%'],
    splitLine: {
      show: true
    },
    min: 'dataMin',
    max: 'dataMax',
    axisLabel: {
      formatter: '{value} °C'
    },
    minInterval: 1,
  },
})
humidityChart.showLoading()
humidityChart.setOption<EChartsOption>({
  title: {
    text: "Relative Humidity"
  },
  legend: {    
    orient: 'horizontal',
    bottom: 5
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      animation: false
    }
  },
  xAxis: {
    type: 'time',
    splitLine: {
      show: false
    }
  },
  yAxis: {
    type: 'value',
    position: 'right',
    //boundaryGap: [0, '100%'],
    splitLine: {
      show: true
    },
    min: 'dataMin',
    max: 'dataMax',
    axisLabel: {
      formatter: '{value}%'
    },
    minInterval: 1,
  },
})


getData().then((graph_data) => {
  temperatureChart.hideLoading()
  temperatureChart.setOption<EChartsOption>({
    series: graph_data.temperature
  })
  humidityChart.hideLoading()
  humidityChart.setOption<EChartsOption>({
    series: graph_data.humidity
  })
})

window.addEventListener('resize', function() {
  temperatureChart.resize()
  humidityChart.resize()
});

setInterval(() => {
  console.log("updating series data")
  getData().then((series_data) => {
    temperatureChart.setOption<EChartsOption>({
      series: series_data.temperature
    })
    humidityChart.setOption<EChartsOption>({
      series: series_data.humidity
    })
  })
}, 1000 * 300)
