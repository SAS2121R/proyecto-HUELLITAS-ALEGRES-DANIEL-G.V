PRIMERO LANDING PAGE DEL SOFTWARE HUELLITAS ALEGRES
<!DOCTYPE html><html lang="es" style=""><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>Huellitas Alegres - Cuidado Veterinario</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com" rel="preconnect">
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&amp;family=Plus+Jakarta+Sans:wght@600;700&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: {
            extend: {
              "colors": {
                      "surface-container-low": "#f3f4f5",
                      "secondary": "#625e56",
                      "surface": "#f8f9fa",
                      "tertiary-fixed": "#d9eaa3",
                      "on-tertiary": "#ffffff",
                      "secondary-container": "#e6dfd5",
                      "on-background": "#191c1d",
                      "on-primary-container": "#ccf0cc",
                      "on-secondary": "#ffffff",
                      "outline-variant": "#c2c8bf",
                      "surface-container-lowest": "#ffffff",
                      "error-container": "#ffdad6",
                      "surface-container-high": "#e7e8e9",
                      "secondary-fixed-dim": "#cdc5bc",
                      "secondary-fixed": "#e9e1d8",
                      "surface-bright": "#f8f9fa",
                      "on-primary-fixed-variant": "#2f4e33",
                      "tertiary": "#47541d",
                      "tertiary-container": "#5e6d33",
                      "primary-fixed": "#c8ecc8",
                      "primary-fixed-dim": "#acd0ad",
                      "on-tertiary-fixed-variant": "#3e4c16",
                      "outline": "#737971",
                      "on-secondary-container": "#67625a",
                      "on-surface-variant": "#424841",
                      "surface-container-highest": "#e1e3e4",
                      "surface-variant": "#e1e3e4",
                      "on-surface": "#191c1d",
                      "on-primary-fixed": "#03210b",
                      "background": "#f8f9fa",
                      "surface-container": "#edeeef",
                      "on-primary": "#ffffff",
                      "inverse-surface": "#2e3132",
                      "on-secondary-fixed": "#1e1b15",
                      "on-tertiary-fixed": "#161f00",
                      "inverse-primary": "#acd0ad",
                      "surface-tint": "#466649",
                      "error": "#ba1a1a",
                      "tertiary-fixed-dim": "#bdce89",
                      "surface-dim": "#d9dadb",
                      "primary-container": "#4f6f52",
                      "on-error": "#ffffff",
                      "on-secondary-fixed-variant": "#4a463f",
                      "primary": "#37563b",
                      "on-error-container": "#93000a",
                      "inverse-on-surface": "#f0f1f2",
                      "on-tertiary-container": "#ddeea7"
              },
              "borderRadius": {
                      "DEFAULT": "0.25rem",
                      "lg": "0.5rem",
                      "xl": "0.75rem",
                      "full": "9999px"
              },
              "spacing": {
                      "base": "8px",
                      "xl": "80px",
                      "margin-desktop": "40px",
                      "md": "24px",
                      "lg": "48px",
                      "margin-mobile": "16px",
                      "gutter": "24px",
                      "xs": "4px",
                      "sm": "12px"
              },
              "fontFamily": {
                      "label-md": [
                              "Manrope"
                      ],
                      "headline-lg-mobile": [
                              "Plus Jakarta Sans"
                      ],
                      "headline-md": [
                              "Plus Jakarta Sans"
                      ],
                      "caption": [
                              "Manrope"
                      ],
                      "headline-lg": [
                              "Plus Jakarta Sans"
                      ],
                      "body-lg": [
                              "Manrope"
                      ],
                      "body-md": [
                              "Manrope"
                      ],
                      "display-lg": [
                              "Plus Jakarta Sans"
                      ]
              },
              "fontSize": {
                      "label-md": [
                              "14px",
                              {
                                      "lineHeight": "1.2",
                                      "letterSpacing": "0.01em",
                                      "fontWeight": "600"
                              }
                      ],
                      "headline-lg-mobile": [
                              "28px",
                              {
                                      "lineHeight": "1.3",
                                      "fontWeight": "600"
                              }
                      ],
                      "headline-md": [
                              "24px",
                              {
                                      "lineHeight": "1.4",
                                      "fontWeight": "600"
                              }
                      ],
                      "caption": [
                              "12px",
                              {
                                      "lineHeight": "1.2",
                                      "fontWeight": "500"
                              }
                      ],
                      "headline-lg": [
                              "32px",
                              {
                                      "lineHeight": "1.3",
                                      "fontWeight": "600"
                              }
                      ],
                      "body-lg": [
                              "18px",
                              {
                                      "lineHeight": "1.6",
                                      "fontWeight": "400"
                              }
                      ],
                      "body-md": [
                              "16px",
                              {
                                      "lineHeight": "1.6",
                                      "fontWeight": "400"
                              }
                      ],
                      "display-lg": [
                              "48px",
                              {
                                      "lineHeight": "1.2",
                                      "letterSpacing": "-0.02em",
                                      "fontWeight": "700"
                              }
                      ]
              }
            }
          }
        }
    </script>
<style>
        .custom-shadow-level-1 {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        }
    </style>
<style data-stitch-cursor=""></style><style data-stitch-scroll-lock=""></style></head>
<body class="bg-background text-on-background antialiased selection:bg-primary-container selection:text-on-primary-container">
<!-- TopNavBar -->
<nav class="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-desktop py-4 max-w-[1440px] mx-auto bg-surface/95 backdrop-blur-md border-b border-outline-variant/30 shadow-sm">
<div class="flex items-center gap-lg">
<a class="font-display-lg text-headline-md text-primary tracking-tight" href="#">Huellitas Alegres</a>
<div class="hidden md:flex gap-md items-center">
<a class="font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#servicios">Servicios</a>
<a class="font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#precios">Precios</a>
<a class="font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#testimonios">Testimonios</a>
<a class="font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#nosotros">Nosotros</a>
</div>
</div>
<div class="flex items-center gap-sm">
<button class="hidden md:block font-label-md text-label-md text-primary bg-transparent border border-outline-variant hover:border-primary hover:opacity-80 transition-all rounded-lg px-md py-sm">Acceso Staff</button>
<button class="font-label-md text-label-md text-on-primary bg-primary hover:opacity-80 transition-all rounded-lg px-md py-sm">Registrar Mascota</button>
</div>
</nav>
<main class="w-full max-w-[1440px] mx-auto px-margin-mobile md:px-margin-desktop pt-[120px]">
<!-- Hero Section -->
<section class="flex flex-col md:flex-row items-center gap-xl mb-xl">
<div class="flex-1 flex flex-col items-start gap-md">
<div class="inline-flex items-center gap-xs px-sm py-xs bg-surface-container rounded-full text-secondary font-label-md text-label-md">
<span class="material-symbols-outlined text-[16px]" data-icon="auto_awesome">auto_awesome</span>
                    Precisión y Ternura
                </div>
<h1 class="font-display-lg text-display-lg text-on-surface text-balance">
                    Cuidado veterinario excepcional para quienes más amas.
                </h1>
<p class="font-body-lg text-body-lg text-on-surface-variant max-w-[500px]">
                    En Huellitas Alegres combinamos tecnología médica de vanguardia con un trato cálido y empático. Porque su bienestar es nuestra prioridad absoluta.
                </p>
<div class="flex flex-wrap items-center gap-sm mt-sm">
<button class="font-label-md text-label-md text-on-primary bg-primary hover:bg-surface-tint transition-colors rounded-lg px-lg py-sm shadow-sm">
                        Registrar Mascota
                    </button>
<button class="font-label-md text-label-md text-primary bg-secondary-container hover:bg-surface-container-high transition-colors rounded-lg px-lg py-sm">
                        Conoce Nuestros Servicios
                    </button>
</div>
</div>
<div class="flex-1 w-full relative h-[400px] md:h-[600px] rounded-xl overflow-hidden custom-shadow-level-1">
<img alt="Mascota feliz en clínica" class="absolute inset-0 w-full h-full object-cover" data-alt="A heartwarming and high-quality photograph of a happy Golden Retriever and its smiling owner in a bright, modern veterinary clinic. The lighting is soft, natural, and airy, emphasizing a clean, welcoming 'Premium-Startup' aesthetic. The color palette features subtle sage greens and warm off-whites, projecting trust, calm, and gentle precision." src="https://lh3.googleusercontent.com/aida-public/AB6AXuCUlcFJhh-W0-ZmsBoV4carxmSdUhRDuDbuIrwvxlOhYoVLklM9k2hod1FmfCrJeC6GeRzL5es--2j9DDLUDwjSaLj30mhRzA21AwVhfn22Q2uU93zYu3PRB7M8ctLW2nuQW5A0XE6ND6oT96zG8G4OgaWiJu7ONXZLG3QT16avWsToYDiJsOOSw14Toav7hFad3UGI8q4C6QQSdrblkAloe4U21TKbk0ftQqId_qZxQocFKR_Nr3WtSLRmwT-G4vZ5R9eYd8IiCDBW">
</div>
</section>
<!-- Core Services (Bento) -->
<section class="pt-xl pb-lg" id="servicios">
<div class="mb-lg text-center">
<h2 class="font-headline-lg text-headline-lg md:text-headline-lg text-on-surface mb-sm">Servicios Integrales</h2>
<p class="font-body-md text-body-md text-on-surface-variant max-w-[600px] mx-auto">Diseñados para cubrir todas las etapas de la vida de tu mascota, con la tranquilidad que brinda la excelencia médica.</p>
</div>
<div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
<!-- Service 1 -->
<div class="bg-surface-container-lowest rounded-xl p-md custom-shadow-level-1 flex flex-col gap-sm border border-transparent hover:border-primary/20 transition-colors">
<div class="w-12 h-12 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container mb-xs">
<span class="material-symbols-outlined" data-icon="monitor_heart">monitor_heart</span>
</div>
<h3 class="font-headline-md text-headline-md text-on-surface">Bienestar General</h3>
<p class="font-body-md text-body-md text-on-surface-variant flex-1">Chequeos preventivos, vacunación y planes nutricionales personalizados para mantener a tu compañero vital y saludable.</p>
<a class="font-label-md text-label-md text-primary inline-flex items-center gap-xs mt-sm hover:underline decoration-primary" href="#">
                        Saber más <span class="material-symbols-outlined text-[16px]" data-icon="arrow_forward">arrow_forward</span>
</a>
</div>
<!-- Service 2 -->
<div class="bg-surface-container-lowest rounded-xl p-md custom-shadow-level-1 flex flex-col gap-sm border border-transparent hover:border-primary/20 transition-colors md:col-span-2 relative overflow-hidden">
<div class="relative z-10 flex flex-col h-full justify-between">
<div>
<div class="w-12 h-12 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container mb-xs">
<span class="material-symbols-outlined" data-icon="medical_services">medical_services</span>
</div>
<h3 class="font-headline-md text-headline-md text-on-surface">Cirugía Avanzada</h3>
<p class="font-body-md text-body-md text-on-surface-variant max-w-[400px]">Quirófanos equipados con tecnología de última generación y monitoreo constante para procedimientos seguros y recuperaciones rápidas.</p>
</div>
<a class="font-label-md text-label-md text-primary inline-flex items-center gap-xs mt-sm hover:underline decoration-primary" href="#">
                            Instalaciones <span class="material-symbols-outlined text-[16px]" data-icon="arrow_forward">arrow_forward</span>
</a>
</div>
<!-- Decorative element -->
<div class="absolute right-0 bottom-0 w-64 h-64 bg-surface-container-low rounded-tl-full -z-0 opacity-50"></div>
</div>
<!-- Service 3 -->
<div class="bg-surface-container-lowest rounded-xl p-md custom-shadow-level-1 flex flex-col gap-sm border border-transparent hover:border-primary/20 transition-colors">
<div class="w-12 h-12 rounded-full bg-tertiary-container flex items-center justify-center text-on-tertiary-container mb-xs">
<span class="material-symbols-outlined" data-icon="dentistry">dentistry</span>
</div>
<h3 class="font-headline-md text-headline-md text-on-surface">Cuidado Dental</h3>
<p class="font-body-md text-body-md text-on-surface-variant flex-1">Profilaxis, extracciones y tratamientos periodontales para asegurar una sonrisa sana y prevenir enfermedades sistémicas.</p>
</div>
<!-- CTA Card within grid -->
<div class="bg-primary rounded-xl p-md flex flex-col items-center justify-center text-center gap-sm md:col-span-2">
<h3 class="font-headline-md text-headline-md text-on-primary">¿Necesitas una consulta urgente?</h3>
<p class="font-body-md text-body-md text-on-primary/90 max-w-[400px]">Nuestro equipo está disponible para atender emergencias con la rapidez y precisión necesarias.</p>
<button class="mt-sm font-label-md text-label-md text-primary bg-on-primary hover:bg-surface transition-colors rounded-lg px-lg py-sm">
                        Contactar Ahora
                    </button>
