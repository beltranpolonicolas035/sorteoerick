/**
 * ==========================================================================
 * MOTOR DE BÚSQUEDA INTELIGENTE CON VALIDACIÓN DE NÚMEROS - ZONA B&R
 * ==========================================================================
 */
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('adminSearchInput');
    
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filtro = this.value.toLowerCase().trim();
            const filas = document.querySelectorAll('.admin-table-scroll tbody tr');

            // Evaluamos si el usuario está digitando puramente números
            const esNumero = /^\d+$/.test(filtro);

            filas.forEach(fila => {
                if (!fila.classList.contains('admin-empty')) {
                    
                    // 1. Extraemos las celdas específicas de la fila actual
                    const celdaNombre = fila.querySelector('.td-name')?.textContent.toLowerCase() || '';
                    const celdaCedula = fila.querySelector('.td-mono:nth-of-type(1)')?.textContent.trim() || '';
                    const celdaWhatsapp = fila.querySelector('.td-mono:nth-of-type(2)')?.textContent.trim() || '';
                    const celdaTickets = fila.querySelector('.td-tickets')?.textContent.toLowerCase() || '';

                    let coincide = false;

                    if (esNumero) {
                        // SI ES NÚMERO: Evaluamos coincidencia exacta o término de inicio para la Cédula o el Ticket
                        // Esto evita que "432" te traiga correos o números cruzados de WhatsApp
                        const coincideCedula = celdaCedula === filtro || celdaCedula.startsWith(filtro);
                        const coincideTicket = celdaTickets.includes(filtro); // Por si tiene varios tickets separados por coma
                        
                        coincide = coincideCedula || coincideTicket;
                    } else {
                        // SI ES TEXTO: Buscamos de manera normal por el nombre del participante
                        coincide = celdaNombre.includes(filtro);
                    }

                    // Aplicamos el filtro visual en la tabla
                    if (coincide || filtro === '') {
                        fila.style.display = '';
                    } else {
                        fila.style.display = 'none';
                    }
                }
            });
        });
    }
});

/**
 * Zona B&R - Controlador del Panel de Administración
 * Gestión del modal de visualización de comprobantes mediante escucha de eventos.
 */
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('imgModal');
    const modalImg = document.getElementById('imgModalSrc');
    const closeBtn = document.getElementById('closeModalBtn');

    if (modal && modalImg) {
        
        // 1. Escuchar los clics en cualquier miniatura o botón de zoom
        document.querySelectorAll('.js-open-modal').forEach(element => {
            element.addEventListener('click', function() {
                const targetSrc = this.getAttribute('data-src');
                if (targetSrc) {
                    modalImg.src = targetSrc;
                    modal.style.display = 'flex';
                    modal.classList.add('open');
                }
            });
        });

        // 2. Función unificada para cerrar el modal
        const cerrarModal = () => {
            modal.style.display = 'none';
            modal.classList.remove('open');
            modalImg.src = ''; // Limpiamos la ruta por seguridad
        };

        // 3. Evento para el botón de cerrar (X)
        if (closeBtn) {
            closeBtn.addEventListener('click', cerrarModal);
        }

        // 4. Evento para cerrar si hacen clic fuera de la tarjeta contenedora
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                cerrarModal();
            }
        });

        // 5. Evento de accesibilidad: Cerrar con la tecla Escape
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && modal.classList.contains('open')) {
                cerrarModal();
            }
        });
    }
});

/**
 * Zona B&R - Control de Validación en el Panel de Administración
 */

// SOLUCIÓN AL ERROR DE CONSOLA: Abre el comprobante en tamaño completo
function openImgModal(element) {
    if (element && element.src) {
        // Abre la imagen de la transferencia en una nueva pestaña de Chrome de forma limpia
        window.open(element.src, '_blank');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("Panel de administración de Zona B&R cargado correctamente.");
    
    // Aquí puedes añadir lógica futura para filtros de búsqueda o confirmaciones por AJAX si lo necesitas
});