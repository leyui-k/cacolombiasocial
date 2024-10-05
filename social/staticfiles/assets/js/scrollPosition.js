// Verificar si hay una posición guardada en el localStorage
if (localStorage.getItem('scrollPosition')) {
    // Obtener la posición guardada
    const scrollPosition = parseInt(localStorage.getItem('scrollPosition'));

    // Desplazar la página a la posición guardada
    window.scrollTo(0, scrollPosition);

    // Limpiar la posición guardada después de restaurarla
    localStorage.removeItem('scrollPosition');
}

// Función para guardar la posición actual antes de actualizar la página
function saveScrollPosition() {
    const scrollPosition = window.scrollY;
    localStorage.setItem('scrollPosition', scrollPosition);
}

// Agregar un evento antes de actualizar la página para guardar la posición
window.addEventListener('beforeunload', saveScrollPosition);