</div>
</div>
</section>
</main>
<!-- Footer -->
<footer class="w-full bg-surface-container-highest border-t border-outline-variant/30">
<div class="max-w-[1440px] mx-auto px-margin-desktop flex flex-col md:flex-row justify-between items-center gap-md py-lg">
<div class="font-headline-md text-headline-md text-primary">
                Huellitas Alegres
            </div>
<div class="flex gap-md">
<a class="font-body-md text-body-md text-on-surface-variant hover:text-primary underline decoration-transparent hover:decoration-primary transition-all" href="#">Privacidad</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:text-primary underline decoration-transparent hover:decoration-primary transition-all" href="#">Términos</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:text-primary underline decoration-transparent hover:decoration-primary transition-all" href="#">Soporte</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:text-primary underline decoration-transparent hover:decoration-primary transition-all" href="#">Contacto</a>
</div>
<div class="font-caption text-caption text-on-surface-variant">
                © 2024 Huellitas Alegres. Gentle Precision in Veterinary Care.
            </div>
</div>
</footer>


</body></html>

SEGUNDO DASHBOARD ADMINISTRADOR
<!DOCTYPE html>

<html class="light" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Huellitas Alegres - Admin Dashboard</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&amp;family=Plus+Jakarta+Sans:wght@600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: {
            extend: {
              "colors": {
                      "surface-container-low": "#f3f4f5",
                      "secondary": "#625e56",
                      "surface": "#f8f9fa",
                      "tertiary-fixed": "#d9eaa3",
                      "on-tertiary": "#ffffff",
                      "secondary-container": "#e6dfd5",
                      "on-background": "#191c1d",
                      "on-primary-container": "#ccf0cc",
                      "on-secondary": "#ffffff",
                      "outline-variant": "#c2c8bf",
                      "surface-container-lowest": "#ffffff",
                      "error-container": "#ffdad6",
                      "surface-container-high": "#e7e8e9",
                      "secondary-fixed-dim": "#cdc5bc",
                      "secondary-fixed": "#e9e1d8",
                      "surface-bright": "#f8f9fa",
                      "on-primary-fixed-variant": "#2f4e33",
                      "tertiary": "#47541d",
                      "tertiary-container": "#5e6d33",
                      "primary-fixed": "#c8ecc8",
                      "primary-fixed-dim": "#acd0ad",
                      "on-tertiary-fixed-variant": "#3e4c16",
                      "outline": "#737971",
                      "on-secondary-container": "#67625a",
                      "on-surface-variant": "#424841",
                      "surface-container-highest": "#e1e3e4",
                      "surface-variant": "#e1e3e4",
                      "on-surface": "#191c1d",
                      "on-primary-fixed": "#03210b",
                      "background": "#f8f9fa",
                      "surface-container": "#edeeef",
                      "on-primary": "#ffffff",
                      "inverse-surface": "#2e3132",
                      "on-secondary-fixed": "#1e1b15",
                      "on-tertiary-fixed": "#161f00",
                      "inverse-primary": "#acd0ad",
                      "surface-tint": "#466649",
                      "error": "#ba1a1a",
                      "tertiary-fixed-dim": "#bdce89",
                      "surface-dim": "#d9dadb",
                      "primary-container": "#4f6f52",
                      "on-error": "#ffffff",
                      "on-secondary-fixed-variant": "#4a463f",
                      "primary": "#37563b",
                      "on-error-container": "#93000a",
                      "inverse-on-surface": "#f0f1f2",
                      "on-tertiary-container": "#ddeea7"
              },
              "borderRadius": {
                      "DEFAULT": "0.25rem",
                      "lg": "0.5rem",
                      "xl": "0.75rem",
                      "full": "9999px"
              },
              "spacing": {
                      "base": "8px",
                      "xl": "80px",
                      "margin-desktop": "40px",
                      "md": "24px",
                      "lg": "48px",
                      "margin-mobile": "16px",
                      "gutter": "24px",
                      "xs": "4px",
                      "sm": "12px"
              },
              "fontFamily": {
                      "label-md": [
                              "Manrope"
                      ],
                      "headline-lg-mobile": [
                              "Plus Jakarta Sans"
                      ],
                      "headline-md": [
                              "Plus Jakarta Sans"
                      ],
                      "caption": [
                              "Manrope"
                      ],
                      "headline-lg": [
                              "Plus Jakarta Sans"
                      ],
                      "body-lg": [
                              "Manrope"
                      ],
                      "body-md": [
                              "Manrope"
                      ],
                      "display-lg": [
                              "Plus Jakarta Sans"
                      ]
              },
              "fontSize": {
                      "label-md": [
                              "14px",
                              {
                                      "lineHeight": "1.2",
                                      "letterSpacing": "0.01em",
                                      "fontWeight": "600"
                              }
                      ],
                      "headline-lg-mobile": [
                              "28px",
                              {
                                      "lineHeight": "1.3",
                                      "fontWeight": "600"
                              }
                      ],
                      "headline-md": [
                              "24px",
                              {
                                      "lineHeight": "1.4",
                                      "fontWeight": "600"
                              }
                      ],
                      "caption": [
                              "12px",
                              {
                                      "lineHeight": "1.2",
                                      "fontWeight": "500"
                              }
                      ],
                      "headline-lg": [
                              "32px",
                              {
                                      "lineHeight": "1.3",
                                      "fontWeight": "600"
                              }
                      ],
                      "body-lg": [
                              "18px",
                              {
                                      "lineHeight": "1.6",
                                      "fontWeight": "400"
                              }
                      ],
                      "body-md": [
                              "16px",
                              {
                                      "lineHeight": "1.6",
                                      "fontWeight": "400"
                              }
                      ],
                      "display-lg": [
                              "48px",
                              {
                                      "lineHeight": "1.2",
                                      "letterSpacing": "-0.02em",
                                      "fontWeight": "700"
                              }
                      ]
              }
      },
          },
        }
    </script>
<style>
        .card-shadow {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        }
        .hide-scrollbar::-webkit-scrollbar {
            display: none;
        }
        .hide-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
    </style>
</head>
<body class="bg-background min-h-screen text-on-background font-body-md text-body-md flex antialiased">
<!-- SideNavBar -->
<nav class="bg-surface-container-low dark:bg-surface-container-lowest border-r border-outline-variant/20 h-screen w-[280px] fixed left-0 top-0 flex flex-col p-md gap-base z-40">
<!-- Brand/Header -->
<div class="mb-lg px-sm">
<h1 class="font-headline-md text-headline-md text-primary dark:text-primary-fixed font-bold tracking-tight">Huellitas Alegres</h1>
<p class="font-caption text-caption text-secondary mt-xs">Portal Administrativo</p>
</div>
<!-- CTA -->
<button class="w-full bg-primary text-on-primary font-label-md text-label-md rounded-lg py-sm px-md mb-md hover:opacity-90 transition-opacity flex items-center justify-center gap-xs shadow-sm">
<span class="material-symbols-outlined text-[18px]">add</span>
            Nueva Cita
        </button>
<!-- Navigation Links -->
<ul class="flex flex-col gap-xs flex-1">
<li>
<a class="bg-primary-container dark:bg-primary-fixed-dim text-on-primary-container dark:text-on-primary-fixed rounded-lg font-bold flex items-center gap-3 px-4 py-3 translate-x-1 transition-transform font-label-md text-label-md" href="#">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">dashboard</span>
                    Dashboard
                </a>
</li>
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">calendar_today</span>
                    Citas
                </a>
</li>
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">pets</span>
                    Pacientes
                </a>
</li>
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">inventory_2</span>
                    Inventario
                </a>
</li>
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">payments</span>
                    Finanzas
                </a>
</li>
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">settings</span>
                    Configuración
                </a>
</li>
</ul>
<!-- Footer Links -->
<ul class="flex flex-col gap-xs mt-auto pt-md border-t border-outline-variant/20">
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">help</span>
                    Ayuda
                </a>
</li>
<li>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest font-label-md text-label-md" href="#">
<span class="material-symbols-outlined">logout</span>
                    Cerrar Sesión
                </a>
</li>
</ul>
</nav>
<!-- Main Content Area -->
<main class="ml-[280px] flex-1 flex flex-col min-h-screen">
<!-- TopNavBar (Dashboard Version) -->
<header class="bg-surface dark:bg-surface-dim shadow-sm fixed top-0 w-[calc(100%-280px)] z-30 h-[72px] flex justify-between items-center px-md py-sm">
<!-- Search -->
<div class="relative w-full max-w-[400px]">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-secondary">search</span>
<input class="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant/30 rounded-lg font-body-md text-body-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" placeholder="Buscar pacientes, citas, o facturas..." type="text"/>
</div>
<!-- Trailing Actions -->
<div class="flex items-center gap-sm">
<button class="text-on-surface-variant hover:bg-surface-container rounded-full p-2 transition-all relative">
<span class="material-symbols-outlined">notifications</span>
<span class="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full"></span>
</button>
<button class="text-on-surface-variant hover:bg-surface-container rounded-full p-2 transition-all">
<span class="material-symbols-outlined">chat_bubble</span>
</button>
<div class="h-8 w-px bg-outline-variant/30 mx-sm"></div>
<button class="flex items-center gap-2 hover:bg-surface-container rounded-full p-1 pr-3 transition-all">
<img alt="Admin User Profile" class="w-8 h-8 rounded-full object-cover border border-outline-variant/20" data-alt="A close-up, professional portrait of a female veterinarian with an approachable, warm smile, wearing a clean white clinical coat over a soft sage green scrub. The background is a gently out-of-focus, modern, well-lit veterinary clinic with bright, natural lighting. The mood is trustworthy and compassionate, reflecting a premium healthcare startup aesthetic." src="https://lh3.googleusercontent.com/aida-public/AB6AXuDiK24mj9W2qWGiO8YyLJHWleHi7Ust1G16sJICufCWkMPQ0cdHg0GgBvtU9Si2sLkGcTUTRjFQftruV8yuOly0H25bmcG-Zwg_-Nfdk3XGVzduI74WYFvUjxRi3RUU1cROagOsFuPhAb_aOzDvs_ZeXG9SpoRj6IReghucPzBoalORCkLInm5Bl_mHaX_GpAvjG5I7V-9pDAwBpXyVnL89MNeZ18t3GwNF-oD3ILvJlHhpQuJrZ84KAXORzZ04nquTHD1HXqtdI1cw"/>
<span class="font-label-md text-label-md text-on-surface">Dra. Martinez</span>
</button>
</div>
</header>
<!-- Dashboard Content Stage -->
<div class="mt-[72px] p-md max-w-[1440px] w-full mx-auto flex flex-col gap-sm">
<!-- Welcome Header -->
<div class="flex justify-between items-end mb-xs">
<div>
<h2 class="font-headline-lg text-headline-lg text-on-surface">Resumen General</h2>
<p class="font-body-md text-body-md text-secondary mt-1">Aquí tienes el estado actual de la clínica hoy, 24 de Octubre.</p>
</div>
<button class="bg-secondary-container/30 text-primary font-label-md text-label-md rounded-lg py-2 px-4 hover:bg-secondary-container/50 transition-colors flex items-center gap-2">
<span class="material-symbols-outlined text-[18px]">download</span>
                    Exportar Reporte
                </button>
</div>
<!-- Metrics Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-sm">
<!-- Metric 1: Revenue -->
<div class="bg-surface-container-lowest card-shadow rounded-xl p-md border border-outline-variant/10 flex flex-col justify-between">
<div class="flex justify-between items-start">
<span class="font-label-md text-label-md text-secondary uppercase tracking-wider">Ingresos (Mes)</span>
<div class="bg-primary-container/20 p-1.5 rounded-lg text-primary">
<span class="material-symbols-outlined text-[20px]">trending_up</span>
</div>
</div>
<div class="mt-4">
<h3 class="font-headline-lg text-headline-lg text-on-surface">$42,500</h3>
<p class="font-caption text-caption text-primary flex items-center gap-1 mt-1">
<span class="material-symbols-outlined text-[14px]">arrow_upward</span>
                            12.5% vs mes anterior
                        </p>
