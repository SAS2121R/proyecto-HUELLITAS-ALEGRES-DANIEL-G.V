/**
 * SERVICIO WEB DE AUTENTICACIÓN - HUELLITAS ALEGRES
 * =====================================================
 * 
 * Este archivo implementa un servicio web completo para registro e inicio de sesión
 * de usuarios en la plataforma Huellitas Alegres (tienda para mascotas).
 * 
 * FUNCIONALIDADES PRINCIPALES:
 * - Registro de nuevos usuarios con validación completa
 * - Inicio de sesión con autenticación segura
 * - Validación en tiempo real de formularios
 * - Mensajes de éxito/error para feedback del usuario
 * - Efectos visuales modernos y accesibilidad
 * 
 * TECNOLOGÍAS UTILIZADAS:
 * - JavaScript ES6+ (Clases, Arrow Functions, Async/Await)
 * - DOM API para manipulación de elementos
 * - CSS3 para animaciones y efectos visuales
 * - ARIA para accesibilidad web
 * 
 * AUTOR: Sistema de Desarrollo Huellitas Alegres
 * VERSIÓN: 3.0 - Diseño Vibrante y Moderno
 * FECHA: 2024
 */

/**
 * CLASE PRINCIPAL DEL SERVICIO WEB DE AUTENTICACIÓN
 * ================================================
 * 
 * Esta clase maneja todo el sistema de autenticación web incluyendo:
 * - Registro de usuarios nuevos
 * - Inicio de sesión de usuarios existentes
 * - Validación de datos en tiempo real
 * - Manejo de errores y mensajes de éxito
 */
class ModernAuthSystem {
    /**
     * CONSTRUCTOR - Inicializa el servicio web de autenticación
     * ========================================================
     * 
     * Configura las reglas de validación y el estado inicial del sistema
     */
    constructor() {
        // Estado actual del formulario (login o register)
        this.currentForm = 'login';
        
        // REGLAS DE VALIDACIÓN PARA EL SERVICIO WEB
        // ==========================================
        this.validationRules = {
            // Validación de email: formato estándar RFC 5322
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            
            // Validación de contraseña segura:
            // - Mínimo 8 caracteres
            // - Al menos una minúscula
            // - Al menos una mayúscula  
            // - Al menos un número
            password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
            
            // Validación de nombres: solo letras y espacios (2-50 caracteres)
            name: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{2,50}$/,
            
            // Validación de teléfono: formato internacional opcional
            phone: /^[\+]?[1-9]?[0-9]{7,15}$/
        };
        
        // Control de estado para evitar envíos múltiples
        this.isSubmitting = false;
        
        // Inicializar el servicio web
        this.init();
    }

    /**
     * INICIALIZACIÓN DEL SERVICIO WEB
     * ===============================
     * 
     * Configura todos los componentes necesarios para el funcionamiento
     * del servicio web de autenticación
     */
    init() {
        // Configurar eventos de interacción del usuario
        this.setupEventListeners();
        
        // Configurar cambio entre formularios (login/registro)
        this.setupFormSwitching();
        
        // Configurar validación de datos en tiempo real
        this.setupValidation();
        
        // Configurar accesibilidad para usuarios con discapacidades
        this.setupAccessibility();
        
        // Configurar efectos visuales modernos
        this.setupVisualEffects();
        
        // Anunciar que el servicio está listo
        this.announceToScreenReader('🎉 Sistema de autenticación cargado correctamente');
    }

