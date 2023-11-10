$(document).ready(function() {
    // Inicializar la interfaz y actualizar los valores de los sensores
    initSensorUI();
    updateSensorValues();

    // Asignar evento de clic a las filas de la tabla para actualizar la gráfica
    $('.clickable-row').click(function() {
        var sensor = $(this).data('sensor');
        updateGraph(sensor);
    });

    // Actualizar la gráfica regularmente
    setInterval(function() {
        var sensor = $('.clickable-row.active').data('sensor');
        if (sensor) {
            updateGraph(sensor);
        }
    }, 3000);
});

function initSensorUI() {
    // Inicializar elementos de la interfaz relacionados con los sensores

    // Asignar eventos a botones o controles, si existen
    $('#someButton').click(function() {
        // Lógica de manejo de clic del botón
    });

    // Inicializar cualquier elemento interactivo, como sliders o switches
    $('.sensor-switch').each(function() {
        // Inicializar elementos individuales, si es necesario
    });

    // Establecer valores predeterminados o estado inicial de los elementos de la interfaz
    $('#sensor1Value').text("Cargando...");
    $('#sensor2Value').text("Cargando...");
    // Repetir para otros valores de sensores

    // Realizar cualquier configuración inicial adicional
    // Por ejemplo, ocultar ciertos elementos que deben mostrarse solo después de cargar datos
    $('.sensor-data-dependent').hide();
}

function updateSensorValues() {
    // Realizar una solicitud AJAX al servidor para obtener los datos más recientes
    $.ajax({
        url: "/latest_data", // Endpoint para obtener los datos de los sensores
        method: "GET",
        dataType: "json",
        success: function(data) {
            // Procesar y actualizar la interfaz de usuario con los nuevos datos

            // Ejemplo de actualización para múltiples sensores:
            $('#setpointValue').text(data.setpoint || "0"); // Actualizar el valor de setpoint
            $('#pidValue').text(data.sensor1 || "N/A");
            $('#sensor1Value').text(data.sensor1 || "N/A"); // Actualizar sensor 1
            $('#sensor2Value').text(data.sensor2 || "N/A"); 
            $('#sensor3Value').text(data.sensor3 || "N/A"); 
            $('#sensor4Value').text(data.sensor4 || "N/A");
            $('#sensor5Value').text(data.sensor5 || "N/A"); 
            $('#sensor6Value').text(data.sensor6 || "N/A");
            $('#sensor7Value').text(data.sensor7 || "N/A");
            

            // Si se desea agregar alguna lógica adicional en función de los datos recibidos,
            // se puede incluir aquí. Por ejemplo, cambiar el color del texto si un valor es demasiado alto.

        },
        error: function(error) {
            // Manejar cualquier error que ocurra durante la solicitud
            console.log("Error al obtener los datos:", error);
            // Opcionalmente, actualizar la interfaz para reflejar que hubo un error
            $('.sensor-value').text("Error"); // Esto establece un mensaje de error para todos los elementos de clase 'sensor-value'
        },
        complete: function() {
            // Independientemente del resultado, reprogramar la próxima actualización
            setTimeout(updateSensorValues, 3000); // Volver a llamar a esta función después de 3 segundos
        }
    });
}
