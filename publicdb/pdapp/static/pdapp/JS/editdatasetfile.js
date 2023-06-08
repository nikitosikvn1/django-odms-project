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

            if (i === 1) td.setAttribute("data-value", `${data[i][j]}`);

            td.textContent = data[i][j];
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
        input.value = activeTd.textContent;
        activeTd.textContent = "";
        activeTd.appendChild(input);

        input.addEventListener("blur", () => {
            activeTd.textContent = input.value;
            if (activeTd.hasAttribute("data-value")) {
                const intValue = Number(input.value);
                if (isNaN(intValue) || intValue === 0) {
                    alert("Wrong data format input");
                    activeTd.textContent = activeTd.getAttribute("data-value");
                    return;
                }
                activeTd.setAttribute("data-value", `${input.value}`);
            }
            input.remove();
        });

        input.focus();
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

async function sendPostRequest(url, labels, values) {
    const csrfToken = getCookie("csrftoken");
    try {
        const response = await axios.post(
            url,
            { labels, values },
            {
                headers: {
                    "X-CSRFToken": csrfToken,
                },
            }
        );
        if (response.status === 200) {
            console.log("POST request sent successfully");
            console.log(response.data);
            return response.data;
        } else {
            throw new Error(`Request failed with status ${response.status}`);
        }
    } catch (error) {
        console.error(error.message);
        throw error;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector("#df-content");
    const confirmButton = document.querySelector(".confirm");
    let initialData = null;

    getData().then((fetchedData) => {
        initialData = [fetchedData.labels, fetchedData.values];
        drawTable(initialData, table);
        editTable(table);
    });

    function confirmPostRequest() {
        const objID = getObjID();

        const tableRows = table.querySelectorAll("tr");
        const postData = Array.from(tableRows).map((row) => {
            return Array.from(row.querySelectorAll("td")).map(
                (cell) => cell.textContent
            );
        });

        if (JSON.stringify(postData) === JSON.stringify(initialData)) {
            alert("No changes were made.");
            return;
        }

        console.log(initialData);

        sendPostRequest(
            `/api/datasetfile-data/${objID}/`,
            postData[0],
            postData[1]
        ).then((response) => {
            if (!response.ok) {
                alert(`Error sending request: ${response.status}`);
            }
            initialData = postData;
        });
    }

    confirmButton.addEventListener("click", confirmPostRequest);
});
