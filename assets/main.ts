import * as echarts from 'echarts';
import { decodeAsync } from "@msgpack/msgpack";

type EChartsOption = echarts.EChartsOption;

const chartDom = document.getElementById('main')!;
var myChart = echarts.init(chartDom);
var option: EChartsOption;

interface DataItem {
  name: string;
  value: [string, number];
}

interface Series {
  name: string
  data: DataItem[]
}

async function getData() {
  const now = new Date()
  const one_day_ago = new Date(+now - (24 * 60 * 60 * 1000))
  const url = encodeURI(`/api/readings/?fields=device_name,mac,timestamp,temperature,humidity&timestamp__gt=${one_day_ago.toISOString()}&ordering=timestamp&limit=2000`)
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/msgpack'
    }
  })
  const data = await decodeAsync(response.body!);

  let series_data = new Map()

  for (const reading of data.results) {
    if (reading.temperature === null) {
      continue
    }
    const name = reading.device_name
    if (!series_data.has(name)) {
      series_data.set(name, 
        {
          name: name,
          type: 'line',
          showSymbol: false,
          data: []
        }
      )
    }
    series_data.get(name).data.push(
      {
        name: name,
        value: [reading.timestamp, reading.temperature]
      }
    )
  }
  const series_array = Array.from(series_data, ([name, value]) => value)
  series_array.sort((a, b) => a.name < b.name ? -1: 1);
  return series_array
}

option = {
  title: {
    text: 'Temperature'
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
};


myChart.showLoading()
myChart.setOption(option)

getData().then((value) => {
  option['series'] = value
  myChart.hideLoading()
  myChart.setOption(option)
})

window.addEventListener('resize', function() {
  myChart.resize();
});

setInterval(() => {
  console.log("updating series data")
  getData().then((series_data) => {
    myChart.setOption({
      series: series_data
    })
  })
}, 1000 * 300)
