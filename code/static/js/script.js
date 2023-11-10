document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("table-body");
    const temperatureChart = new Chart(document.getElementById("temperature-chart"), {
        type: "line",
        data: {
            labels: [],  // Aquí puedes agregar las etiquetas de tiempo (hora:min:seg)
            datasets: [
                {
                    label: "Temperatura °C",
                    data: [],
                    fill: false,
                    borderColor: "rgb(75, 192, 192)",
                    tension: 0.1,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: "time",  // Puedes configurar el eje x como tiempo
                    time: {
                        unit: "second",  // Puedes ajustar la unidad de tiempo
                    },
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: 100,  // Establece el rango máximo del eje y
                },
            },
        },
    });

    // Función para actualizar la tabla y el gráfico
    function updateData() {
        fetch("/get_data")
            .then((response) => response.json())
            .then((data) => {
                // Actualizar la tabla
                tableBody.innerHTML = "";
                for (const entry of data) {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${entry["time"]}</td>
                        <td>${entry["temperature"]}</td>
                    `;
                    tableBody.appendChild(row);
                }

                // Actualizar el gráfico
                temperatureChart.data.labels = data.map((entry) => entry["time"]);
                temperatureChart.data.datasets[0].data = data.map((entry) => entry["temperature"]);
                temperatureChart.update();

                // Llama a esta función periódicamente para obtener datos en tiempo real
                setTimeout(updateData, 1000); // Actualiza cada segundo
            })
            .catch((error) => {
                console.error("Error al obtener datos:", error);
            });
    }

    // Llama a la función para obtener datos inicialmente
    updateData();
});
