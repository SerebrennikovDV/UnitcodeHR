// Корпоративный JS UnitcodeHR

// Подсветка карточек kanban при перетаскивании (упрощённый stub)
document.addEventListener('DOMContentLoaded', function () {
    // Автозакрытие flash-сообщений через 5 секунд
    document.querySelectorAll('.alert').forEach(function (a) {
        setTimeout(function () {
            try { new bootstrap.Alert(a).close(); } catch (e) {}
        }, 5000);
    });
});
