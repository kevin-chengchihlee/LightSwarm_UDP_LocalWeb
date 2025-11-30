#!/usr/bin/env python3
"""
LightSwarm Web Dashboard - Real-Time Browser Plotting
Uses Chart.js for true real-time plotting in the browser
"""

from flask import Flask, render_template_string, jsonify
import plot as PLOT
import state_machine_v04 as STATE

web = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>LightSwarm Real-Time Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
      color: white;
      min-height: 100vh;
      padding: 20px;
    }
    
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    header {
      text-align: center;
      margin-bottom: 30px;
    }
    
    h1 {
      color: #4CAF50;
      font-size: 2.5em;
      margin-bottom: 10px;
      text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    .subtitle {
      color: #aaa;
      font-size: 1.1em;
    }
    
    .controls {
      display: flex;
      justify-content: center;
      gap: 15px;
      margin: 25px 0;
      flex-wrap: wrap;
    }
    
    button {
      background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
      color: white;
      padding: 14px 28px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      font-weight: 600;
      transition: all 0.3s ease;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    
    button:active {
      transform: translateY(0);
    }
    
    .export-btn {
      background: linear-gradient(135deg, #2196F3 0%, #0b7dda 100%);
    }
    
    .status {
      text-align: center;
      margin: 15px 0;
      padding: 12px 24px;
      background-color: #2e2e2e;
      border-radius: 8px;
      display: inline-block;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      font-size: 1.05em;
    }
    
    .status-container {
      text-align: center;
    }
    
    .chart-container {
      background: #2e2e2e;
      padding: 25px;
      border-radius: 12px;
      box-shadow: 0 8px 16px rgba(0,0,0,0.4);
      margin: 20px 0;
    }
    
    canvas {
      background: #1a1a1a;
      border-radius: 8px;
    }
    
    .info-box {
      background: #2e2e2e;
      padding: 15px;
      border-radius: 8px;
      margin-top: 20px;
      border-left: 4px solid #4CAF50;
    }
    
    .info-box h3 {
      color: #4CAF50;
      margin-bottom: 10px;
    }
    
    .info-box p {
      color: #ccc;
      line-height: 1.6;
    }
    
    @media (max-width: 768px) {
      h1 {
        font-size: 1.8em;
      }
      
      button {
        padding: 10px 20px;
        font-size: 14px;
      }
      
      .chart-container {
        padding: 15px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🔆 LightSwarm Real-Time Dashboard</h1>
      <p class="subtitle">Live Brightness Monitoring & Master Device Tracking</p>
    </header>
    
    <div class="controls">
      <button onclick="resetPlot()">🔄 Reset Plot</button>
      <button onclick="exportLog()" class="export-btn">💾 Export Log</button>
    </div>
    
    <div class="status-container">
      <div class="status" id="status">
        <span style="color: #4CAF50;">●</span> Status: Active
      </div>
    </div>
    
    <div class="chart-container">
      <canvas id="brightnessChart"></canvas>
    </div>
    
    <div class="chart-container">
      <canvas id="masterChart"></canvas>
    </div>
    
    <div class="info-box">
      <h3>📋 Dashboard Info</h3>
      <p>
        • <strong>Real-time plotting:</strong> Charts render live in your browser<br>
        • <strong>Update rate:</strong> 1 second<br>
        • <strong>Window:</strong> Last 30 seconds of data<br>
        • <strong>Devices:</strong> Tracking 3 LightSwarm devices<br>
        • <strong>Interactive:</strong> Hover over data points for details
      </p>
    </div>
  </div>

  <script>
    let lastResetCounter = -1;
    
    // Initialize Brightness Line Chart
    const brightnessCtx = document.getElementById('brightnessChart').getContext('2d');
    const brightnessChart = new Chart(brightnessCtx, {
      type: 'line',
      data: {
        datasets: [
          {
            label: 'Device 0 Brightness',
            type: 'scatter',
            data: [],
            borderColor: '#00ff00',
            backgroundColor: 'rgba(0, 255, 0, 0.1)',
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#00ff00',
            tension: 0.1,
            showLine: false
          },
          {
            label: 'Device 1 Brightness',
            type: 'scatter',
            data: [],
            borderColor: '#ffff00',
            backgroundColor: 'rgba(255, 255, 0, 0.1)',
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#ffff00',
            tension: 0.1,
            showLine: false
          },
          {
            label: 'Device 2 Brightness',
            type: 'scatter',
            data: [],
            borderColor: '#ff0000',
            backgroundColor: 'rgba(255, 0, 0, 0.1)',
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#ff0000',
            tension: 0.1,
            showLine: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2.5,
        interaction: {
          mode: 'nearest',
          intersect: false
        },
        scales: {
          x: {
            type: 'linear',
            title: { 
              display: true, 
              text: 'Time (s)', 
              color: '#fff',
              font: { size: 14 }
            },
            ticks: { color: '#aaa' },
            grid: { color: '#333' }
          },
          y: {
            title: { 
              display: true, 
              text: 'PhotoCell Reading', 
              color: '#fff',
              font: { size: 14 }
            },
            min: 0,
            max: 5000,
            ticks: { color: '#aaa' },
            grid: { color: '#333' }
          }
        },
        plugins: {
          legend: { 
            labels: { 
              color: '#fff',
              font: { size: 13 }
            } 
          },
          title: {
            display: true,
            text: 'LightSwarm Brightness',
            color: '#fff',
            font: { size: 18, weight: 'bold' }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#4CAF50',
            borderWidth: 1
          }
        },
        animation: {
          duration: 0
        }
      }
    });

    // Initialize Master Count Bar Chart
    const masterCtx = document.getElementById('masterChart').getContext('2d');
    const masterChart = new Chart(masterCtx, {
      type: 'bar',
      data: {
        labels: ['Device 0', 'Device 1', 'Device 2'],
        datasets: [{
          label: 'Master Count',
          data: [0, 0, 0],
          backgroundColor: ['#00ff00', '#ffff00', '#ff0000'],
          borderWidth: 2,
          borderColor: ['#00cc00', '#cccc00', '#cc0000']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 3,
        scales: {
          y: {
            beginAtZero: true,
            max: 30,
            title: { 
              display: true, 
              text: 'Accumulative Master Count', 
              color: '#fff',
              font: { size: 14 }
            },
            ticks: { 
              color: '#aaa',
              stepSize: 5
            },
            grid: { color: '#333' }
          },
          x: {
            ticks: { color: '#aaa' },
            grid: { color: '#333' }
          }
        },
        plugins: {
          legend: { 
            labels: { 
              color: '#fff',
              font: { size: 13 }
            } 
          },
          title: {
            display: true,
            text: 'Device Master Chart',
            color: '#fff',
            font: { size: 18, weight: 'bold' }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff',
            borderColor: '#4CAF50',
            borderWidth: 1
          }
        },
        animation: {
          duration: 500
        }
      }
    });

    // ✅ UPDATE WITH EXTERNAL RESET DETECTION
    async function updateCharts() {
      try {
        const response = await fetch('/data');
        const data = await response.json();
        
        // ✅ DETECT EXTERNAL RESET (from button press)
        if (lastResetCounter !== -1 && data.reset_counter !== lastResetCounter) {
          console.log('🔄 External reset detected! Clearing charts...');
          
          // Clear all chart data
          brightnessChart.data.datasets[0].data = [];
          brightnessChart.data.datasets[1].data = [];
          brightnessChart.data.datasets[2].data = [];
          masterChart.data.datasets[0].data = [0, 0, 0];
          
          // Reset axis ranges
          brightnessChart.options.scales.x.min = 0;
          brightnessChart.options.scales.x.max = 30;
          
          // Show notification
          updateStatus('🔄 External reset detected!', '#FFA500');
          setTimeout(() => {
            updateStatus('● Status: Active', '#4CAF50');
          }, 2000);
        }
        
        // Update reset counter tracker
        lastResetCounter = data.reset_counter;
        
        // Update brightness chart datasets
        brightnessChart.data.datasets[0].data = data.time0.map((x, i) => ({
          x: x,
          y: data.brightness0[i]
        }));
        
        brightnessChart.data.datasets[1].data = data.time1.map((x, i) => ({
          x: x,
          y: data.brightness1[i]
        }));
        
        brightnessChart.data.datasets[2].data = data.time2.map((x, i) => ({
          x: x,
          y: data.brightness2[i]
        }));
        
        // Update x-axis range
        if (data.current_time > 30) {
          brightnessChart.options.scales.x.min = data.current_time - 30;
          brightnessChart.options.scales.x.max = data.current_time;
        } else {
          brightnessChart.options.scales.x.min = 0;
          brightnessChart.options.scales.x.max = 30;
        }
        
        brightnessChart.update('none');
        
        // Update master count chart
        masterChart.data.datasets[0].data = data.master_count;
        masterChart.update('none');
        
      } catch (error) {
        console.error('Error updating charts:', error);
        updateStatus('✗ Connection error', '#f44336');
      }
    }

    async function resetPlot() {
      try {
        updateStatus('⏳ Resetting...', '#FFA500');
        const response = await fetch('/reset', { method: 'POST' });
        const data = await response.json();
        updateStatus('✓ ' + data.message, '#4CAF50');
        setTimeout(() => {
          updateStatus('● Status: Active', '#4CAF50');
        }, 2000);
      } catch (error) {
        updateStatus('✗ Error: ' + error.message, '#f44336');
      }
    }

    async function exportLog() {
      try {
        updateStatus('⏳ Exporting...', '#FFA500');
        const response = await fetch('/export', { method: 'POST' });
        const data = await response.json();
        updateStatus('✓ ' + data.message, '#4CAF50');
        setTimeout(() => {
          updateStatus('● Status: Active', '#4CAF50');
        }, 3000);
      } catch (error) {
        updateStatus('✗ Error: ' + error.message, '#f44336');
      }
    }
    
    function updateStatus(message, color) {
      const status = document.getElementById('status');
      status.innerHTML = message;
      status.style.borderLeft = '4px solid ' + color;
    }

    // Start real-time updates
    setInterval(updateCharts, 1000);
    updateCharts(); // Initial load
  </script>
</body>
</html>
"""

@web.route("/")
def home():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@web.route("/data")
def get_data():
    """API endpoint: Get current plot data"""
    data = PLOT.get_plot_data()
    return jsonify(data)

@web.route("/reset", methods=["POST"])
def reset_plot():
    """API endpoint: Reset plot"""
    STATE.state_machine()
    return jsonify({
        "status": "success",
        "message": "Plot reset successfully!"
    })

@web.route("/export", methods=["POST"])
def export_log():
    """API endpoint: Export log"""
    try:
        PLOT.ex_log()
        return jsonify({
            "status": "success",
            "message": "Log exported successfully!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Export failed: {str(e)}"
        }), 500

@web.route("/status")
def status():
    """API endpoint: System status"""
    data = PLOT.get_plot_data()
    return jsonify({
        "status": "running",
        "master_count": data['master_count'],
        "window_size": PLOT.WINDOW,
        "data_points": {
            "device0": len(data['time0']),
            "device1": len(data['time1']),
            "device2": len(data['time2'])
        }
    })