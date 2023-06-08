function getObjID() {
    const currentURL = window.location.href;

    const objID = parseInt(currentURL.split("/")[4]);
    if (isNaN(objID)) {
        throw new Error("Invalid URL: can't extract object ID");
    }

    return objID;
}

async function getData() {
    const objID = getObjID();

    try {
        const response = await axios.get(`/api/datasetfile-data/${objID}/`);

        return response.data;
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
        "#ff638433",
        "#36a2eb33",
        "#ffce5633",
        "#4bc0c033",
        "#9966ff33",
        "#ff9f4033",
    ];
    const bdColor = [
        "#ff6384",
        "#36a2eb",
        "#ffce56",
        "#4bc0c0",
        "#9966ff",
        "#ff9f40",
    ];

    chart = new Chart(canvas, {
        type: typed,
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
                x: { beginAtZero: true },
                y: { beginAtZero: true },
            },
        },
    });
    return chart;
}

let chart = null;
let data = null;

document.addEventListener("DOMContentLoaded", () => {
    const chartCanvas = document.querySelector("#chartfield").getContext("2d");
    const table = document.querySelector("#df-content");
    openTab("Chart");

    getData().then((fetchedData) => {
        data = fetchedData;
        chart = drawChart(chartCanvas, data.labels, data.values);
        drawTable([data.labels, data.values], table);
    });

    document.querySelectorAll(".tablink").forEach((button) => {
        button.addEventListener("click", () => {
            if (button.hasAttribute("data-type")) {
                openTab("Chart");
                const type = button.getAttribute("data-type");
                chart = drawChart(
                    chartCanvas,
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

    document.querySelectorAll("[download-type]").forEach((e) => {
        const type = e.getAttribute("download-type");
        e.setAttribute("href", `/exportfile/${type}/${getObjID()}/`);
    });
});
