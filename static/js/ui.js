/**
 * Zona B&R - Manejo de la Interfaz de Usuario Principal
 */
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('comprobante');
    const labelTexto = document.getElementById('texto-comprobante');

    // Cambiar dinámicamente el texto del botón al cargar el comprobante
    if (fileInput && labelTexto) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                labelTexto.innerText = "✅ Archivo: " + this.files[0].name;
                labelTexto.style.color = "#46d39a";
            } else {
                labelTexto.innerText = "Subir imagen del pago (Obligatorio)";
                labelTexto.style.color = "";
            }
        });
    }
});