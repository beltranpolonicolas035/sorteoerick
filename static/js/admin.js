/**
 * ==========================================================================
 * ZONA B&R - Panel de Administración
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', function() {

    console.log("Panel de administración de Zona B&R cargado correctamente.");

    // -----------------------------------------------------------------------
    // 1. BUSCADOR DE PARTICIPANTES
    // -----------------------------------------------------------------------
    const searchInput = document.getElementById('adminSearchInput');

    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filtro = this.value.toLowerCase().trim();
            const filas = document.querySelectorAll('.admin-table-scroll tbody tr');
            const esNumero = /^\d+$/.test(filtro);

            filas.forEach(fila => {
                if (!fila.classList.contains('admin-empty')) {
                    const celdaNombre  = fila.querySelector('.td-name')?.textContent.toLowerCase() || '';
                    const celdaCedula  = fila.querySelector('.td-mono')?.textContent.trim() || '';
                    const celdaTickets = fila.querySelector('.td-tickets')?.textContent.toLowerCase() || '';

                    let coincide = false;

                    if (esNumero) {
                        coincide = celdaCedula === filtro || celdaCedula.startsWith(filtro) || celdaTickets.includes(filtro);
                    } else {
                        coincide = celdaNombre.includes(filtro);
                    }

                    fila.style.display = (coincide || filtro === '') ? '' : 'none';
                }
            });
        });
    }

    // -----------------------------------------------------------------------
    // 2. MODAL VISOR DE COMPROBANTES
    // -----------------------------------------------------------------------
    const modal    = document.getElementById('imgModal');
    const modalImg = document.getElementById('imgModalSrc');
    const closeBtn = document.getElementById('closeModalBtn');

    if (!modal || !modalImg) {
        console.warn('Modal no encontrado en el DOM.');
        return;
    }

    const abrirModal = (src) => {
        modalImg.src = src;
        modal.classList.add('open');
    };

    const cerrarModal = () => {
        modal.classList.remove('open');
        modalImg.src = '';
    };

    // Clic en imagen o botón de zoom
    document.querySelectorAll('.js-open-modal').forEach(function(el) {
        el.addEventListener('click', function() {
            const src = this.getAttribute('data-src');
            if (src) abrirModal(src);
        });
    });

    // Botón cerrar (X)
    if (closeBtn) closeBtn.addEventListener('click', cerrarModal);

    // Clic fuera del contenido
    modal.addEventListener('click', function(e) {
        if (e.target === modal) cerrarModal();
    });

    // Tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('open')) cerrarModal();
    });

});