    /**
     * CONFIGURACIÓN DE EVENTOS DEL SERVICIO WEB
     * =========================================
     * 
     * Establece todos los listeners necesarios para la interacción
     * del usuario con el servicio de autenticación
     */
    setupEventListeners() {
        // EVENTOS DE NAVEGACIÓN ENTRE FORMULARIOS
        // =======================================
        // Permite cambiar entre login y registro
        document.querySelectorAll('.switcher button').forEach(button => {
            // Click para cambiar formulario
            button.addEventListener('click', (e) => this.switchForm(e));
            // Navegación con teclado (accesibilidad)
            button.addEventListener('keydown', (e) => this.handleKeyNavigation(e));
        });

        // EVENTOS DE VALIDACIÓN EN TIEMPO REAL
        // ====================================
        // Valida los datos mientras el usuario escribe
        document.querySelectorAll('input').forEach(input => {
            // Validar mientras escribe (input event)
            input.addEventListener('input', (e) => this.validateField(e.target));
            // Validar al salir del campo (blur event)
            input.addEventListener('blur', (e) => this.validateField(e.target));
            // Efectos visuales al enfocar campo
            input.addEventListener('focus', (e) => this.handleFieldFocus(e.target));
        });

        // EVENTOS DE ENVÍO DE FORMULARIOS
        // ===============================
        // Maneja el envío de datos al servidor
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        });

        // EVENTOS DE MENSAJES DE SISTEMA
        // ==============================
        // Permite cerrar mensajes de error/éxito
        document.querySelectorAll('.error-message, .success-message').forEach(msg => {
            msg.addEventListener('click', (e) => this.dismissMessage(e.target));
        });

        // EFECTOS VISUALES INTERACTIVOS
        // =============================
        this.setupHoverEffects();
    }

    setupFormSwitching() {
        const switcher = document.querySelector('.switcher');
        if (!switcher) return;

        // Crear indicador visual del switcher
        if (!switcher.querySelector('.switcher-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'switcher-indicator';
            switcher.appendChild(indicator);
        }
    }

    switchForm(event) {
        const button = event.target;
        const formType = button.dataset.form;
        
        if (formType === this.currentForm) return;

        // Actualizar estado de botones
        document.querySelectorAll('.switcher button').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });
        
        button.classList.add('active');
        button.setAttribute('aria-selected', 'true');

        // Animar transición de formularios
        this.animateFormTransition(this.currentForm, formType);
        
        this.currentForm = formType;
        
        // Anunciar cambio para accesibilidad
        const formName = formType === 'login' ? 'Iniciar Sesión' : 'Registro';
        this.announceToScreenReader(`✨ Cambiado a formulario de ${formName}`);
        
        // Enfocar primer campo del nuevo formulario
        setTimeout(() => {
            const newForm = document.getElementById(`${formType}-form`);
            const firstInput = newForm?.querySelector('input');
            if (firstInput) {
                firstInput.focus();
                this.addVisualFocus(firstInput);
            }
        }, 300);
    }

    animateFormTransition(fromForm, toForm) {
        const fromElement = document.getElementById(`${fromForm}-form`);
        const toElement = document.getElementById(`${toForm}-form`);
        
        if (!fromElement || !toElement) return;

        // Animación de salida
        fromElement.style.transform = 'translateX(-30px)';
        fromElement.style.opacity = '0';
        fromElement.style.pointerEvents = 'none';
        
        setTimeout(() => {
            fromElement.classList.remove('active');
            toElement.classList.add('active');
            
            // Animación de entrada
            toElement.style.transform = 'translateX(30px)';
            toElement.style.opacity = '0';
            toElement.style.pointerEvents = 'all';
            
            requestAnimationFrame(() => {
                toElement.style.transform = 'translateX(0)';
                toElement.style.opacity = '1';
            });
        }, 150);
    }

    setupValidation() {
        // Configurar validación de confirmación de contraseña
        const passwordConfirm = document.getElementById('register-password-confirm');
        if (passwordConfirm) {
            passwordConfirm.addEventListener('input', () => {
                this.validatePasswordMatch();
            });
        }
    }

    /**
     * VALIDACIÓN DE CAMPOS DEL SERVICIO WEB
     * =====================================
     * 
     * Valida los datos ingresados por el usuario en tiempo real
     * según las reglas de negocio del servicio de autenticación
     * 
     * @param {HTMLElement} field - Campo de formulario a validar
     * @returns {boolean} - true si el campo es válido, false si no
     */
    validateField(field) {
        // Si el campo no tiene reglas de validación, es válido por defecto
        if (!field.dataset.validation) return true;
        
        // Obtener tipo de validación y valor del campo
        const validationType = field.dataset.validation;
        const value = field.value.trim();
        const errorElement = field.parentElement.querySelector('.error-text');
        
        // Variables para el resultado de la validación
        let isValid = true;
        let errorMessage = '';

        // APLICAR REGLAS DE VALIDACIÓN SEGÚN EL TIPO DE CAMPO
        // ===================================================
        switch (validationType) {
            case 'email':
                // Validar formato de correo electrónico
                isValid = this.validationRules.email.test(value);
                errorMessage = isValid ? '' : '📧 Formato de email inválido';
                break;
                
            case 'password':
                // Validar contraseña segura (requisitos de seguridad)
                isValid = this.validationRules.password.test(value);
                errorMessage = isValid ? '' : '🔐 Contraseña debe tener 8+ caracteres, mayúsculas y números';
                break;
                
            case 'name':
                // Validar nombres (solo letras y espacios)
                isValid = this.validationRules.name.test(value);
                errorMessage = isValid ? '' : '👤 Solo letras y espacios (2-50 caracteres)';
                break;
                
            case 'phone':
                // Validar teléfono (campo opcional)
                if (value) { // Solo validar si hay valor
                    isValid = this.validationRules.phone.test(value);
                    errorMessage = isValid ? '' : '📱 Formato de teléfono inválido';
                }
                break;
                
            case 'password-confirm':
                // Validar confirmación de contraseña
                return this.validatePasswordMatch();
        }

        // APLICAR RESULTADO DE VALIDACIÓN AL CAMPO
        // ========================================
        this.updateFieldValidation(field, isValid, errorMessage, errorElement);
        
        return isValid;
    }

    validatePasswordMatch() {
        const password = document.getElementById('register-password');
        const passwordConfirm = document.getElementById('register-password-confirm');
        const errorElement = passwordConfirm?.parentElement.querySelector('.error-text');
        
        if (!password || !passwordConfirm) return true;
        
        const isValid = password.value === passwordConfirm.value && passwordConfirm.value.length > 0;
        const errorMessage = isValid ? '' : '🔒 Las contraseñas no coinciden';
        
        this.updateFieldValidation(passwordConfirm, isValid, errorMessage, errorElement);
        
        return isValid;
    }

    updateFieldValidation(field, isValid, errorMessage, errorElement) {
        // Remover clases anteriores
        field.classList.remove('error', 'valid');
        
        if (field.value.trim()) {
            if (isValid) {
                field.classList.add('valid');
                this.addSuccessEffect(field);
            } else {
                field.classList.add('error');
                this.addErrorEffect(field);
            }
        }
        
        // Mostrar/ocultar mensaje de error
        if (errorElement) {
            if (errorMessage) {
                errorElement.textContent = errorMessage;
                errorElement.style.display = 'block';
                errorElement.setAttribute('aria-live', 'polite');
            } else {
                errorElement.style.display = 'none';
            }
        }
    }

    addSuccessEffect(field) {
        // Efecto visual de éxito
        field.style.boxShadow = '0 0 0 4px rgba(56, 161, 105, 0.2), 0 8px 25px rgba(0, 0, 0, 0.15)';
        
        setTimeout(() => {
            if (field.classList.contains('valid')) {
                field.style.boxShadow = '';
            }
        }, 2000);
    }

    addErrorEffect(field) {
        // Efecto visual de error con vibración
        field.style.boxShadow = '0 0 0 4px rgba(229, 62, 62, 0.2), 0 8px 25px rgba(229, 62, 62, 0.3)';
        
        // Vibración suave
        if (navigator.vibrate) {
            navigator.vibrate([100, 50, 100]);
        }
        
        setTimeout(() => {
            if (field.classList.contains('error')) {
                field.style.boxShadow = '';
            }
        }, 3000);
    }

    handleFieldFocus(field) {
        // Efecto de enfoque mejorado
        this.addVisualFocus(field);
        
        // Anunciar ayuda contextual
        const helpText = field.parentElement.querySelector('.help-text');
        if (helpText) {
            this.announceToScreenReader(helpText.textContent);
        }
    }

    addVisualFocus(field) {
        // Efecto de glow en el campo enfocado
        field.style.transform = 'translateY(-2px)';
        field.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        field.addEventListener('blur', () => {
            field.style.transform = '';
        }, { once: true });
    }

    /**
     * MANEJO DE ENVÍO DE FORMULARIOS DEL SERVICIO WEB
     * ===============================================
     * 
     * Procesa el envío de datos de registro o login al servidor.
     * Solo previene el envío si la validación del lado cliente falla.
     * Si la validación pasa, el formulario se envía normalmente preservando
     * el token CSRF de Django.
     * 
     * @param {Event} event - Evento de envío del formulario
     */
    handleSubmit(event) {
        // Evitar envíos múltiples simultáneos
        if (this.isSubmitting) {
            event.preventDefault();
            return;
        }
        
        // OBTENER ELEMENTOS DEL FORMULARIO
        // ================================
        const form = event.target;
        const formType = form.closest('.form-slide') ? form.closest('.form-slide').id.replace('-form', '') : 'login';
        const submitButton = form.querySelector('.btn-primary');
        
        // VALIDACIÓN COMPLETA DEL FORMULARIO
        // ==================================
        const inputs = form.querySelectorAll('input[required]');
        let isFormValid = true;
        
        // Validar cada campo requerido
        inputs.forEach(input => {
            if (!this.validateField(input) || !input.value.trim()) {
                isFormValid = false;
            }
        });
        
        // MANEJO DE ERRORES DE VALIDACIÓN
        // ===============================
        if (!isFormValid) {
            // Prevenir envío SÓLO cuando la validación falla
            event.preventDefault();
            // Mostrar mensaje de error al usuario
            this.showFormError('⚠️ Por favor, completa todos los campos correctamente');
            // Enfocar el primer campo con error
            this.focusFirstError(form);
            return;
        }
        
        // VALIDACIÓN CORRECTA — Mostrar animación de carga en el botón
        // y dejar que el formulario se envíe normalmente con el token CSRF intacto.
        // No llamamos event.preventDefault() ni form.submit() programático,
        // ya que eso rompe la verificación CSRF de Django.
        if (submitButton) {
            submitButton.classList.add('loading');
            submitButton.disabled = true;
        }
        this.isSubmitting = true;
        
        // Anunciar acción para accesibilidad
        const actionText = formType === 'login' ? 'Verificando credenciales' : 'Creando cuenta';
        this.announceToScreenReader(`⏳ ${actionText}...`);
    }

    startSubmitAnimation(button, formType) {
        // Animación de envío — ya no se usa como flujo principal
        // porque el formulario se envía normalmente (preserva CSRF).
        // Se mantiene solo como referencia para efectos visuales opcionales.
        button.classList.add('loading');
        button.disabled = true;
        this.createRippleEffect(button);
    }

    createRippleEffect(button) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.appendChild(ripple);
        
        // Añadir animación CSS si no existe
        if (!document.querySelector('#ripple-animation')) {
            const style = document.createElement('style');
            style.id = 'ripple-animation';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => ripple.remove(), 600);
    }

