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
                if (isNaN(intValue)) {
                    alert("You are trying to input a string");
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

sendPostRequest = async (url, labels, values) => {
    try {
        const response = await axios.post(url, { labels, values });
        console.log("POST request sent successfully");
        console.log(response.data);
    } catch (error) {
        console.error(error.response.data);
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector("#df-content");
    const confirmButton = document.querySelector(".confirm");

    getData().then((fetchedData) => {
        drawTable([fetchedData.labels, fetchedData.values], table);
        editTable(table);
    });

    function confirmPostRequest() {
        const currentURL = window.location.href;
        const objID = parseInt(currentURL.split("/")[4]);

        const postData = [[], []];

        const tableRows = table.querySelectorAll("tr");
        for (let row = 0; row < tableRows.length; row++) {
            const currentRow = tableRows[row].querySelectorAll("td");
            
            currentRow.forEach((cell) => {
                postData[row].push(cell.textContent);
            })
        }
        console.log(postData);
        sendPostRequest(`/api/tabledata/${objID}/`, postData[0], postData[1]);
    };

    confirmButton.addEventListener("click", confirmPostRequest);
});
