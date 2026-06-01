/**
 * ==========================================================================
 * GESTIÓN DE SELECCIÓN DIRECTA CON LÍMITE MÁXIMO DE 99.999 - ZONA B&R
 * ==========================================================================
 */
document.addEventListener('DOMContentLoaded', () => {
    const PRECIO_POR_TICKET = 700; // $700 COP por boleta
    const MAX_ABSOLUTO = 99999;     // Tope máximo solicitado

    // Captura de elementos del DOM
    const tarjetasPaquetes = document.querySelectorAll('.package-card');
    const inputCantidad = document.getElementById('ticketQuantity');
    const botonesFiltro = document.querySelectorAll('.qty-btn');
    
    const badgeCount = document.querySelector('.count-badge');
    const ticketTagText = document.querySelector('.ticket-tag');
    const priceValueText = document.querySelector('.price-value');

    // Identificar botones manuales (+ / −)
    let btnMenos = null;
    let btnMas = null;
    botonesFiltro.forEach(btn => {
        if (btn.textContent.trim() === '−') btnMenos = btn;
        if (btn.textContent.trim() === '+') btnMas = btn;
    });

    /**
     * Sincroniza la interfaz y calcula los precios en base a la cantidad ingresada
     */
    function actualizarInterfaz(cantidadTotal) {
        // Candado de seguridad: Si por algún motivo supera el máximo, lo frena en 99999
        let cantidadFinal = cantidadTotal;
        if (cantidadFinal > MAX_ABSOLUTO) {
            cantidadFinal = MAX_ABSOLUTO;
        }

        const totalDinero = cantidadFinal * PRECIO_POR_TICKET;
        const totalFormateado = `$${totalDinero.toLocaleString('es-CO')}`;

        // Sincronizar inputs y etiquetas
        if (inputCantidad) inputCantidad.value = cantidadFinal;
        if (badgeCount) badgeCount.textContent = cantidadFinal;
        if (ticketTagText) ticketTagText.textContent = `${cantidadFinal} NÚMEROS ALEATORIOS`;

        // Animación suave del precio
        if (priceValueText) {
            priceValueText.classList.remove('visible');
            setTimeout(() => {
                priceValueText.textContent = totalFormateado;
                priceValueText.classList.add('visible');
            }, 50);
        }
    }

    // EVENTO: Clic en los paquetes predefinidos
    tarjetasPaquetes.forEach(tarjeta => {
        tarjeta.classList.remove('popular'); 
        tarjeta.addEventListener('click', function() {
            tarjetasPaquetes.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const qtyText = this.querySelector('.package-qty')?.textContent.trim();
            const valorPaquete = parseInt(qtyText) || 20;

            actualizarInterfaz(valorPaquete);
        });
    });

    // EVENTO: Botón Más (+) con límite de tope
    if (btnMas && inputCantidad) {
        btnMas.addEventListener('click', () => {
            let actual = parseInt(inputCantidad.value) || 20;
            
            if (actual < MAX_ABSOLUTO) {
                tarjetasPaquetes.forEach(t => t.classList.remove('active'));
                actualizarInterfaz(actual + 1);
            } else {
                alert(`⚠️ Límite excedido: No puedes comprar más de ${MAX_ABSOLUTO.toLocaleString('es-CO')} tickets.`);
            }
        });
    }

    // EVENTO: Botón Menos (−)
    if (btnMenos && inputCantidad) {
        btnMenos.addEventListener('click', () => {
            let actual = parseInt(inputCantidad.value) || 20;
            
            if (actual > 20) {
                tarjetasPaquetes.forEach(t => t.classList.remove('active'));
                actualizarInterfaz(actual - 1);
            } else {
                alert("⚠️ Operación no permitida: La cantidad mínima de compra es de 20 tickets.");
            }
        });
    }

    // EVENTO: Escritura manual libre con control de máximos
    if (inputCantidad) {
        inputCantidad.removeAttribute('readonly'); // Dejar escribir

        // Control dinámico mientras digita
        inputCantidad.addEventListener('input', function() {
            tarjetasPaquetes.forEach(t => t.classList.remove('active'));
            let valorIngresado = parseInt(this.value);
            
            if (!isNaN(valorIngresado)) {
                // Si el usuario se pasa escribiendo, recortamos el exceso en tiempo real
                if (valorIngresado > MAX_ABSOLUTO) {
                    this.value = MAX_ABSOLUTO;
                    valorIngresado = MAX_ABSOLUTO;
                }
                actualizarInterfaz(valorIngresado);
            }
        });

        // Control rígido con alerta al quitar el cursor del cuadro
        inputCantidad.addEventListener('blur', function() {
            let valorFinal = parseInt(this.value) || 20;
            
            if (valorFinal < 20) {
                alert("⚠️ Ajuste automático: La cantidad mínima permitida es de 20 tickets.");
                valorFinal = 20;
            }
            if (valorFinal > MAX_ABSOLUTO) {
                alert(`⚠️ Límite excedido: El máximo permitido son ${MAX_ABSOLUTO.toLocaleString('es-CO')} tickets.`);
                valorFinal = MAX_ABSOLUTO;
            }
            
            actualizarInterfaz(valorFinal);
        });
    }

    // Inicializar estado del precio al cargar
    if (priceValueText) {
        priceValueText.classList.add('visible');
    }
});

/**
 * Zona B&R - Sincronización del formulario de tickets
 * Sigue las buenas prácticas manteniendo la lógica fuera del HTML.
 */
document.addEventListener("DOMContentLoaded", function() {
    const inputVisual = document.getElementById('ticketQuantity');
    const inputOculto = document.getElementById('hiddenTicketQuantity');
    const form = document.getElementById('purchaseForm');

    if (form && inputVisual && inputOculto) {
        
        // 1. Sincroniza el valor justo en el momento en que el usuario da clic a "Confirmar Compra"
        form.addEventListener('submit', function() {
            inputOculto.value = inputVisual.value;
        });

        // 2. Escucha clics en los botones de paquetes preestablecidos (20, 50, 100, etc.)
        document.querySelectorAll('.package-card').forEach(card => {
            card.addEventListener('click', function() {
                // Un pequeño retraso de 50ms permite que el script principal de la tarjeta 
                // actualice el inputVisual antes de copiar el dato al inputOculto
                setTimeout(() => {
                    inputOculto.value = inputVisual.value;
                }, 50);
            });
        });

        // 3. Extensión de seguridad: Observa cambios en los atributos del input por si usas JS para alterarlo
        const observer = new MutationObserver(function() {
            inputOculto.value = inputVisual.value;
        });
        observer.observe(inputVisual, { attributes: true, attributeFilter: ['value'] });
    }
});