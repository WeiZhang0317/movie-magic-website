// chart for popularity report
document.addEventListener('DOMContentLoaded', function () {
    // Prepare the data for the chart
    const labels = topMoviesData.map(data => data.movie_title);
    const data = {
        labels: labels,
        datasets: [{
            label: 'Total Tickets Sold',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            data: topMoviesData.map(data => data.total_tickets_sold),
        }]
    };

    // Configuration options
    const config = {
        type: 'bar',
        data: data,
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 14,
                            weight: 'bold',
                            color: 'white'
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 14,
                            weight: 'bold',
                            color: 'rgb(255, 255, 255)'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 14,
                            weight: 'bold',
                            color: 'rgb(255, 255, 255)'
                        }
                    }
                }
            }
        }
    };

    // Render the chart
    const topMoviesChart = new Chart(
        document.getElementById('topMoviesCanvas'),
        config
    );
});


document.addEventListener('DOMContentLoaded', function () {
    // Extract months and their corresponding income
    const labels = monthlyIncomeData.map(data => data.Month);
    const incomeData = monthlyIncomeData.map(data => data.MonthlyIncome);

    // Chart data
    const data = {
        labels: labels,
        datasets: [{
            label: 'Monthly Income',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            data: incomeData,
        }]
    };

    // Chart configuration
 // Configuration options
 const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'white'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        }
    }
};

    // Render the chart
    new Chart(document.getElementById('monthlyIncomeCanvas'), config);
});



document.addEventListener('DOMContentLoaded', function () {
    
    const labels = weekofdateIncomeData.map(data => data.DayOfWeek);
    const incomes = weekofdateIncomeData.map(data => data.DailyIncome);

    const data = {
        labels: labels,
        datasets: [{
            label: 'Week of Date Income',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            data: incomes,
        }]
    };

  // Chart configuration
 // Configuration options
 const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'white'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        }
    }
};

    const weekofdateIncomeChart = new Chart(
        document.getElementById('weekofdateIncomeCanvas'),
        config
    );
});


document.addEventListener('DOMContentLoaded', function () {
    
    const labels = categotyIncomeData.map(data => data.GenreName);
    const incomes = categotyIncomeData.map(data => data.GenreIncome);

    const data = {
        labels: labels,
        datasets: [{
            label: 'Income by Category',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            data: incomes,
        }]
    };
    
  // Chart configuration
 // Configuration options
 const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'white'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        }
    }
};

    const categotyIncomeChart= new Chart(
        document.getElementById('categotyIncomeCanvas'),
        config
    );
});



document.addEventListener('DOMContentLoaded', function () {
    
    const labels = paymentMethodsData.map(data => data.payment_method);
    const bookings = paymentMethodsData.map(data => data.bookings_per_paymentMethods);
    const income = paymentMethodsData.map(data => data.income_per_paymentMethods);

    const data = {
        labels: labels,
        datasets: [{
            label: 'Bookings by Payment Methods',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            data: bookings,
        }]
    };
    

 const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'white'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        }
    }
};

    const categotyIncomeChart= new Chart(
        document.getElementById('paymentMethodsCanvas'),
        config
    );
});


document.addEventListener('DOMContentLoaded', function () {
    
    const labels = ticketTypeData.map(data => data.ticket_type);
    const tickets = ticketTypeData.map(data => data.tickets_sold);

    const data = {
        labels: labels,
        datasets: [{
            label: 'Ticket Type Sales',
            backgroundColor: 'rgb(255, 0, 0)',
            borderColor: 'rgb(255, 0, 0)',
            data: tickets,
        }]
    };
    

 const config = {
    type: 'bar',
    data: data,
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'white'
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 14,
                        weight: 'bold',
                        color: 'rgb(255, 255, 255)'
                    }
                }
            }
        }
    }
};

    const categotyIncomeChart= new Chart(
        document.getElementById('ticketTypeCanvas'),
        config
    );
});