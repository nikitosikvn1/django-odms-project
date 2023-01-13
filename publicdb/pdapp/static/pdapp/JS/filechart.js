async function getData() {
    const curreentURL = window.location.href;
    const objID = parseInt(curreentURL.split('/')[4]);
    
    const data = fetch(`/api/tabledata/${objID}/`)
    .then(Response => Response.json())
    .catch(Error => {
        console.log('Error: ', Error);
    });

    return await data;
}

function DrawChart(canvas, labels, values, typed='line') {
    const bcColor = [
        'rgba(255, 99, 132, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 206, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(255, 159, 64, 0.2)'
    ];
    const bdColor = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
    ];

    const chart = new Chart(canvas, {
        type: typed, // 'pie', 'doughnut', 'bar', 'bubble', 'line', 'polarArea', 'radar', 'scatter'
        data: {
            labels: labels,
            datasets: [{
                label: 'Data',
                data: values,
                backgroundColor: bcColor,
                borderColor: bdColor,
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const chartObj = document.querySelector('#chartfield').getContext('2d');
    const cData = getData().then((data) => {
        DrawChart(chartObj, data.labels, data.values);
    });
});