</div>
</div>
<!-- Metric 2: Occupancy -->
<div class="bg-surface-container-lowest card-shadow rounded-xl p-md border border-outline-variant/10 flex flex-col justify-between">
<div class="flex justify-between items-start">
<span class="font-label-md text-label-md text-secondary uppercase tracking-wider">Ocupación Clínica</span>
<div class="bg-tertiary-container/20 p-1.5 rounded-lg text-tertiary">
<span class="material-symbols-outlined text-[20px]">local_hospital</span>
</div>
</div>
<div class="mt-4">
<h3 class="font-headline-lg text-headline-lg text-on-surface">85%</h3>
<div class="w-full bg-surface-container-high rounded-full h-2 mt-2">
<div class="bg-tertiary h-2 rounded-full" style="width: 85%"></div>
</div>
<p class="font-caption text-caption text-secondary mt-2">17 de 20 boxes ocupados</p>
</div>
</div>
<!-- Metric 3: Active Staff -->
<div class="bg-surface-container-lowest card-shadow rounded-xl p-md border border-outline-variant/10 flex flex-col justify-between">
<div class="flex justify-between items-start">
<span class="font-label-md text-label-md text-secondary uppercase tracking-wider">Staff Activo</span>
<div class="bg-secondary-container/50 p-1.5 rounded-lg text-secondary">
<span class="material-symbols-outlined text-[20px]">groups</span>
</div>
</div>
<div class="mt-4 flex items-end justify-between">
<h3 class="font-headline-lg text-headline-lg text-on-surface">12</h3>
<div class="flex -space-x-2">
<img alt="Staff 1" class="w-8 h-8 rounded-full border-2 border-surface-container-lowest object-cover" data-alt="A small circular profile picture of a young male veterinary technician in a clean, brightly lit clinic setting. He is wearing teal scrubs and has a warm, professional expression. The image is bright and modern." src="https://lh3.googleusercontent.com/aida-public/AB6AXuA1x-yvaVqwh12VOtAdFZFRoPNfYxKPoBUifaiPJ1CloGxC9d5YMqQ5dnZ6vAKuO5omEJqvWx6BwM2GITU2pfm_-YepmtWEqlBQ_n7j4fAo5K3IUTrehjiIq780284tqRsylqCSkP0G5XYPWLjr_uBDX1fznSdl_d6gNnxsDy4Hipnw39tbL_5EropLYs2f8-KVzfzN4YaR_ku9D2-RmjJtojYArheIqeSRAsCKkrSIR3HVanezPZIndxOL2rC-h4tuRM1cj75l8QwS"/>
<img alt="Staff 2" class="w-8 h-8 rounded-full border-2 border-surface-container-lowest object-cover" data-alt="A small circular profile picture of an older female veterinarian with glasses, looking knowledgeable and friendly. She is in a well-lit, minimalist examination room. The lighting is soft and natural." src="https://lh3.googleusercontent.com/aida-public/AB6AXuChEJdJAbBAo1dSvFSZ6zuG-z1zQlC1ya5D2indf9Jp8UAtmWlHF-1UignbGiaggw_obZb7cWFGmOTHtFElvYMFXaHbAiElEitedo5BdylmgsqOecMy5YV_70JdslGgmIXf3B425YDENkkQy7RR3lVUx-kQ5sVdqiO9UTzSeexx82hSreXmS8RLmikbQMb5HgHZLTSRLMyA6T6oEfUeGfs0iBwbIMpiRz_lYIYOkC3-ebYNtyy8OhmEIf5pDrOVkK-ezuutF_HxN1SO"/>
<img alt="Staff 3" class="w-8 h-8 rounded-full border-2 border-surface-container-lowest object-cover" data-alt="A small circular profile picture of a male doctor in a white coat. The background is a clean, modern white wall with a hint of a green plant, reflecting a calming, premium healthcare environment." src="https://lh3.googleusercontent.com/aida-public/AB6AXuC_z2O1gS8yJSNYj-3J5BpwSTeSMdu16cm2RX36YOcm4IrGVxNlADz32HUOZoVcVAFxl1_zRTy507ZEKAfMwWl8TJZ06tpZ4qmIVyTePeShisteYNBCw-vg1qcBfmGbQkdMAttEVQNVFj-PGsLf0i0-3DajxgSo5XDh8AvUR0k6VB499kzAeQEn0IlnQPG1r0Pvo-rwYM1ewXgTEwiqQbhs8B8Gb8kvh31pqUKzQy4F2ydof4FBa1Z7hRjjeI6EcYd_qtesOT7zc_eH"/>
<div class="w-8 h-8 rounded-full border-2 border-surface-container-lowest bg-surface-container-high flex items-center justify-center font-caption text-caption text-secondary">+9</div>
</div>
</div>
</div>
<!-- Metric 4: Critical Alerts -->
<div class="bg-[#FFF5F5] card-shadow rounded-xl p-md border border-error-container/50 flex flex-col justify-between">
<div class="flex justify-between items-start">
<span class="font-label-md text-label-md text-[#93000A] uppercase tracking-wider">Alertas Críticas</span>
<div class="bg-[#FFDAD6] p-1.5 rounded-lg text-[#BA1A1A]">
<span class="material-symbols-outlined text-[20px]" style="font-variation-settings: 'FILL' 1;">warning</span>
</div>
</div>
<div class="mt-4">
<h3 class="font-headline-lg text-headline-lg text-[#93000A]">3</h3>
<p class="font-caption text-caption text-[#BA1A1A] mt-1">Suministros bajos / Urgencias</p>
</div>
</div>
</div>
<!-- Main Content Grid (Charts & Lists) -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-sm mt-xs">
<!-- Revenue Chart Area (Spans 2 cols) -->
<div class="bg-surface-container-lowest card-shadow rounded-xl p-md border border-outline-variant/10 lg:col-span-2 flex flex-col">
<div class="flex justify-between items-center mb-md">
<h3 class="font-headline-md text-headline-md text-on-surface">Flujo de Ingresos</h3>
<select class="bg-surface border border-outline-variant/30 rounded-lg px-3 py-1 font-caption text-caption text-on-surface-variant focus:outline-none focus:border-primary">
<option>Últimos 7 días</option>
<option>Este Mes</option>
<option>Este Año</option>
</select>
</div>
<!-- Mock Chart -->
<div class="flex-1 min-h-[240px] flex items-end gap-2 pt-8 relative">
<!-- Y-axis labels -->
<div class="absolute left-0 top-0 h-full flex flex-col justify-between text-secondary font-caption text-caption pb-8">
<span>$5k</span>
<span>$4k</span>
<span>$3k</span>
<span>$2k</span>
<span>$1k</span>
<span>$0</span>
</div>
<!-- Grid lines -->
<div class="absolute left-8 right-0 top-0 h-[calc(100%-32px)] flex flex-col justify-between pointer-events-none">
<div class="border-t border-outline-variant/10 w-full"></div>
<div class="border-t border-outline-variant/10 w-full"></div>
<div class="border-t border-outline-variant/10 w-full"></div>
<div class="border-t border-outline-variant/10 w-full"></div>
<div class="border-t border-outline-variant/10 w-full"></div>
<div class="border-t border-outline-variant/30 w-full"></div>
</div>
<!-- Bars -->
<div class="w-full h-full flex items-end justify-between pl-10 pb-8 z-10">
<div class="w-[10%] bg-primary-container/40 rounded-t-sm h-[40%] hover:bg-primary-container transition-colors relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-secondary">Lun</span>
</div>
<div class="w-[10%] bg-primary-container/40 rounded-t-sm h-[60%] hover:bg-primary-container transition-colors relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-secondary">Mar</span>
</div>
<div class="w-[10%] bg-primary-container/40 rounded-t-sm h-[45%] hover:bg-primary-container transition-colors relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-secondary">Mie</span>
</div>
<div class="w-[10%] bg-primary-container rounded-t-sm h-[80%] relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-on-surface font-bold">Jue</span>
</div>
<div class="w-[10%] bg-primary-container/40 rounded-t-sm h-[65%] hover:bg-primary-container transition-colors relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-secondary">Vie</span>
</div>
<div class="w-[10%] bg-tertiary-container/30 rounded-t-sm h-[90%] hover:bg-tertiary-container transition-colors relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-secondary">Sab</span>
</div>
<div class="w-[10%] bg-tertiary-container/30 rounded-t-sm h-[30%] hover:bg-tertiary-container transition-colors relative group">
<span class="absolute -bottom-6 left-1/2 -translate-x-1/2 font-caption text-caption text-secondary">Dom</span>
</div>
</div>
</div>
</div>
<!-- Inventory Alerts -->
<div class="bg-surface-container-lowest card-shadow rounded-xl p-md border border-outline-variant/10 flex flex-col">
<div class="flex justify-between items-center mb-md">
<h3 class="font-headline-md text-headline-md text-on-surface">Inventario Crítico</h3>
<a class="font-label-md text-label-md text-primary hover:underline" href="#">Ver todo</a>
</div>
<div class="flex flex-col gap-3 flex-1 overflow-y-auto hide-scrollbar">
<!-- Alert Item -->
<div class="flex items-center gap-3 p-3 bg-error-container/20 rounded-lg border border-error-container">
<div class="w-10 h-10 rounded-full bg-surface flex items-center justify-center text-error shrink-0">
<span class="material-symbols-outlined">vaccines</span>
</div>
<div class="flex-1 min-w-0">
<p class="font-label-md text-label-md text-on-surface truncate">Vacuna Antirrábica</p>
<p class="font-caption text-caption text-error">Quedan 5 dosis</p>
</div>
<button class="text-primary font-caption text-caption bg-primary-fixed/30 px-2 py-1 rounded hover:bg-primary-fixed/50">Pedir</button>
</div>
<!-- Alert Item -->
<div class="flex items-center gap-3 p-3 bg-surface-container rounded-lg border border-outline-variant/20">
<div class="w-10 h-10 rounded-full bg-surface flex items-center justify-center text-secondary shrink-0">
<span class="material-symbols-outlined">medication</span>
</div>
<div class="flex-1 min-w-0">
<p class="font-label-md text-label-md text-on-surface truncate">Meloxicam 1.5mg</p>
<p class="font-caption text-caption text-secondary">Quedan 12 cajas</p>
</div>
<button class="text-primary font-caption text-caption bg-primary-fixed/30 px-2 py-1 rounded hover:bg-primary-fixed/50">Pedir</button>
</div>
<!-- Alert Item -->
<div class="flex items-center gap-3 p-3 bg-surface-container rounded-lg border border-outline-variant/20">
<div class="w-10 h-10 rounded-full bg-surface flex items-center justify-center text-secondary shrink-0">
<span class="material-symbols-outlined">healing</span>
</div>
<div class="flex-1 min-w-0">
<p class="font-label-md text-label-md text-on-surface truncate">Gasas Estériles</p>
<p class="font-caption text-caption text-secondary">Quedan 20 paquetes</p>
</div>
<button class="text-primary font-caption text-caption bg-primary-fixed/30 px-2 py-1 rounded hover:bg-primary-fixed/50">Pedir</button>
</div>
</div>
</div>
</div>
<!-- Recent Activity Log (Full Width Table) -->
<div class="bg-surface-container-lowest card-shadow rounded-xl p-md border border-outline-variant/10 mt-xs overflow-hidden">
<div class="flex justify-between items-center mb-md">
<h3 class="font-headline-md text-headline-md text-on-surface">Actividad Reciente</h3>
<div class="flex gap-2">
<button class="p-1.5 rounded-md hover:bg-surface-container text-secondary transition-colors"><span class="material-symbols-outlined text-[20px]">filter_list</span></button>
<button class="p-1.5 rounded-md hover:bg-surface-container text-secondary transition-colors"><span class="material-symbols-outlined text-[20px]">more_vert</span></button>
</div>
</div>
<div class="overflow-x-auto">
<table class="w-full text-left border-collapse">
<thead>
<tr class="border-b border-outline-variant/30 text-secondary font-label-md text-label-md">
<th class="pb-3 px-2 font-semibold">Paciente / Cliente</th>
<th class="pb-3 px-2 font-semibold">Tipo</th>
<th class="pb-3 px-2 font-semibold">Monto</th>
<th class="pb-3 px-2 font-semibold">Estado</th>
<th class="pb-3 px-2 font-semibold text-right">Hora</th>
</tr>
</thead>
<tbody class="font-body-md text-body-md text-on-surface">
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-low transition-colors group">
<td class="py-3 px-2">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold text-[12px]">B</div>
<div>
<p class="font-medium text-on-surface">Bella (Golden Retriever)</p>
<p class="font-caption text-caption text-secondary">Carlos Ruiz</p>
</div>
</div>
</td>
<td class="py-3 px-2">Consulta General</td>
<td class="py-3 px-2 font-medium">$45.00</td>
<td class="py-3 px-2">
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#E6F4EA] text-[#1E8E3E] font-caption text-caption">
<span class="w-1.5 h-1.5 rounded-full bg-[#1E8E3E]"></span>
                                        Completado
                                    </span>
