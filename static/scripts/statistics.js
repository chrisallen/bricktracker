/**
 * Statistics page chart functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if charts are enabled and chart data exists
    if (typeof window.chartData === 'undefined') {
        return;
    }

    // Debug: Log chart data to console
    console.log('Chart Data:', window.chartData);

    // Get current theme colors
    const isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const textColor = isDarkMode ? '#f8f9fa' : '#212529';
    const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Common chart configuration
    const commonConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Release Year',
                        color: textColor
                    },
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        display: false,
                        color: gridColor
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count',
                        color: textColor
                    },
                    ticks: {
                        precision: 0,
                        color: textColor
                    },
                    grid: {
                        color: gridColor
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    cornerRadius: 4
                }
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 5
                },
                line: {
                    borderWidth: 2
                }
            }
        }
    };

    // Sets Chart
    const setsCanvas = document.getElementById('setsChart');
    if (setsCanvas) {
        const setsCtx = setsCanvas.getContext('2d');
        new Chart(setsCtx, {
            ...commonConfig,
            data: {
                labels: window.chartData.years,
                datasets: [{
                    label: 'Sets',
                    data: window.chartData.sets,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            }
        });
    }

    // Parts Chart
    const partsCanvas = document.getElementById('partsChart');
    if (partsCanvas) {
        const partsCtx = partsCanvas.getContext('2d');
        new Chart(partsCtx, {
            ...commonConfig,
            data: {
                labels: window.chartData.years,
                datasets: [{
                    label: 'Parts',
                    data: window.chartData.parts,
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                ...commonConfig.options,
                scales: {
                    ...commonConfig.options.scales,
                    y: {
                        ...commonConfig.options.scales.y,
                        title: {
                            display: true,
                            text: 'Parts Count',
                            color: textColor
                        }
                    }
                }
            }
        });
    }

    // Minifigures Chart
    const minifigsCanvas = document.getElementById('minifigsChart');
    if (minifigsCanvas) {
        const minifigsCtx = minifigsCanvas.getContext('2d');
        new Chart(minifigsCtx, {
            ...commonConfig,
            data: {
                labels: window.chartData.years,
                datasets: [{
                    label: 'Minifigures',
                    data: window.chartData.minifigs,
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                ...commonConfig.options,
                scales: {
                    ...commonConfig.options.scales,
                    y: {
                        ...commonConfig.options.scales.y,
                        title: {
                            display: true,
                            text: 'Minifigures Count',
                            color: textColor
                        }
                    }
                }
            }
        });
    }
});