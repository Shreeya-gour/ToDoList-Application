/**
 * TaskFlow - Interactive UI Controller
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss flash alert messages after 5 seconds
    const alerts = document.querySelectorAll('.taskflow-alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.transition = 'opacity 0.4s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 400);
            }
        }, 5000);
    });

    // 2. View Toggle: Grid Cards View vs Table View vs Calendar View
    const gridBtn = document.getElementById('viewGridBtn');
    const tableBtn = document.getElementById('viewTableBtn');
    const calendarBtn = document.getElementById('viewCalendarBtn');
    const gridView = document.getElementById('tasksGridView');
    const tableView = document.getElementById('tasksTableView');
    const calendarView = document.getElementById('tasksCalendarView');

    let calendarInstance = null;

    function initCalendar() {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl || calendarInstance) return;

        const dataEl = document.getElementById('tasksCalendarData');
        let events = [];
        if (dataEl) {
            try {
                events = JSON.parse(dataEl.textContent);
            } catch (e) {
                console.error('Error parsing calendar tasks:', e);
            }
        }

        if (typeof FullCalendar !== 'undefined') {
            calendarInstance = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,listMonth'
                },
                buttonText: {
                    today: 'Today',
                    dayGridMonth: 'Month',
                    listMonth: 'List'
                },
                events: events,
                eventClick: function (info) {
                    const modalEl = document.getElementById('taskModal' + info.event.id);
                    if (modalEl) {
                        const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
                        bsModal.show();
                    }
                },
                dayMaxEvents: 3,
                height: 'auto'
            });
            calendarInstance.render();
        }
    }

    if (gridBtn && tableBtn && gridView && tableView) {
        // Retrieve stored preference or default to grid
        const savedView = localStorage.getItem('taskflow_view') || 'grid';
        if (savedView === 'table') {
            activateTableView();
        } else if (savedView === 'calendar' && calendarBtn && calendarView) {
            activateCalendarView();
        } else {
            activateGridView();
        }

        gridBtn.addEventListener('click', function () {
            activateGridView();
            localStorage.setItem('taskflow_view', 'grid');
        });

        tableBtn.addEventListener('click', function () {
            activateTableView();
            localStorage.setItem('taskflow_view', 'table');
        });

        if (calendarBtn && calendarView) {
            calendarBtn.addEventListener('click', function () {
                activateCalendarView();
                localStorage.setItem('taskflow_view', 'calendar');
            });
        }

        function activateGridView() {
            gridView.classList.remove('d-none');
            tableView.classList.add('d-none');
            if (calendarView) calendarView.classList.add('d-none');
            gridBtn.classList.add('active');
            tableBtn.classList.remove('active');
            if (calendarBtn) calendarBtn.classList.remove('active');
        }

        function activateTableView() {
            tableView.classList.remove('d-none');
            gridView.classList.add('d-none');
            if (calendarView) calendarView.classList.add('d-none');
            tableBtn.classList.add('active');
            gridBtn.classList.remove('active');
            if (calendarBtn) calendarBtn.classList.remove('active');
        }

        function activateCalendarView() {
            if (!calendarView) return;
            calendarView.classList.remove('d-none');
            gridView.classList.add('d-none');
            tableView.classList.add('d-none');
            if (calendarBtn) calendarBtn.classList.add('active');
            gridBtn.classList.remove('active');
            tableBtn.classList.remove('active');

            initCalendar();
            if (calendarInstance) {
                setTimeout(function () {
                    calendarInstance.updateSize();
                }, 50);
            }
        }
    }
});