/**
     * COMPLETAR ENVÍO AL SERVICIO WEB
     * ==============================
     * 
     * Este método ya no envía el formulario programáticamente.
     * El formulario se envía de forma nativa, preservando el token CSRF.
     * Se mantiene como método de referencia para futuras integraciones AJAX.
     */
    completeSubmit(form, formType) {
        // No-op: el formulario ya se envió de forma nativa con el token CSRF intacto.
        // Este método se conserva para compatibilidad hacia atrás y futuras extensiones.
    }

    showFormError(message) {
        this.showMessage(message, 'error');
    }

    showFormSuccess(message) {
        this.showMessage(message, 'success');
    }

    showMessage(message, type) {
        // Remover mensajes existentes
        document.querySelectorAll('.error-message, .success-message').forEach(msg => {
            msg.remove();
        });
        
        const messageArea = document.getElementById('message-area');
        if (!messageArea) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `${type}-message`;
        messageElement.setAttribute('role', 'alert');
        messageElement.setAttribute('tabindex', '0');
        messageElement.innerHTML = message;
        
        // Añadir evento de cierre
        messageElement.addEventListener('click', () => this.dismissMessage(messageElement));
        
        messageArea.appendChild(messageElement);
        
        // Enfocar el mensaje para accesibilidad
        setTimeout(() => {
            messageElement.focus();
            this.announceToScreenReader(message);
        }, 100);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (messageElement.parentElement) {
                this.dismissMessage(messageElement);
            }
        }, 5000);
    }

    dismissMessage(messageElement) {
        messageElement.style.transform = 'translateY(-20px)';
        messageElement.style.opacity = '0';
        
        setTimeout(() => {
            if (messageElement.parentElement) {
                messageElement.remove();
            }
        }, 300);
    }

    focusFirstError(form) {
        const firstError = form.querySelector('input.error');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    setupAccessibility() {
        // Navegación por teclado mejorada
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
            if (e.key === 'Escape') {
                this.handleEscapeKey(e);
            }
        });
        
        // Anuncios para lectores de pantalla
        this.setupScreenReaderAnnouncements();
    }

    handleKeyNavigation(event) {
        const buttons = Array.from(document.querySelectorAll('.switcher button'));
        const currentIndex = buttons.indexOf(event.target);
        
        let newIndex = currentIndex;
        
        switch (event.key) {
            case 'ArrowLeft':
            case 'ArrowUp':
                newIndex = currentIndex > 0 ? currentIndex - 1 : buttons.length - 1;
                break;
            case 'ArrowRight':
            case 'ArrowDown':
                newIndex = currentIndex < buttons.length - 1 ? currentIndex + 1 : 0;
                break;
            case 'Home':
                newIndex = 0;
                break;
            case 'End':
                newIndex = buttons.length - 1;
                break;
            default:
                return;
        }
        
        event.preventDefault();
        buttons[newIndex].focus();
        buttons[newIndex].click();
    }

    handleTabNavigation(event) {
        // Mejorar la navegación por teclado
        const focusableElements = document.querySelectorAll(
            'button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const currentForm = document.querySelector('.form-slide.active');
        if (currentForm) {
            const formElements = Array.from(currentForm.querySelectorAll(
                'button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
            ));
            
            // Lógica adicional de navegación si es necesaria
        }
    }

    handleEscapeKey(event) {
        // Cerrar mensajes con Escape
        const messages = document.querySelectorAll('.error-message, .success-message');
        if (messages.length > 0) {
            messages.forEach(msg => this.dismissMessage(msg));
            event.preventDefault();
        }
    }

    setupScreenReaderAnnouncements() {
        // Configurar área de anuncios para lectores de pantalla
        if (!document.getElementById('screen-reader-announcements')) {
            const announcer = document.createElement('div');
            announcer.id = 'screen-reader-announcements';
            announcer.className = 'sr-only';
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            document.body.appendChild(announcer);
        }
    }

    announceToScreenReader(message) {
        const announcer = document.getElementById('screen-reader-announcements');
        if (announcer) {
            announcer.textContent = message;
            
            // Limpiar después de un tiempo
            setTimeout(() => {
                announcer.textContent = '';
            }, 1000);
        }
    }

    setupVisualEffects() {
        // Efectos de partículas en el fondo
        this.createBackgroundParticles();
        
        // Efectos de hover mejorados
        this.setupHoverEffects();
        
        // Animaciones de entrada
        this.animateOnLoad();
    }

    createBackgroundParticles() {
        // Crear partículas flotantes decorativas
        const particleCount = 15;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.style.cssText = `
                position: fixed;
                width: ${Math.random() * 6 + 2}px;
                height: ${Math.random() * 6 + 2}px;
                background: rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                pointer-events: none;
                z-index: -1;
                animation: float-particle ${Math.random() * 10 + 10}s infinite linear;
            `;
            
            document.body.appendChild(particle);
        }
        
        // Añadir animación CSS para partículas
        if (!document.querySelector('#particle-animation')) {
            const style = document.createElement('style');
            style.id = 'particle-animation';
            style.textContent = `
                @keyframes float-particle {
                    0% {
                        transform: translateY(100vh) rotate(0deg);
                        opacity: 0;
                    }
                    10% {
                        opacity: 1;
                    }
                    90% {
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(-100vh) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    setupHoverEffects() {
        // Efectos de hover para elementos interactivos
        document.querySelectorAll('.form-group').forEach(group => {
            group.addEventListener('mouseenter', () => {
                if (window.matchMedia('(hover: hover)').matches) {
                    group.style.transform = 'translateY(-2px)';
                    group.style.transition = 'transform 0.3s ease';
                }
            });
            
            group.addEventListener('mouseleave', () => {
                group.style.transform = '';
            });
        });
    }

    animateOnLoad() {
        // Animaciones de entrada escalonadas
        const elements = document.querySelectorAll('.form-group, .switcher, .auth-header');
        
        elements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 100 + 200);
        });
    }

    // Método para limpiar recursos
    destroy() {
        // Remover partículas
        document.querySelectorAll('.floating-particle').forEach(particle => {
            particle.remove();
        });
        
        // Remover estilos dinámicos
        document.querySelectorAll('#ripple-animation, #particle-animation').forEach(style => {
            style.remove();
        });
        
        this.announceToScreenReader('🔄 Sistema de autenticación desactivado');
    }
}

// Inicializar el sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.authSystem = new ModernAuthSystem();
    
    // Manejar visibilidad de la página
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Pausar animaciones cuando la página no es visible
            document.querySelectorAll('.floating-particle').forEach(particle => {
                particle.style.animationPlayState = 'paused';
            });
        } else {
            // Reanudar animaciones
            document.querySelectorAll('.floating-particle').forEach(particle => {
                particle.style.animationPlayState = 'running';
            });
        }
    });
});

// Limpiar recursos al salir
window.addEventListener('beforeunload', () => {
    if (window.authSystem) {
        window.authSystem.destroy();
    }
});

// Exportar para uso en otros módulos si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernAuthSystem;
}