</td>
<td class="py-3 px-2 text-right text-secondary text-sm">Hace 10 min</td>
</tr>
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-low transition-colors group">
<td class="py-3 px-2">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-tertiary-container/30 flex items-center justify-center text-tertiary font-bold text-[12px]">L</div>
<div>
<p class="font-medium text-on-surface">Luna (Siamés)</p>
<p class="font-caption text-caption text-secondary">María Gómez</p>
</div>
</div>
</td>
<td class="py-3 px-2">Cirugía Menor</td>
<td class="py-3 px-2 font-medium">$250.00</td>
<td class="py-3 px-2">
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FEF7E0] text-[#B06000] font-caption text-caption">
<span class="w-1.5 h-1.5 rounded-full bg-[#B06000]"></span>
                                        En Progreso
                                    </span>
</td>
<td class="py-3 px-2 text-right text-secondary text-sm">Hace 45 min</td>
</tr>
<tr class="hover:bg-surface-container-low transition-colors group">
<td class="py-3 px-2">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-primary-container/30 flex items-center justify-center text-primary font-bold text-[12px]">R</div>
<div>
<p class="font-medium text-on-surface">Rocky (Bulldog)</p>
<p class="font-caption text-caption text-secondary">Familia Torres</p>
</div>
</div>
</td>
<td class="py-3 px-2">Vacunación</td>
<td class="py-3 px-2 font-medium">$35.00</td>
<td class="py-3 px-2">
<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#F3F4F5] text-[#5F6368] font-caption text-caption">
<span class="w-1.5 h-1.5 rounded-full bg-[#5F6368]"></span>
                                        Pendiente
                                    </span>
</td>
<td class="py-3 px-2 text-right text-secondary text-sm">Hace 2 hrs</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
</main>
</body></html>

TERCERO DASHBOARD VETERINARIO
<!DOCTYPE html>

<html class="light" lang="es"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Huellitas Alegres - Veterinario Dashboard</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&amp;family=Plus+Jakarta+Sans:wght@600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
          darkMode: "class",
          theme: {
            extend: {
              "colors": {
                      "surface-container-low": "#f3f4f5",
                      "secondary": "#625e56",
                      "surface": "#f8f9fa",
                      "tertiary-fixed": "#d9eaa3",
                      "on-tertiary": "#ffffff",
                      "secondary-container": "#e6dfd5",
                      "on-background": "#191c1d",
                      "on-primary-container": "#ccf0cc",
                      "on-secondary": "#ffffff",
                      "outline-variant": "#c2c8bf",
                      "surface-container-lowest": "#ffffff",
                      "error-container": "#ffdad6",
                      "surface-container-high": "#e7e8e9",
                      "secondary-fixed-dim": "#cdc5bc",
                      "secondary-fixed": "#e9e1d8",
                      "surface-bright": "#f8f9fa",
                      "on-primary-fixed-variant": "#2f4e33",
                      "tertiary": "#47541d",
                      "tertiary-container": "#5e6d33",
                      "primary-fixed": "#c8ecc8",
                      "primary-fixed-dim": "#acd0ad",
                      "on-tertiary-fixed-variant": "#3e4c16",
                      "outline": "#737971",
                      "on-secondary-container": "#67625a",
                      "on-surface-variant": "#424841",
                      "surface-container-highest": "#e1e3e4",
                      "surface-variant": "#e1e3e4",
                      "on-surface": "#191c1d",
                      "on-primary-fixed": "#03210b",
                      "background": "#f8f9fa",
                      "surface-container": "#edeeef",
                      "on-primary": "#ffffff",
                      "inverse-surface": "#2e3132",
                      "on-secondary-fixed": "#1e1b15",
                      "on-tertiary-fixed": "#161f00",
                      "inverse-primary": "#acd0ad",
                      "surface-tint": "#466649",
                      "error": "#ba1a1a",
                      "tertiary-fixed-dim": "#bdce89",
                      "surface-dim": "#d9dadb",
                      "primary-container": "#4f6f52",
                      "on-error": "#ffffff",
                      "on-secondary-fixed-variant": "#4a463f",
                      "primary": "#37563b",
                      "on-error-container": "#93000a",
                      "inverse-on-surface": "#f0f1f2",
                      "on-tertiary-container": "#ddeea7"
              },
              "borderRadius": {
                      "DEFAULT": "0.25rem",
                      "lg": "0.5rem",
                      "xl": "0.75rem",
                      "full": "9999px"
              },
              "spacing": {
                      "base": "8px",
                      "xl": "80px",
                      "margin-desktop": "40px",
                      "md": "24px",
                      "lg": "48px",
                      "margin-mobile": "16px",
                      "gutter": "24px",
                      "xs": "4px",
                      "sm": "12px"
              },
              "fontFamily": {
                      "label-md": ["Manrope"],
                      "headline-lg-mobile": ["Plus Jakarta Sans"],
                      "headline-md": ["Plus Jakarta Sans"],
                      "caption": ["Manrope"],
                      "headline-lg": ["Plus Jakarta Sans"],
                      "body-lg": ["Manrope"],
                      "body-md": ["Manrope"],
                      "display-lg": ["Plus Jakarta Sans"]
              },
              "fontSize": {
                      "label-md": ["14px", {"lineHeight": "1.2", "letterSpacing": "0.01em", "fontWeight": "600"}],
                      "headline-lg-mobile": ["28px", {"lineHeight": "1.3", "fontWeight": "600"}],
                      "headline-md": ["24px", {"lineHeight": "1.4", "fontWeight": "600"}],
                      "caption": ["12px", {"lineHeight": "1.2", "fontWeight": "500"}],
                      "headline-lg": ["32px", {"lineHeight": "1.3", "fontWeight": "600"}],
                      "body-lg": ["18px", {"lineHeight": "1.6", "fontWeight": "400"}],
                      "body-md": ["16px", {"lineHeight": "1.6", "fontWeight": "400"}],
                      "display-lg": ["48px", {"lineHeight": "1.2", "letterSpacing": "-0.02em", "fontWeight": "700"}]
              }
            }
          }
        }
    </script>
<style>
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .icon-fill {
            font-variation-settings: 'FILL' 1;
        }
    </style>
</head>
<body class="bg-background text-on-surface font-body-md antialiased overflow-x-hidden min-h-screen flex">
<!-- SideNavBar -->
<nav class="bg-surface-container-low dark:bg-surface-container-lowest border-r border-outline-variant/20 h-screen w-[280px] fixed left-0 top-0 flex flex-col p-md gap-base z-40 hidden md:flex">
<div class="flex items-center gap-sm mb-lg">
<div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary font-bold">
                HA
            </div>
<div>
<h1 class="font-headline-md text-headline-md text-primary dark:text-primary-fixed font-bold">Huellitas Alegres</h1>
<p class="font-caption text-caption text-secondary">Portal Administrativo</p>
</div>
</div>
<div class="flex-1 overflow-y-auto flex flex-col gap-sm">
<a class="bg-primary-container dark:bg-primary-fixed-dim text-on-primary-container dark:text-on-primary-fixed rounded-lg font-bold flex items-center gap-3 px-4 py-3 font-label-md text-label-md translate-x-1 transition-transform" href="#">
<span class="material-symbols-outlined icon-fill">dashboard</span>
                Dashboard
            </a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">calendar_today</span>
                Citas
            </a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">pets</span>
                Pacientes
            </a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">inventory_2</span>
                Inventario
            </a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">payments</span>
                Finanzas
            </a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">settings</span>
                Configuración
            </a>
</div>
<button class="bg-primary text-on-primary w-full py-3 rounded-lg font-label-md text-label-md mb-md hover:bg-primary/90 transition-colors">
            Nueva Cita
        </button>
<div class="border-t border-outline-variant/20 pt-md flex flex-col gap-sm">
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">help</span>
                Ayuda
            </a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors font-label-md text-label-md hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">logout</span>
                Cerrar Sesión
            </a>
</div>
</nav>
<!-- Main Content Area -->
<div class="flex-1 md:ml-[280px] flex flex-col min-h-screen">
<!-- TopNavBar (Dashboard) -->
<header class="bg-surface dark:bg-surface-dim shadow-sm docked top-0 w-full flex justify-between items-center px-md py-sm z-30 sticky">
<div class="flex items-center gap-sm flex-1">
<button class="md:hidden p-2 rounded-full hover:bg-surface-container text-on-surface-variant transition-colors">
<span class="material-symbols-outlined">menu</span>
</button>
<div class="relative w-full max-w-md hidden md:block">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
<input class="w-full pl-10 pr-4 py-2 rounded-full bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:ring-2 focus:ring-primary/50 outline-none font-body-md text-body-md text-on-surface placeholder:text-on-surface-variant transition-all" placeholder="Buscar paciente, cita..." type="text"/>
</div>
</div>
<div class="flex items-center gap-2">
<button class="text-on-surface-variant dark:text-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high rounded-full p-2 transition-all">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="text-on-surface-variant dark:text-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high rounded-full p-2 transition-all">
<span class="material-symbols-outlined">chat_bubble</span>
</button>
<button class="text-on-surface-variant dark:text-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high rounded-full p-2 transition-all ml-sm">
<img alt="Admin User Profile" class="w-8 h-8 rounded-full object-cover border border-outline-variant/30" data-alt="Close up professional portrait of a smiling veterinarian wearing scrubs in a well-lit, modern clinic. The lighting is soft and natural, emphasizing a trustworthy and caring demeanor. The background is slightly blurred, showing clean white and soft green tones typical of a premium veterinary practice." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBAl1NupVDjWnbLRZCGE57kr54PBHiO_59bD86zAZnHJdTw3YZZvuW7Ycol75z4FHzjjAVwcjNe3hnbNKHbnO4wpuEu3Yq8uVdKbA88xUhGWXEd_x3G3ev6d7fPOX8HjeHnVdxmlQCUBz9QlNnwKRvyj95Y9kco-Wmub_idfNZ1sOth3uOmDTstROBCar-cFF5HjxGNu_0pfnLKzAwERnA2VLhQverPbz3uVP__6qWz6LvC6y5h9KAE-Dwcke0XTm-nQsf_uL1OcYtU"/>
</button>
</div>
</header>
<!-- Canvas -->
<main class="flex-1 p-md md:p-lg max-w-[1440px] mx-auto w-full flex flex-col gap-lg">
<!-- Header Section -->
<div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-sm">
<div>
<h2 class="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-xs">Buenos días, Dr. Ramírez</h2>
<p class="font-body-md text-body-md text-on-surface-variant">Resumen de actividades para hoy, 24 de Octubre.</p>
</div>
<div class="flex gap-sm">
<button class="bg-surface border border-outline-variant text-on-surface font-label-md text-label-md px-4 py-2 rounded-lg hover:bg-surface-container transition-colors flex items-center gap-2">
<span class="material-symbols-outlined text-sm">filter_list</span>
                        Filtros
                    </button>
<button class="bg-primary text-on-primary font-label-md text-label-md px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors shadow-sm flex items-center gap-2">
<span class="material-symbols-outlined text-sm">add</span>
                        Registrar Consulta
                    </button>
</div>
</div>
<!-- Bento Grid Content -->
<div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
<!-- Schedule Column (Left, 8 cols) -->
<div class="lg:col-span-8 flex flex-col gap-gutter">
<!-- Quick Stats Row -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
<!-- Stat Card 1 -->
<div class="bg-white rounded-xl p-md shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-outline-variant/10 flex flex-col gap-sm relative overflow-hidden">
<div class="absolute -right-4 -top-4 w-16 h-16 bg-primary-container/20 rounded-full blur-xl"></div>
<div class="flex items-center gap-2 text-on-surface-variant font-label-md text-label-md uppercase tracking-wider">
<span class="material-symbols-outlined text-primary">calendar_clock</span>
                                Citas Hoy
                            </div>
<div class="font-display-lg text-display-lg text-on-surface">12</div>
<div class="font-caption text-caption text-secondary">3 pendientes de confirmación</div>
</div>
<!-- Stat Card 2 -->
<div class="bg-white rounded-xl p-md shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-outline-variant/10 flex flex-col gap-sm relative overflow-hidden">
<div class="absolute -right-4 -top-4 w-16 h-16 bg-tertiary-container/20 rounded-full blur-xl"></div>
<div class="flex items-center gap-2 text-on-surface-variant font-label-md text-label-md uppercase tracking-wider">
<span class="material-symbols-outlined text-tertiary">medical_services</span>
                                Tratamientos Activos
                            </div>
