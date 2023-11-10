$(document).ready(function() {
    var currentSensor = 'sensor1';

    function initChart() {
        var ctx = document.getElementById('temperatureCanvas').getContext('2d');
        window.temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperatura',
                    data: [],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }


    function updateGraph(sensor) {
        // Si es PID, entonces necesitamos manejarlo de manera especial
        if (sensor === 'pid') {
            // Obtén los datos para setpoint y sensor1 y combínalos
            $.when(
                $.ajax({url: "/latest_data_for_graph", method: "GET", data: {sensor: 'setpoint'}, dataType: "json"}),
                $.ajax({url: "/latest_data_for_graph", method: "GET", data: {sensor: 'sensor1'}, dataType: "json"})
            ).done(function(setpointResponse, sensor1Response) {
                // Extraer los datos de las respuestas
                var setpointData = setpointResponse[0];
                var sensor1Data = sensor1Response[0];
    
                // Asegúrate de que la estructura de datos es la esperada
                if (!setpointData || !sensor1Data || !setpointData.label || !sensor1Data.label || !setpointData.value0 || !sensor1Data.value1) {
                    console.error("Error: Datos recibidos son incompletos o no válidos para PID.", setpointData, sensor1Data);
                    return;
                }
    
                // Configurar los datos para la gráfica de PID
                var pidLabels = setpointData.label; // Usa las etiquetas del setpoint
                var pidSetpointData = setpointData.value0; // Datos del setpoint
                var pidSensor1Data = sensor1Data.value1; // Datos del sensor 1
    
                // Asegúrate de que la gráfica PID tenga dos conjuntos de datos
                window.temperatureChart.data.labels = pidLabels;
                window.temperatureChart.data.datasets = [
                    {
                        label: 'Setpoint',
                        data: pidSetpointData,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        fill: false,
                    },
                    {
                        label: 'Sensor 1',
                        data: pidSensor1Data,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        fill: false,
                    }
                ];
                window.temperatureChart.update();
            });
        } else {
            // Manejo normal de la actualización de gráficos para otros sensores
            $.ajax({
                url: "/latest_data_for_graph",
                method: "GET",
                data: { sensor: sensor },
                dataType: "json",
                success: function(data) {
                    var valueKey = sensor === 'setpoint' ? 'value0' : 'value' + sensor.slice(-1);
                    if (!data || !data.label || !data[valueKey]) {
                        console.error("Error: Datos recibidos son incompletos o no válidos.", data);
                        return;
                    }
                    
                    window.temperatureChart.data.labels = data.label;
                    window.temperatureChart.data.datasets[0].data = data[valueKey];
                    // Asegúrate de eliminar el segundo conjunto de datos si existe
                    if (window.temperatureChart.data.datasets.length > 1) {
                        window.temperatureChart.data.datasets.pop();
                    }
                    window.temperatureChart.update();
    
                    // Actualiza el valor actual del sensor en la tabla
                    if (data.currentValue !== undefined) {
                        updateSensorCurrentValue(sensor, data.currentValue);
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Error fetching data: ", status, error);
                }
            });
        }
    }
    
    


    function updateSensorCurrentValue(sensor, value) {
        
        $('#' + sensor + 'Value').text(value);
    }

    function updateCurrentGraph() {
        updateGraph(currentSensor);
    }

    window.updateGraph = updateGraph;
    window.initChart = initChart;

    initChart();
    updateGraph(currentSensor);

    // Establece un intervalo para actualizar la gráfica actual automáticamente
    setInterval(updateCurrentGraph, 1500); // Actualiza cada 5 segundos

    // Event handlers y otras inicializaciones
    $('body').on('click', '.clickable-row', function() {
        // Actualiza la variable currentSensor cada vez que el usuario selecciona un sensor diferente
        currentSensor = $(this).data('sensor');
        updateGraph(currentSensor);


    });
   
});
