async function getData() {
    const currentURL = window.location.href;
    const objID = parseInt(currentURL.split("/")[4]);

    if (isNaN(objID)) {
        throw new Error("Invalid URL: can't extract object ID");
    }

    try {
        const response = await fetch(`/api/tabledata/${objID}/`);
        if (!response.ok) {
            throw new Error(
                `Network response was not ok: ${response.statusText}`
            );
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Fetch Error: ${error}`);
        throw error;
    }
}

function drawTable(data, table) {
    const numOfFields = data.length;

    for (let i = 0; i < numOfFields; i++) {
        const row = document.createElement("tr");

        for (let j = 0; j < data[i].length; j++) {
            const td = document.createElement("td");

            if (i == 1) td.setAttribute("data-value", `${data[i][j]}`);

            td.innerHTML = data[i][j];
            row.appendChild(td);
        }
        table.appendChild(row);
    }
}

function editTable(table) {
    table.addEventListener("click", (e) => {
        const activeTd = e.target;

        if (activeTd.querySelector("input")) {
            return;
        }

        const input = document.createElement("input");
        input.value = activeTd.innerHTML;
        activeTd.innerHTML = "";
        activeTd.appendChild(input);

        input.addEventListener("blur", () => {
            activeTd.innerHTML = input.value;
            if (activeTd.hasAttribute("data-value")) {
                const intValue = Number(input.value);
                if (isNaN(intValue)) {
                    alert("You are trying to input a string");
                    activeTd.innerHTML = activeTd.getAttribute("data-value");
                    return;
                }
                activeTd.setAttribute("data-value", `${input.value}`);
            }
            input.remove();
        });

        input.focus();
    });
}

function openTab(page) {
    document.querySelectorAll(".tabcontent").forEach((element) => {
        element.style.display = "none";
    });

    document.querySelector(`#${page}`).style.display = "block";
}

function drawChart(canvas, labels, values, typed = "line", chart = null) {
    if (chart) {
        chart.destroy();
    }

    const bcColor = [
        "rgba(255, 99, 132, 0.2)",
        "rgba(54, 162, 235, 0.2)",
        "rgba(255, 206, 86, 0.2)",
        "rgba(75, 192, 192, 0.2)",
        "rgba(153, 102, 255, 0.2)",
        "rgba(255, 159, 64, 0.2)",
    ];
    const bdColor = [
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(75, 192, 192, 1)",
        "rgba(153, 102, 255, 1)",
        "rgba(255, 159, 64, 1)",
    ];

    chart = new Chart(canvas, {
        type: typed, // 'pie', 'doughnut', 'bar', 'bubble', 'line', 'polarArea', 'radar', 'scatter'
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Data",
                    data: values,
                    backgroundColor: bcColor,
                    borderColor: bdColor,
                    borderWidth: 1,
                },
            ],
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true,
                },
                y: {
                    beginAtZero: true,
                },
            },
        },
    });
    return chart;
}

let chart = null;
let data = null;

document.addEventListener("DOMContentLoaded", () => {
    const chartObj = document.querySelector("#chartfield").getContext("2d");
    const table = document.querySelector("#df-content");
    openTab("Chart");

    getData().then((fetchedData) => {
        data = fetchedData;
        chart = drawChart(chartObj, data.labels, data.values);
        drawTable([data.labels, data.values], table);
        editTable(table);
    });

    document.querySelectorAll(".tablink").forEach((button) => {
        button.addEventListener("click", () => {
            if (button.hasAttribute("data-type")) {
                openTab("Chart");
                const type = button.getAttribute("data-type");
                chart = drawChart(
                    chartObj,
                    data.labels,
                    data.values,
                    type,
                    chart
                );
            } else {
                openTab("Table");
            }
        });
    });
});