<div class="font-display-lg text-display-lg text-on-surface">8</div>
<div class="font-caption text-caption text-secondary">2 requieren revisión hoy</div>
</div>
<!-- Stat Card 3 -->
<div class="bg-white rounded-xl p-md shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-outline-variant/10 flex flex-col gap-sm relative overflow-hidden">
<div class="absolute -right-4 -top-4 w-16 h-16 bg-error-container/30 rounded-full blur-xl"></div>
<div class="flex items-center gap-2 text-on-surface-variant font-label-md text-label-md uppercase tracking-wider">
<span class="material-symbols-outlined text-error">science</span>
                                Resultados Pdte.
                            </div>
<div class="font-display-lg text-display-lg text-on-surface">4</div>
<div class="font-caption text-caption text-error font-medium">1 urgente (Hemograma)</div>
</div>
</div>
<!-- Daily Schedule Table Card -->
<div class="bg-white rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-outline-variant/10 overflow-hidden flex flex-col h-full">
<div class="p-md border-b border-outline-variant/10 flex justify-between items-center bg-surface/50">
<h3 class="font-headline-md text-headline-md text-on-surface">Agenda del Día</h3>
<button class="text-primary hover:text-primary-container font-label-md text-label-md transition-colors flex items-center gap-1">
                                Ver Calendario Completo <span class="material-symbols-outlined text-sm">arrow_forward</span>
</button>
</div>
<div class="overflow-x-auto">
<table class="w-full text-left font-body-md text-body-md">
<thead class="bg-surface-container-low text-on-surface-variant font-label-md text-label-md">
<tr>
<th class="py-sm px-md font-semibold">Hora</th>
<th class="py-sm px-md font-semibold">Paciente</th>
<th class="py-sm px-md font-semibold">Motivo</th>
<th class="py-sm px-md font-semibold">Estado</th>
<th class="py-sm px-md font-semibold text-right">Acción</th>
</tr>
</thead>
<tbody class="divide-y divide-outline-variant/10 text-on-surface">
<tr class="hover:bg-surface transition-colors group">
<td class="py-sm px-md font-medium text-primary">09:00 AM</td>
<td class="py-sm px-md">
<div class="flex items-center gap-3">
<img alt="Dog Patient" class="w-8 h-8 rounded-full object-cover border border-outline-variant/20" data-alt="A portrait of a Golden Retriever dog looking attentive. The lighting is bright and soft, typical of a professional pet photography studio. The background is a plain, neutral light gray, keeping the focus entirely on the dog's friendly expression." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBVaGCuxhu19LLMVzqfSJTC3uup4tCzqsvKeB5d13Y_Dm2fFzsjNFmQvhnIrLWAWwaFrGOdTxd7CWSAgX5grCq2xnfosSoxjNKXHczBxMCqsJLJVCICtT_yDxjkNlGbXuIQpypzs-5L8Fi12e6Z4ZrjBgSgwDhsE8eyxnOeH-0xOk0GFH5Rj-Jk8S88LFYZMzTr5vaJ9p1XkSa56-8P2odHTP1y3a3ociiRO1tDdu0zTsGkQMNTfTizwIER0qMkzRhvUr0ib54V_2S1"/>
<div>
<div class="font-medium">Luna</div>
<div class="text-sm text-on-surface-variant">Golden Retriever, 4a</div>
</div>
</div>
</td>
<td class="py-sm px-md">Vacunación Anual</td>
<td class="py-sm px-md">
<span class="inline-flex items-center px-2 py-1 rounded-full bg-surface-container-high text-on-surface-variant font-caption text-caption">En Sala de Espera</span>
</td>
<td class="py-sm px-md text-right">
<button class="bg-primary text-on-primary font-label-md text-label-md px-3 py-1.5 rounded-lg hover:bg-primary/90 transition-colors shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                                                Iniciar Consulta
                                            </button>
</td>
</tr>
<tr class="hover:bg-surface transition-colors group">
<td class="py-sm px-md font-medium">10:30 AM</td>
<td class="py-sm px-md">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold text-sm">
                                                    M
                                                </div>
<div>
<div class="font-medium">Max</div>
<div class="text-sm text-on-surface-variant">Gato Siamés, 2a</div>
</div>
</div>
</td>
<td class="py-sm px-md">Revisión Dermatológica</td>
<td class="py-sm px-md">
<span class="inline-flex items-center px-2 py-1 rounded-full bg-surface-container text-on-surface-variant font-caption text-caption">Confirmado</span>
</td>
<td class="py-sm px-md text-right">
<button class="bg-primary text-on-primary font-label-md text-label-md px-3 py-1.5 rounded-lg hover:bg-primary/90 transition-colors shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                                                Iniciar Consulta
                                            </button>
</td>
</tr>
<tr class="hover:bg-surface transition-colors group">
<td class="py-sm px-md font-medium">11:45 AM</td>
<td class="py-sm px-md">
<div class="flex items-center gap-3">
<img alt="Dog Patient" class="w-8 h-8 rounded-full object-cover border border-outline-variant/20" data-alt="A portrait of a French Bulldog sitting calmly. The dog has a dark brindle coat. The lighting is even and bright, casting soft shadows. The background is a clean, modern veterinary clinic setting with subtle light green accents in the decor." src="https://lh3.googleusercontent.com/aida-public/AB6AXuDieL4LDSXRvGFAUpQ2oKs5seKmySAeqaY_0-L2kvQ1jt4_GLXi7Wz3zlg6FzDoxZnKf02xgLyjPdpfn2c4rH6e1Z38zKpdddqK9oVZRwQP1Qs88NXzWwzlF1d04SNwtG8v8q8oS8YJmLtJE2g636VhrYjecdnFTTme4SZmkacU5F80x1NtBuQh3b5vOnL1nN_DSS4xWbVzgACv31LbXPXkHZ5d_C7BGNhU4UKtF3wks0p62t-RXASVC3IHmZ97Y6qM3eyFBYwPQ-3U"/>
<div>
<div class="font-medium">Rocky</div>
<div class="text-sm text-on-surface-variant">Bulldog Francés, 6m</div>
</div>
</div>
</td>
<td class="py-sm px-md">Seguimiento Post-operatorio</td>
<td class="py-sm px-md">
<span class="inline-flex items-center px-2 py-1 rounded-full bg-surface-container text-on-surface-variant font-caption text-caption">Confirmado</span>
</td>
<td class="py-sm px-md text-right">
<button class="bg-primary text-on-primary font-label-md text-label-md px-3 py-1.5 rounded-lg hover:bg-primary/90 transition-colors shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                                                Iniciar Consulta
                                            </button>
</td>
</tr>
<tr class="hover:bg-surface transition-colors opacity-60">
<td class="py-sm px-md font-medium line-through">08:00 AM</td>
<td class="py-sm px-md">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface-variant font-bold text-sm">
                                                    B
                                                </div>
<div>
<div class="font-medium">Bella</div>
<div class="text-sm text-on-surface-variant">Caniche, 8a</div>
</div>
</div>
</td>
<td class="py-sm px-md">Control Peso</td>
<td class="py-sm px-md">
<span class="inline-flex items-center px-2 py-1 rounded-full bg-tertiary-container/20 text-tertiary font-caption text-caption">Completado</span>
</td>
<td class="py-sm px-md text-right">
<button class="text-secondary font-label-md text-label-md px-3 py-1.5 rounded-lg hover:bg-surface-container transition-colors">
                                                Ver Resumen
                                            </button>
</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
<!-- Action/Info Column (Right, 4 cols) -->
<div class="lg:col-span-4 flex flex-col gap-gutter">
<!-- Lab Results Pending Widget -->
<div class="bg-white rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-outline-variant/10 p-md flex flex-col gap-sm">
<div class="flex justify-between items-center mb-xs">
<h3 class="font-label-md text-label-md uppercase tracking-wider text-on-surface flex items-center gap-2">
<span class="material-symbols-outlined text-primary">science</span>
                                Resultados de Laboratorio
                            </h3>
<span class="bg-error-container text-on-error-container text-xs font-bold px-2 py-0.5 rounded-full">1 Urgente</span>
</div>
<div class="flex flex-col gap-3">
<!-- Alert Item -->
<div class="bg-error-container/20 border-l-4 border-error p-3 rounded-r-lg flex justify-between items-start">
<div>
<div class="font-label-md text-label-md text-on-surface">Hemograma Completo</div>
<div class="font-caption text-caption text-on-surface-variant">Paciente: Thor (Husky)</div>
<div class="font-caption text-caption text-error mt-1 flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">warning</span> Anomalías detectadas
                                    </div>
</div>
<button class="text-primary hover:text-primary-container p-1 rounded hover:bg-surface transition-colors">
<span class="material-symbols-outlined">visibility</span>
</button>
</div>
<!-- Normal Item -->
<div class="bg-surface border border-outline-variant/20 p-3 rounded-lg flex justify-between items-start">
<div>
<div class="font-label-md text-label-md text-on-surface">Análisis de Orina</div>
<div class="font-caption text-caption text-on-surface-variant">Paciente: Mia (Persa)</div>
<div class="font-caption text-caption text-secondary mt-1">Recibido hace 2 hrs</div>
</div>
<button class="text-primary hover:text-primary-container p-1 rounded hover:bg-surface transition-colors">
<span class="material-symbols-outlined">visibility</span>
</button>
</div>
<!-- Pending Item -->
<div class="bg-surface border border-outline-variant/20 p-3 rounded-lg flex justify-between items-start opacity-70">
<div>
<div class="font-label-md text-label-md text-on-surface">Citología</div>
<div class="font-caption text-caption text-on-surface-variant">Paciente: Coco (Pug)</div>
<div class="font-caption text-caption text-secondary mt-1 flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">hourglass_empty</span> Pendiente lab externo
                                    </div>
</div>
</div>
</div>
<button class="mt-2 text-primary font-label-md text-label-md hover:underline text-center w-full">
                            Ver todos los resultados
                        </button>
</div>
<!-- Quick Access / Recent Patients -->
<div class="bg-white rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-outline-variant/10 p-md flex flex-col gap-sm flex-1">
<div class="flex justify-between items-center mb-xs">
<h3 class="font-label-md text-label-md uppercase tracking-wider text-on-surface flex items-center gap-2">
<span class="material-symbols-outlined text-primary">history</span>
                                Acceso Rápido
                            </h3>
</div>
<div class="relative mb-4">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
<input class="w-full pl-9 pr-3 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant/30 focus:border-primary focus:ring-1 focus:ring-primary/50 outline-none font-caption text-caption text-on-surface placeholder:text-on-surface-variant transition-all" placeholder="Buscar historia clínica..." type="text"/>
</div>
<div class="flex flex-col gap-2">
<!-- Patient Pill -->
<div class="flex items-center justify-between p-2 rounded-lg hover:bg-surface transition-colors cursor-pointer border border-transparent hover:border-outline-variant/20">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container font-bold text-xs">
                                        T
                                    </div>
<div>
<div class="font-label-md text-label-md text-on-surface">Thor</div>
<div class="font-caption text-caption text-on-surface-variant">HC-2023-089</div>
</div>
</div>
<span class="material-symbols-outlined text-outline">chevron_right</span>
</div>
<!-- Patient Pill -->
<div class="flex items-center justify-between p-2 rounded-lg hover:bg-surface transition-colors cursor-pointer border border-transparent hover:border-outline-variant/20">
<div class="flex items-center gap-3">
<img alt="Cat Patient" class="w-8 h-8 rounded-full object-cover border border-outline-variant/20" data-alt="A portrait of a fluffy domestic cat looking intently off-camera. The lighting is soft and natural, emphasizing the texture of its fur. The background is a clean, slightly out-of-focus white and light grey setting typical of a modern clinical environment." src="https://lh3.googleusercontent.com/aida-public/AB6AXuCq7OvFhg969eJwOn-I8HpYPA6LpvRFnfB75MI4swt316Jpu1zSIGwbi7s5ojK-R2FOPW3Kl8ReQnxUIv1A00UqSLcdEiAMUOsJ4SPD7Vns06RvsEvFaOVdNuIeOIO0XCHmtVd_-fdRdSjv7K1-1cbRdY4wIjSWv4-4ogRzwyqpbSXx8fjo9M-YkwO8w7A1y4i9rGNoKzWXQi6GQDsV1ADXTlcTbii1FFBajJoC93Huc-_QyjAdQWG5l11Ue3LMANo7IVo8zTUfTKgB"/>
<div>
<div class="font-label-md text-label-md text-on-surface">Mia</div>
<div class="font-caption text-caption text-on-surface-variant">HC-2024-112</div>
</div>
</div>
<span class="material-symbols-outlined text-outline">chevron_right</span>
</div>
</div>
</div>
</div>
</div>
</main>
</div>
</body></html>

CUATRO DUEÑO DE LA MASCOTA (CLIENTE)
<!DOCTYPE html>

<html lang="es"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Huellitas Alegres - Dashboard de Dueño</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&amp;family=Manrope:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "surface-container-low": "#f3f4f5",
                        "secondary": "#625e56",
                        "surface": "#f8f9fa",
                        "tertiary-fixed": "#d9eaa3",
                        "on-tertiary": "#ffffff",
                        "secondary-container": "#e6dfd5",
                        "on-background": "#191c1d",
                        "on-primary-container": "#ccf0cc",
                        "on-secondary": "#ffffff",
                        "outline-variant": "#c2c8bf",
                        "surface-container-lowest": "#ffffff",
                        "error-container": "#ffdad6",
                        "surface-container-high": "#e7e8e9",
                        "secondary-fixed-dim": "#cdc5bc",
                        "secondary-fixed": "#e9e1d8",
                        "surface-bright": "#f8f9fa",
                        "on-primary-fixed-variant": "#2f4e33",
                        "tertiary": "#47541d",
                        "tertiary-container": "#5e6d33",
                        "primary-fixed": "#c8ecc8",
                        "primary-fixed-dim": "#acd0ad",
                        "on-tertiary-fixed-variant": "#3e4c16",
                        "outline": "#737971",
                        "on-secondary-container": "#67625a",
                        "on-surface-variant": "#424841",
                        "surface-container-highest": "#e1e3e4",
                        "surface-variant": "#e1e3e4",
                        "on-surface": "#191c1d",
                        "on-primary-fixed": "#03210b",
                        "background": "#f8f9fa",
                        "surface-container": "#edeeef",
                        "on-primary": "#ffffff",
                        "inverse-surface": "#2e3132",
                        "on-secondary-fixed": "#1e1b15",
                        "on-tertiary-fixed": "#161f00",
                        "inverse-primary": "#acd0ad",
                        "surface-tint": "#466649",
                        "error": "#ba1a1a",
                        "tertiary-fixed-dim": "#bdce89",
                        "surface-dim": "#d9dadb",
                        "primary-container": "#4f6f52",
                        "on-error": "#ffffff",
                        "on-secondary-fixed-variant": "#4a463f",
                        "primary": "#37563b",
                        "on-error-container": "#93000a",
                        "inverse-on-surface": "#f0f1f2",
                        "on-tertiary-container": "#ddeea7"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                    "spacing": {
                        "base": "8px",
                        "xl": "80px",
                        "margin-desktop": "40px",
                        "md": "24px",
                        "lg": "48px",
                        "margin-mobile": "16px",
                        "gutter": "24px",
                        "xs": "4px",
                        "sm": "12px"
                    },
                    "fontFamily": {
                        "label-md": ["Manrope"],
                        "headline-lg-mobile": ["Plus Jakarta Sans"],
                        "headline-md": ["Plus Jakarta Sans"],
                        "caption": ["Manrope"],
                        "headline-lg": ["Plus Jakarta Sans"],
                        "body-lg": ["Manrope"],
                        "body-md": ["Manrope"],
                        "display-lg": ["Plus Jakarta Sans"]
                    },
                    "fontSize": {
                        "label-md": ["14px", { "lineHeight": "1.2", "letterSpacing": "0.01em", "fontWeight": "600" }],
                        "headline-lg-mobile": ["28px", { "lineHeight": "1.3", "fontWeight": "600" }],
                        "headline-md": ["24px", { "lineHeight": "1.4", "fontWeight": "600" }],
                        "caption": ["12px", { "lineHeight": "1.2", "fontWeight": "500" }],
                        "headline-lg": ["32px", { "lineHeight": "1.3", "fontWeight": "600" }],
                        "body-lg": ["18px", { "lineHeight": "1.6", "fontWeight": "400" }],
                        "body-md": ["16px", { "lineHeight": "1.6", "fontWeight": "400" }],
                        "display-lg": ["48px", { "lineHeight": "1.2", "letterSpacing": "-0.02em", "fontWeight": "700" }]
                    }
                }
            }
        }
    </script>
<style>
        body { background-color: #f8f9fa; }
        .bento-shadow { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); }
    </style>
</head>
<body class="font-body-md text-on-surface bg-background">
<!-- SideNavBar Component -->
<aside class="hidden md:flex flex-col h-screen w-[280px] fixed left-0 top-0 bg-surface-container-low border-r border-outline-variant/20 p-md gap-base z-50">
<div class="mb-lg">
<h1 class="font-headline-md text-headline-md text-primary font-bold">Huellitas Alegres</h1>
<p class="font-caption text-caption text-secondary mt-xs">Portal Administrativo</p>
</div>
<nav class="flex-1 flex flex-col gap-base">
<!-- Active Tab -->
<a class="bg-primary-container text-on-primary-container rounded-lg font-label-md text-label-md font-bold flex items-center gap-3 px-4 py-3" href="#">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">dashboard</span>
                Dashboard
            </a>
<!-- Inactive Tabs -->
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">calendar_today</span>
                Citas
            </a>
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">pets</span>
                Pacientes
            </a>
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">inventory_2</span>
                Inventario
            </a>
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">payments</span>
                Finanzas
            </a>
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">settings</span>
                Configuración
            </a>
</nav>
<div class="mt-auto flex flex-col gap-base">
<button class="bg-primary text-on-primary font-label-md text-label-md rounded-lg py-3 w-full text-center hover:opacity-80 transition-all">Nueva Cita</button>
<div class="pt-base border-t border-outline-variant/20 flex flex-col gap-base">
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">help</span>
                    Ayuda
                </a>
<a class="text-secondary hover:bg-surface-container-high rounded-lg font-label-md text-label-md flex items-center gap-3 px-4 py-3 transition-colors" href="#">
<span class="material-symbols-outlined">logout</span>
                    Cerrar Sesión
                </a>
</div>
</div>
</aside>
<!-- TopNavBar Component -->
<header class="fixed top-0 w-full md:w-[calc(100%-280px)] md:ml-[280px] bg-surface shadow-sm z-40 flex justify-between items-center px-md py-sm">
<div class="flex items-center gap-sm">
<button class="md:hidden text-on-surface-variant p-2 hover:bg-surface-container rounded-full">
<span class="material-symbols-outlined">menu</span>
</button>
<div class="hidden md:flex items-center bg-surface-container-low rounded-full px-4 py-2 border border-outline-variant/30">
<span class="material-symbols-outlined text-secondary mr-2">search</span>
<input class="bg-transparent border-none focus:ring-0 text-body-md font-body-md placeholder:text-secondary outline-none" placeholder="Buscar mascotas o citas..." type="text"/>
</div>
</div>
<div class="flex items-center gap-base">
<button class="text-on-surface-variant hover:bg-surface-container rounded-full p-2 transition-all">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="text-on-surface-variant hover:bg-surface-container rounded-full p-2 transition-all">
<span class="material-symbols-outlined">chat_bubble</span>
</button>
<button class="text-on-surface-variant hover:bg-surface-container rounded-full p-2 transition-all">
<span class="material-symbols-outlined">account_circle</span>
</button>
<img alt="Admin User" class="w-10 h-10 rounded-full object-cover ml-2 border border-outline-variant/20" data-alt="A close up portrait of a smiling woman with warm lighting, serving as an avatar profile picture for a modern web application dashboard. The setting implies a professional but friendly veterinary or pet care context." src="https://lh3.googleusercontent.com/aida-public/AB6AXuAoO-aycp7IGnhKkclXmuk4f3JVDo7rHLXWnjoV6rsC74n2_dw5GZT3QPk_ZywH5LzDEEAmmk6mnQhIj2viIDF483SldWrLS_l3bWJLocc2SMTa2som6WLGKvp8IxPrQ6HqZc7s5pXZe8MwXdfe24s-LjPasjN611O71fQuWq_nZ_yGdXM9P07eLqJmbFMfArjxPFzgA310Yk7ajk954ZlluBksfoR6MnrCznmExOwRKYccm0a_ybFstdrh_4rAh1-AR9AkYHxataNT"/>
</div>
</header>
<!-- Main Content Canvas -->
<main class="ml-0 md:ml-[280px] pt-[80px] p-md md:p-lg max-w-[1440px] mx-auto flex flex-col gap-lg">
<header>
<h2 class="font-headline-lg text-headline-lg text-on-surface">Hola, María</h2>
<p class="font-body-lg text-body-lg text-secondary mt-xs">Aquí está el resumen del bienestar de tus mascotas hoy.</p>
</header>
<!-- Bento Grid Layout -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
<!-- My Pets Cards (Span 2 columns) -->
<div class="lg:col-span-2 flex flex-col gap-md">
<h3 class="font-headline-md text-headline-md text-on-surface">Mis Mascotas</h3>
<div class="grid grid-cols-1 md:grid-cols-2 gap-md">
<!-- Pet Card 1 -->
<div class="bg-surface-container-lowest rounded-xl p-md bento-shadow border border-outline-variant/10 flex items-start gap-md">
<img alt="Max" class="w-20 h-20 rounded-lg object-cover" data-alt="A bright, high-quality portrait of a Golden Retriever looking happy and healthy in a well-lit indoor environment with a soft, neutral background, suitable for a premium pet care app profile picture." src="https://lh3.googleusercontent.com/aida-public/AB6AXuC0J5xV7k0TVnBi1FPDZ7t_EQok6hgtE1ZSSo5g8wQaB6zQzpxwajVtWnoSI1A8j5vadSRqFINhd6LNQxJYpU6S1maZ5v0SXfN9hjW1fundKRUaJZxM-s5ZeVKp3Oa_OYusCYjY-Lp-SU2Mbof-Y9YG8vmBf69SeepPvW76pdDrpKBswaSziQNzVbsS78vaGICwpVgsmobUKvW6TLo2ZEelxZmASBb3ufKkq6SZLaTAWB30-hUDsrft5sPGnpgQzPVqmt5g7odePLdY"/>
<div class="flex-1">
<div class="flex justify-between items-start">
<div>
<h4 class="font-headline-md text-headline-md text-on-surface">Max</h4>
<p class="font-body-md text-body-md text-secondary">Golden Retriever • 3 años</p>
</div>
<span class="bg-tertiary-container text-on-tertiary-container font-caption text-caption px-2 py-1 rounded-full flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">check_circle</span> Sano
                                </span>
</div>
<div class="mt-sm flex gap-sm">
<button class="font-label-md text-label-md text-primary hover:bg-surface-container px-3 py-1 rounded-md transition-colors">Ver Perfil</button>
</div>
</div>
</div>
<!-- Pet Card 2 -->
<div class="bg-surface-container-lowest rounded-xl p-md bento-shadow border border-outline-variant/10 flex items-start gap-md">
<img alt="Luna" class="w-20 h-20 rounded-lg object-cover" data-alt="A clean, sharp portrait of a relaxed tabby cat sitting calmly, illuminated by soft natural light against a minimalist background, intended for a user profile in a modern veterinary dashboard." src="https://lh3.googleusercontent.com/aida-public/AB6AXuDr00doZ7iI9gAPw7EZ5d35LV1K30G1llqk2nkz4DnU2LgNskXtYVYKGHKrBHgqb85759HMZ3ZXKJz7IxCW1_kq_tWpH4d2gGBb1lQ3-Krtu8gYMuuY27Cw1XL--KmtKUsPRS21gOfIjsyK26tgUL2O4oz24LecG2kDAbp3Ttg1sp93r6Imw86AskcA58cFOQ_USyzF7lw38km0YupNY6R_hq7jXyGlGZCWLyeCZiix8uCAsTC91qRkRgiZ6TMjEfg9zVQDCTn_Bban"/>
<div class="flex-1">
<div class="flex justify-between items-start">
<div>
<h4 class="font-headline-md text-headline-md text-on-surface">Luna</h4>
<p class="font-body-md text-body-md text-secondary">Gato Tabby • 1 año</p>
</div>
<span class="bg-surface-variant text-on-surface-variant font-caption text-caption px-2 py-1 rounded-full flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">info</span> Tratamiento
                                </span>
</div>
<div class="mt-sm flex gap-sm">
<button class="font-label-md text-label-md text-primary hover:bg-surface-container px-3 py-1 rounded-md transition-colors">Ver Perfil</button>
</div>
</div>
</div>
</div>
</div>
<!-- Vaccination Reminders (Span 1 column) -->
<div class="lg:col-span-1 flex flex-col gap-md">
<h3 class="font-headline-md text-headline-md text-on-surface">Recordatorios</h3>
<div class="bg-surface-container-lowest rounded-xl p-md bento-shadow border border-outline-variant/10 h-full">
<ul class="flex flex-col gap-sm">
<li class="flex items-center gap-3 p-3 bg-surface rounded-lg border border-outline-variant/20">
<div class="bg-error-container text-on-error-container p-2 rounded-full flex items-center justify-center">
<span class="material-symbols-outlined">vaccines</span>
</div>
<div class="flex-1">
<p class="font-label-md text-label-md text-on-surface">Rabia - Max</p>
<p class="font-caption text-caption text-error">Vence en 5 días</p>
</div>
</li>
<li class="flex items-center gap-3 p-3 bg-surface rounded-lg border border-outline-variant/20">
<div class="bg-secondary-container text-on-secondary-container p-2 rounded-full flex items-center justify-center">
<span class="material-symbols-outlined">medication</span>
</div>
<div class="flex-1">
<p class="font-label-md text-label-md text-on-surface">Desparasitación - Luna</p>
<p class="font-caption text-caption text-secondary">En 2 semanas</p>
</div>
</li>
</ul>
</div>
</div>
</div>
<!-- Secondary Section -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-gutter mt-md">
<!-- Upcoming Appointment -->
<div class="bg-surface-container-lowest rounded-xl p-md bento-shadow border border-outline-variant/10">
<div class="flex justify-between items-center mb-md">
<h3 class="font-headline-md text-headline-md text-on-surface">Próxima Cita</h3>
<span class="material-symbols-outlined text-secondary">more_horiz</span>
</div>
<div class="flex items-start gap-md">
<div class="bg-primary-container text-on-primary-container rounded-lg p-3 text-center min-w-[80px]">
<p class="font-label-md text-label-md">OCT</p>
<p class="font-headline-lg text-headline-lg font-bold">24</p>
</div>
<div>
<h4 class="font-headline-md text-headline-md text-on-surface">Chequeo General - Max</h4>
<p class="font-body-md text-body-md text-secondary mt-xs flex items-center gap-1">
<span class="material-symbols-outlined text-[18px]">schedule</span> 10:30 AM - Dra. Ramírez
                        </p>
<p class="font-body-md text-body-md text-secondary flex items-center gap-1">
<span class="material-symbols-outlined text-[18px]">location_on</span> Clínica Central
                        </p>
</div>
</div>
<div class="mt-md pt-md border-t border-outline-variant/20 flex gap-sm justify-end">
<button class="bg-transparent border border-outline-variant text-primary font-label-md text-label-md px-4 py-2 rounded-lg hover:bg-surface-container transition-colors">Reprogramar</button>
<button class="bg-primary text-on-primary font-label-md text-label-md px-4 py-2 rounded-lg hover:opacity-90 transition-opacity">Confirmar</button>
</div>
</div>
<!-- Health Records Summary -->
<div class="bg-surface-container-lowest rounded-xl p-md bento-shadow border border-outline-variant/10">
<h3 class="font-headline-md text-headline-md text-on-surface mb-md">Historial Médico Reciente</h3>
<div class="overflow-x-auto">
<table class="w-full text-left font-body-md text-body-md">
<thead>
<tr class="text-secondary font-label-md text-label-md border-b border-outline-variant/20">
<th class="pb-2 font-normal">Fecha</th>
<th class="pb-2 font-normal">Mascota</th>
<th class="pb-2 font-normal">Tipo</th>
<th class="pb-2 text-right font-normal">Acción</th>
</tr>
</thead>
<tbody>
<tr class="border-b border-outline-variant/10 hover:bg-surface transition-colors">
<td class="py-3">12 Sep 2023</td>
<td class="py-3">Luna</td>
<td class="py-3">Vacunación</td>
<td class="py-3 text-right">
<button class="text-primary hover:text-primary-container"><span class="material-symbols-outlined">download</span></button>
</td>
</tr>
<tr class="hover:bg-surface transition-colors">
<td class="py-3">05 Ago 2023</td>
<td class="py-3">Max</td>
<td class="py-3">Examen Sangre</td>
<td class="py-3 text-right">
<button class="text-primary hover:text-primary-container"><span class="material-symbols-outlined">visibility</span></button>
</td>
</tr>
</tbody>
</table>
</div>
</div>
</div>
</main>
</body></html>

CINCO DASHBOARD DOMICILIARIO
<!DOCTYPE html>

<html lang="es"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Dashboard Repartidor - Huellitas Alegres</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&amp;family=Manrope:wght@400;500;600&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "background": "#f8f9fa",
                        "surface-container": "#edeeef",
                        "on-primary": "#ffffff",
                        "inverse-surface": "#2e3132",
                        "on-secondary-fixed": "#1e1b15",
                        "on-tertiary-fixed": "#161f00",
                        "surface-tint": "#466649",
                        "inverse-primary": "#acd0ad",
                        "tertiary-fixed-dim": "#bdce89",
                        "error": "#ba1a1a",
                        "surface-dim": "#d9dadb",
                        "primary-container": "#4f6f52",
                        "on-secondary-fixed-variant": "#4a463f",
                        "on-error": "#ffffff",
                        "primary": "#37563b",
                        "on-error-container": "#93000a",
                        "inverse-on-surface": "#f0f1f2",
                        "on-tertiary-container": "#ddeea7",
                        "surface-container-low": "#f3f4f5",
                        "secondary": "#625e56",
                        "tertiary-fixed": "#d9eaa3",
                        "surface": "#f8f9fa",
                        "on-tertiary": "#ffffff",
                        "secondary-container": "#e6dfd5",
                        "on-secondary": "#ffffff",
                        "on-primary-container": "#ccf0cc",
                        "on-background": "#191c1d",
                        "surface-container-lowest": "#ffffff",
                        "outline-variant": "#c2c8bf",
                        "error-container": "#ffdad6",
                        "surface-container-high": "#e7e8e9",
                        "surface-bright": "#f8f9fa",
                        "secondary-fixed-dim": "#cdc5bc",
                        "secondary-fixed": "#e9e1d8",
                        "on-primary-fixed-variant": "#2f4e33",
                        "tertiary": "#47541d",
                        "tertiary-container": "#5e6d33",
                        "primary-fixed": "#c8ecc8",
                        "primary-fixed-dim": "#acd0ad",
                        "outline": "#737971",
                        "on-tertiary-fixed-variant": "#3e4c16",
                        "on-secondary-container": "#67625a",
                        "on-surface-variant": "#424841",
                        "surface-variant": "#e1e3e4",
                        "surface-container-highest": "#e1e3e4",
                        "on-surface": "#191c1d",
                        "on-primary-fixed": "#03210b"
                    },
                    "borderRadius": {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                    "spacing": {
                        "xl": "80px",
                        "margin-desktop": "40px",
                        "base": "8px",
                        "sm": "12px",
                        "xs": "4px",
                        "gutter": "24px",
                        "margin-mobile": "16px",
                        "lg": "48px",
                        "md": "24px"
                    },
                    "fontFamily": {
                        "body-md": ["Manrope"],
                        "body-lg": ["Manrope"],
                        "display-lg": ["Plus Jakarta Sans"],
                        "label-md": ["Manrope"],
                        "headline-lg-mobile": ["Plus Jakarta Sans"],
                        "headline-md": ["Plus Jakarta Sans"],
                        "headline-lg": ["Plus Jakarta Sans"],
                        "caption": ["Manrope"]
                    },
                    "fontSize": {
                        "body-md": ["16px", { "lineHeight": "1.6", "fontWeight": "400" }],
                        "body-lg": ["18px", { "lineHeight": "1.6", "fontWeight": "400" }],
                        "display-lg": ["48px", { "lineHeight": "1.2", "letterSpacing": "-0.02em", "fontWeight": "700" }],
                        "label-md": ["14px", { "lineHeight": "1.2", "letterSpacing": "0.01em", "fontWeight": "600" }],
                        "headline-lg-mobile": ["28px", { "lineHeight": "1.3", "fontWeight": "600" }],
                        "headline-md": ["24px", { "lineHeight": "1.4", "fontWeight": "600" }],
                        "headline-lg": ["32px", { "lineHeight": "1.3", "fontWeight": "600" }],
                        "caption": ["12px", { "lineHeight": "1.2", "fontWeight": "500" }]
                    }
                }
            }
        }
    </script>
<style>
        .shadow-level-1 { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); }
        .shadow-level-2 { box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08); }
    </style>
</head>
<body class="bg-background text-on-background font-body-md min-h-screen flex">
<!-- SideNavBar -->
<nav class="h-screen w-[280px] fixed left-0 top-0 bg-surface-container-low dark:bg-surface-container-lowest border-r border-outline-variant/20 flex flex-col p-md gap-base z-40 hidden md:flex">
<div class="mb-lg">
<h1 class="font-headline-md text-headline-md text-primary dark:text-primary-fixed font-bold">Huellitas Alegres</h1>
<p class="font-label-md text-label-md text-secondary mt-1">Portal Administrativo</p>
</div>
<div class="flex-1 flex flex-col gap-2">
<a class="bg-primary-container dark:bg-primary-fixed-dim text-on-primary-container dark:text-on-primary-fixed rounded-lg font-bold flex items-center gap-3 px-4 py-3 translate-x-1 transition-transform" href="#">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">dashboard</span>
<span class="font-label-md text-label-md">Dashboard</span>
</a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">calendar_today</span>
<span class="font-label-md text-label-md">Citas</span>
</a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">pets</span>
<span class="font-label-md text-label-md">Pacientes</span>
</a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">inventory_2</span>
<span class="font-label-md text-label-md">Inventario</span>
</a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">payments</span>
<span class="font-label-md text-label-md">Finanzas</span>
</a>
<a class="text-secondary dark:text-secondary-fixed-dim hover:bg-secondary-container/50 dark:hover:bg-secondary-fixed/10 rounded-lg flex items-center gap-3 px-4 py-3 transition-colors hover:bg-surface-container-high dark:hover:bg-surface-container-highest transition-all" href="#">
<span class="material-symbols-outlined">settings</span>
<span class="font-label-md text-label-md">Configuración</span>
</a>
</div>
<div class="mt-auto flex flex-col gap-2 pt-md border-t border-outline-variant/20">
<button class="bg-primary hover:opacity-80 text-on-primary font-label-md text-label-md py-3 px-4 rounded-lg flex justify-center items-center gap-2 transition-all w-full mb-4">
<span class="material-symbols-outlined">add</span>
                Nueva Cita
            </button>
<a class="text-secondary hover:bg-surface-container-high rounded-lg flex items-center gap-3 px-4 py-2 transition-colors" href="#">
<span class="material-symbols-outlined">help</span>
<span class="font-label-md text-label-md">Ayuda</span>
</a>
<a class="text-secondary hover:bg-surface-container-high rounded-lg flex items-center gap-3 px-4 py-2 transition-colors" href="#">
<span class="material-symbols-outlined">logout</span>
<span class="font-label-md text-label-md">Cerrar Sesión</span>
</a>
</div>
</nav>
<!-- Main Content Area -->
<div class="flex-1 md:ml-[280px] w-full max-w-[1440px] mx-auto pb-xl">
<!-- TopNavBar -->
<header class="flex justify-between items-center px-md py-sm w-full bg-surface dark:bg-surface-dim shadow-sm sticky top-0 z-30">
<div class="flex items-center gap-4">
<button class="md:hidden text-on-surface hover:bg-surface-container rounded-full p-2">
<span class="material-symbols-outlined">menu</span>
</button>
<div class="relative hidden sm:block">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
<input class="pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant/50 rounded-lg text-body-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-64 transition-all" placeholder="Buscar entregas..." type="text"/>
</div>
</div>
<div class="flex items-center gap-2">
<button class="text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high rounded-full p-2 transition-all relative">
<span class="material-symbols-outlined">notifications</span>
<span class="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>
</button>
<button class="text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high rounded-full p-2 transition-all">
<span class="material-symbols-outlined">chat_bubble</span>
</button>
<div class="ml-2 pl-4 border-l border-outline-variant/30 flex items-center gap-3">
<div class="hidden sm:block text-right">
<p class="font-label-md text-label-md text-on-surface">Carlos D.</p>
<p class="font-caption text-caption text-secondary">Repartidor</p>
</div>
<img alt="Profile" class="w-10 h-10 rounded-full object-cover border border-outline-variant/30" data-alt="A professional headshot of a friendly delivery driver in a modern, well-lit studio setting. The lighting is bright and clean, emphasizing a warm and trustworthy expression. The background is a soft, minimalist grey, maintaining a high-end startup aesthetic. The color palette focuses on natural skin tones and a subtle hint of sage green in the attire." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBczh5mylcdpTrHjQmllK2B0_HaQPpwZ24tWKC9jZ4Ybo3LEMguoky6xbw5GX3dG2TTwrp7V4KsRmmaisarJmA_x0HjsBUbWQBdoPZROQJ8CvL7omMKM1IQng2qZbUYhhxkB2jfS7Um3JRbRSzxMDUFwIK-s26briVCA1xb1qGCtb0ncmSZOJWUj0rHBFw0kEQAfYF0oyPdROlrzb2MsafnA2SiTo3zhPWvC0f8br2B_hf5gkB28aW17aUZ62CcWFjmcedwRIil6pn9"/>
</div>
</div>
</header>
<main class="p-margin-mobile md:p-margin-desktop space-y-gutter">
<!-- Page Header -->
<div class="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
<div>
<h2 class="font-headline-lg-mobile md:font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-1">Ruta de Hoy</h2>
<p class="font-body-md text-body-md text-secondary">Martes, 24 de Octubre • 8 Paradas Pendientes</p>
</div>
<button class="bg-error-container text-on-error-container hover:opacity-90 font-label-md text-label-md py-2 px-4 rounded-lg flex items-center gap-2 transition-all">
<span class="material-symbols-outlined">warning</span>
                    Reportar Incidente
                </button>
</div>
<!-- Stats Overview Bento -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
<div class="bg-surface-container-lowest rounded-xl p-md shadow-level-1 border border-outline-variant/20 flex items-center gap-4">
<div class="w-12 h-12 rounded-full bg-primary-container/20 flex items-center justify-center text-primary">
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">local_shipping</span>
</div>
<div>
<p class="font-caption text-caption text-secondary uppercase tracking-wide">En Tránsito</p>
<p class="font-headline-md text-headline-md text-on-surface">3</p>
</div>
</div>
<div class="bg-surface-container-lowest rounded-xl p-md shadow-level-1 border border-outline-variant/20 flex items-center gap-4">
<div class="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center text-on-surface-variant">
<span class="material-symbols-outlined">check_circle</span>
</div>
<div>
<p class="font-caption text-caption text-secondary uppercase tracking-wide">Completados</p>
<p class="font-headline-md text-headline-md text-on-surface">12</p>
</div>
</div>
<div class="bg-surface-container-lowest rounded-xl p-md shadow-level-1 border border-outline-variant/20 flex items-center gap-4">
<div class="w-12 h-12 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container">
<span class="material-symbols-outlined">schedule</span>
</div>
<div>
<p class="font-caption text-caption text-secondary uppercase tracking-wide">Pendientes</p>
<p class="font-headline-md text-headline-md text-on-surface">8</p>
</div>
</div>
</div>
<!-- Main Layout Grid -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
<!-- Active Route Details (Left 2 Columns) -->
<div class="lg:col-span-2 space-y-gutter">
<!-- Map Card -->
<div class="bg-surface-container-lowest rounded-xl shadow-level-1 border border-outline-variant/20 overflow-hidden flex flex-col h-[400px]">
<div class="p-4 border-b border-outline-variant/20 bg-surface flex justify-between items-center">
<h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wide">Mapa de Ruta</h3>
<button class="text-primary hover:bg-primary-container/10 font-label-md text-label-md py-1 px-3 rounded transition-colors flex items-center gap-1">
<span class="material-symbols-outlined text-sm">directions</span>
                                Optimizar Ruta
                            </button>
</div>
<div class="flex-1 relative bg-surface-container">
<img alt="Map View" class="w-full h-full object-cover" data-alt="A clean, highly stylized top-down digital map interface showing a city grid. The map uses a very light, minimalist color scheme primarily featuring soft greys, bone white, and subtle sage green path lines indicating a delivery route. Small, elegant circular markers denote delivery stops. The aesthetic is modern, clean, and resembles a premium startup dashboard map view." src="https://lh3.googleusercontent.com/aida-public/AB6AXuCs47ppa5HG_mSpWW-IRq7WVW3AVPSIQb15LxaBy8OBJS22TesxlXpbUWnhD2nonvCxROWERPbIPAlC4VtjRFjfsyxnLn4_ReqxOFFRE5zO7lfOVZXlkQ5jvIAJ_AkPExmX88tBuDiSMQ4sg7Tc5pdAzMOokB1olstY3bNtRfiExrLBMy_eF2IYaHiQhsFVmMpEgyZBrZta1V0lUfIDNNHRygWk3VuFgOpRv_RNCwsYF3Ng8O0L4IlQlPOUM9zZzWKd-DAlHc0f8eYj"/>
<!-- Overlay Current Delivery Info -->
<div class="absolute bottom-4 left-4 right-4 bg-surface-container-lowest/90 backdrop-blur-md p-4 rounded-lg shadow-level-2 border border-outline-variant/30 flex items-center justify-between">
<div class="flex items-center gap-3">
<div class="bg-primary text-on-primary w-10 h-10 rounded-full flex items-center justify-center font-bold font-label-md">1</div>
<div>
<p class="font-label-md text-label-md text-on-surface">Entrega a Domicilio: Luna (Golden Retriever)</p>
<p class="font-caption text-caption text-secondary">Av. Siempreviva 742 • A 5 min</p>
</div>
</div>
<button class="bg-primary hover:opacity-90 text-on-primary rounded-lg p-2 transition-all">
<span class="material-symbols-outlined">navigation</span>
</button>
</div>
</div>
</div>
<!-- Delivery List -->
<div class="bg-surface-container-lowest rounded-xl shadow-level-1 border border-outline-variant/20">
<div class="p-md border-b border-outline-variant/20">
<h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wide">Paradas Pendientes</h3>
</div>
<div class="divide-y divide-outline-variant/20">
<!-- Stop 1 -->
<div class="p-md hover:bg-surface-container-low transition-colors flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
<div class="flex gap-4">
<div class="flex flex-col items-center">
<div class="w-8 h-8 rounded-full border-2 border-primary text-primary flex items-center justify-center font-bold text-sm bg-primary-container/10">1</div>
<div class="w-0.5 h-full bg-outline-variant/30 my-1"></div>
</div>
<div>
<div class="flex items-center gap-2 mb-1">
<span class="bg-primary-container text-on-primary-fixed-variant px-2 py-0.5 rounded-full font-caption text-caption">Medicamento</span>
<span class="bg-error-container text-on-error-container px-2 py-0.5 rounded-full font-caption text-caption">Alta Prioridad</span>
</div>
<p class="font-label-md text-label-md text-on-surface">Luna (Golden Retriever)</p>
<p class="font-body-md text-body-md text-secondary">Av. Siempreviva 742, Depto 3B</p>
<p class="font-caption text-caption text-secondary mt-1 flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">phone</span> +56 9 8765 4321
                                        </p>
</div>
</div>
<div class="flex flex-row sm:flex-col gap-2 w-full sm:w-auto">
<button class="flex-1 sm:flex-none bg-primary hover:opacity-90 text-on-primary font-label-md text-label-md py-2 px-4 rounded-lg transition-all text-center">
                                        Entregar
                                    </button>
<button class="flex-1 sm:flex-none bg-surface border border-outline-variant hover:border-primary text-primary font-label-md text-label-md py-2 px-4 rounded-lg transition-all text-center">
                                        Detalles
                                    </button>
</div>
</div>
<!-- Stop 2 -->
<div class="p-md hover:bg-surface-container-low transition-colors flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
<div class="flex gap-4">
<div class="flex flex-col items-center">
<div class="w-8 h-8 rounded-full border-2 border-outline text-secondary flex items-center justify-center font-bold text-sm">2</div>
<div class="w-0.5 h-full bg-outline-variant/30 my-1"></div>
</div>
<div>
<div class="flex items-center gap-2 mb-1">
<span class="bg-tertiary-container text-on-tertiary-container px-2 py-0.5 rounded-full font-caption text-caption">Alimento Clínico</span>
</div>
<p class="font-label-md text-label-md text-on-surface">Max (Bulldog Francés)</p>
<p class="font-body-md text-body-md text-secondary">Calle Los Leones 1234, Casa 5</p>
</div>
</div>
<div class="flex gap-2 w-full sm:w-auto opacity-50 pointer-events-none">
<button class="bg-surface border border-outline-variant text-secondary font-label-md text-label-md py-2 px-4 rounded-lg transition-all text-center">
                                        Entregar
                                    </button>
</div>
</div>
<!-- Stop 3 -->
<div class="p-md hover:bg-surface-container-low transition-colors flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
<div class="flex gap-4">
<div class="flex flex-col items-center">
<div class="w-8 h-8 rounded-full border-2 border-outline text-secondary flex items-center justify-center font-bold text-sm">3</div>
</div>
<div>
<div class="flex items-center gap-2 mb-1">
<span class="bg-secondary-container text-on-secondary-container px-2 py-0.5 rounded-full font-caption text-caption">Taxi Pet (Recogida)</span>
</div>
<p class="font-label-md text-label-md text-on-surface">Bella (Siamesa)</p>
<p class="font-body-md text-body-md text-secondary">Av. Providencia 456, Of 102</p>
</div>
</div>
<div class="flex gap-2 w-full sm:w-auto opacity-50 pointer-events-none">
<button class="bg-surface border border-outline-variant text-secondary font-label-md text-label-md py-2 px-4 rounded-lg transition-all text-center">
                                        Entregar
                                    </button>
</div>
</div>
</div>
</div>
</div>
<!-- Action Panel (Right Column) -->
<div class="space-y-gutter">
<!-- Quick Actions -->
<div class="bg-surface-container-lowest rounded-xl shadow-level-1 border border-outline-variant/20 p-md">
<h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wide mb-4">Acciones Rápidas</h3>
<div class="grid grid-cols-2 gap-3">
<button class="bg-surface-container hover:bg-surface-container-high text-on-surface rounded-lg p-3 flex flex-col items-center justify-center gap-2 transition-colors border border-outline-variant/30">
<span class="material-symbols-outlined text-primary">qr_code_scanner</span>
<span class="font-caption text-caption text-center">Escanear Paquete</span>
</button>
<button class="bg-surface-container hover:bg-surface-container-high text-on-surface rounded-lg p-3 flex flex-col items-center justify-center gap-2 transition-colors border border-outline-variant/30">
<span class="material-symbols-outlined text-primary">add_photo_alternate</span>
<span class="font-caption text-caption text-center">Foto Entrega</span>
</button>
<button class="bg-surface-container hover:bg-surface-container-high text-on-surface rounded-lg p-3 flex flex-col items-center justify-center gap-2 transition-colors border border-outline-variant/30">
<span class="material-symbols-outlined text-primary">support_agent</span>
<span class="font-caption text-caption text-center">Llamar Central</span>
</button>
<button class="bg-surface-container hover:bg-surface-container-high text-on-surface rounded-lg p-3 flex flex-col items-center justify-center gap-2 transition-colors border border-outline-variant/30">
<span class="material-symbols-outlined text-primary">local_gas_station</span>
<span class="font-caption text-caption text-center">Reportar Gasto</span>
</button>
</div>
</div>
<!-- Vehicle Status Card -->
<div class="bg-surface-container-lowest rounded-xl shadow-level-1 border border-outline-variant/20 p-md relative overflow-hidden">
<div class="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-full -z-10"></div>
<h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wide mb-4">Estado del Vehículo</h3>
<div class="flex items-center gap-4 mb-4">
<div class="w-12 h-12 bg-secondary-container rounded-lg flex items-center justify-center">
<span class="material-symbols-outlined text-on-secondary-container">directions_car</span>
</div>
<div>
<p class="font-label-md text-label-md text-on-surface">Van Citroen Berlingo</p>
<p class="font-caption text-caption text-secondary">Patente: AB-CD-12</p>
</div>
</div>
<div class="space-y-3">
<div class="flex justify-between items-center text-sm">
<span class="font-body-md text-secondary">Combustible</span>
<span class="font-label-md text-on-surface">75%</span>
</div>
<div class="w-full bg-surface-variant rounded-full h-2">
<div class="bg-primary h-2 rounded-full" style="width: 75%"></div>
</div>
<div class="flex justify-between items-center text-sm pt-2">
<span class="font-body-md text-secondary">Próxima Mantención</span>
<span class="font-label-md text-on-surface text-error">En 200 km</span>
</div>
</div>
</div>
</div>
</div>
</main>
</div>
</body></html>
