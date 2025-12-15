

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('superadmin/gestionar-admins/', views.gestionar_admins, name='gestionar_admins'),
    path('superadmin/cambiar-estado-codigo/<int:usuario_id>/', views.cambiar_estado_codigo_acceso, name='cambiar_estado_codigo_acceso'),
    path('login/', views.CustomLoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('debug/auth-check/', views.auth_check, name='auth_check'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('sin-permiso/', views.sin_permiso, name='sin_permiso'),

    # SUPERADMIN (Administrador general del sistema)
    path('superadmin/', views.inicio_superadmin, name='inicio_superadmin'),
    path('superadmin/eventos-cancelacion/', views.eventos_cancelacion_superadmin, name='eventos_cancelacion_superadmin'),
    path('superadmin/lista-eventos-cambiar-participante/', views.lista_eventos_cambiar_participante_superadmin, name='lista_eventos_cambiar_participante_superadmin'),
    path('superadmin/eventos-programacion/', views.eventos_programacion_superadmin, name='eventos_programacion_superadmin'),
    path('superadmin/asistentes-inscritos-todos/', views.asistentes_inscritos_todos_eventos_superadmin, name='asistentes_inscritos_todos_eventos_superadmin'),
    path('superadmin/participantes-preinscritos/<int:evento_id>/', views.participantes_preinscritos_superadmin, name='participantes_preinscritos_superadmin'),
    path('superadmin/programacion-evento/<int:evento_id>/', views.cargar_programacion_evento_superadmin, name='cargar_programacion_evento_superadmin'),
    path('superadmin/asistentes-inscritos/<int:evento_id>/', views.asistentes_inscritos_evento_superadmin, name='asistentes_inscritos_evento_superadmin'),
    path('superadmin/lista-eventos-cambiar-estado/', views.lista_eventos_cambiar_estado_superadmin, name='lista_eventos_cambiar_estado_superadmin'),
    path('superadmin/cambiar-estado-asistente-evento/<int:inscripcion_id>/<str:nuevo_estado>/', views.cambiar_estado_asistente_evento_superadmin, name='cambiar_estado_asistente_evento_superadmin'),
    path('superadmin/estadisticas-asistentes/', views.estadisticas_asistentes_evento_superadmin, name='estadisticas_asistentes_evento_superadmin'),
    path('superadmin/eventos-gestion-instrumentos/', views.eventos_gestion_instrumentos_superadmin, name='eventos_gestion_instrumentos_superadmin'),
    path('superadmin/certificados-evento/<int:evento_id>/', views.superadmin_certificados_evento, name='superadmin_certificados_evento'),
    path('superadmin/configurar-certificados/', views.lista_eventos_configurar_certificados_superadmin, name='lista_eventos_configurar_certificados_superadmin'),
    path('superadmin/configurar-certificados/<int:evento_id>/', views.configurar_certificados_evento_superadmin, name='configurar_certificados_evento_superadmin'),
    path('superadmin/certificados-evento/<int:evento_id>/', views.admin_certificados_evento, name='admin_certificados_evento'),
    path('superadmin/enviar-correos/', views.seleccionar_evento_envio_correo_superadmin, name='seleccionar_evento_envio_correo_superadmin'),
    path('superadmin/enviar-correos/rol/<int:evento_id>/', views.seleccionar_rol_envio_correo_superadmin, name='seleccionar_rol_envio_correo_superadmin'),
    path('superadmin/enviar-correos/usuarios/<int:evento_id>/<str:rol>/', views.seleccionar_usuarios_envio_correo_superadmin, name='seleccionar_usuarios_envio_correo_superadmin'),
    path('superadmin/enviar-correos/rol/<int:evento_id>/todos/', views.enviar_correo_masivo_evento_superadmin, name='enviar_correo_masivo_evento_superadmin'),
    path('superadmin/enviar-correos/redactar/', views.redactar_envio_correo_superadmin, name='redactar_envio_correo_superadmin'),
    path('superadmin/crear-administrador/', views.crear_administrador_superadmin, name='crear_administrador_superadmin'),
    # ADMIN (Administrador de evento)
    path('admin/', views.inicio_admin, name='inicio_admin'),
    path('admin/configurar-certificados/', views.lista_eventos_configurar_certificados, name='lista_eventos_configurar_certificados'),
    path('admin/eventos-cancelacion/', views.eventos_cancelacion_admin, name='eventos_cancelacion_admin'),
    path('admin/cancelar-evento/<int:evento_id>/', views.cancelar_evento, name='cancelar_evento'),
    path('admin/eventos-programacion/', views.eventos_programacion_admin, name='eventos_programacion_admin'),
    path('admin/programacion-evento/<int:evento_id>/', views.cargar_programacion_evento, name='cargar_programacion_evento'),  
    path('admin/estadisticas-asistentes/', views.estadisticas_asistentes_evento, name='estadisticas_asistentes_evento'),
    path('admin/asistentes-inscritos-todos/', views.asistentes_inscritos_todos_eventos, name='asistentes_inscritos_todos_eventos'),
    path('admin/cambiar-estado-asistente/<int:evento_id>/', views.cambiar_estado_asistente, name='cambiar_estado_asistente'),
    path('admin/lista-eventos-cambiar-estado/', views.lista_eventos_cambiar_estado, name='lista_eventos_cambiar_estado'),
    path('admin/asistentes-inscritos/<int:evento_id>/', views.asistentes_inscritos_evento, name='asistentes_inscritos_evento'),
    path('admin/cambiar-estado-asistente-evento/<int:inscripcion_id>/<str:nuevo_estado>/', views.cambiar_estado_asistente_evento, name='cambiar_estado_asistente_evento'),
    path('admin/aprobar-inscripcion-participante/<int:inscripcion_id>/<str:nuevo_estado>/', views.aprobar_inscripcion_participante, name='aprobar_inscripcion_participante'),
    path('admin/eventos-aprobar-participantes/', views.eventos_para_aprobar_participantes, name='eventos_para_aprobar_participantes'),
    path('admin/participantes-preinscritos/<int:evento_id>/', views.participantes_preinscritos_admin, name='participantes_preinscritos_admin'),
    path('admin/lista-eventos-cambiar-participante/', views.lista_eventos_cambiar_participante, name='lista_eventos_cambiar_participante'),
    path('admin/eventos-gestion-instrumentos/', views.eventos_gestion_instrumentos_admin, name='eventos_gestion_instrumentos_admin'),
    path('admin/lista-eventos-evaluadores/', views.lista_eventos_evaluadores, name='lista_eventos_evaluadores'),
    path('admin/aprobar-inscripcion-evaluador/<int:evaluador_evento_id>/<str:nuevo_estado>/', views.aprobar_inscripcion_evaluador, name='aprobar_inscripcion_evaluador'),
    path('admin/evaluadores-preinscritos/<int:evento_id>/', views.evaluadores_preinscritos_admin, name='evaluadores_preinscritos_admin'),

    # Ruta para configurar certificados de un evento específico
    path('admin/configurar-certificados/<int:evento_id>/', views.configurar_certificados_evento, name='configurar_certificados_evento'),
    path('admin/certificados-evento/<int:evento_id>/', views.admin_certificados_evento, name='admin_certificados_evento'),

    # PARTICIPANTE
    path('crear-inscripcion-participante/<int:evento_id>/', views.crear_inscripcion_participante, name='crear_inscripcion_participante'),
    path('editar-preinscripcion/<int:evento_id>/<int:usuario_id>/', views.editar_preinscripcion_participante, name='editar_preinscripcion_participante'),
    path('evento/<int:evento_id>/ver-info-tecnica-participante/', views.ver_info_tecnica_participante, name='ver_info_tecnica_participante'),

    # ASISTENTE
    path('crear-inscripcion-asistente/<int:evento_id>/', views.crear_inscripcion_asistente, name='crear_inscripcion_asistente'),
    path('editar-preinscripcion-asistente/<int:evento_id>/<int:usuario_id>/', views.editar_preinscripcion_asistente, name='editar_preinscripcion_asistente'),
    path('cancelar-preinscripcion-asistente/<int:evento_id>/<int:usuario_id>/', views.cancelar_preinscripcion_asistente, name='cancelar_preinscripcion_asistente'),
    path('descargar-comprobante-asistente/<int:inscripcion_id>/', views.descargar_comprobante_asistente, name='descargar_comprobante_asistente'),
    path('perfil-asistente/', views.perfil_asistente, name='perfil_asistente'),

    path('asistente/', views.inicio_asistente, name='inicio_asistente'),
    path('cancelar-preinscripcion/<int:evento_id>/<int:usuario_id>/', views.cancelar_preinscripcion, name='cancelar_preinscripcion'),
    path('descargar-comprobante/<int:inscripcion_id>/', views.descargar_comprobante, name='descargar_comprobante'),
    path('perfil/', views.perfil_participante, name='perfil_participante'),
    path('ver-evaluaciones/<int:evento_id>/', views.ver_evaluaciones_evento, name='ver_evaluaciones_evento'),

    # EVALUADOR
    path('evaluador/', views.inicio_evaluador, name='inicio_evaluador'),
    path('evaluador/evento/<int:evento_id>/editar/', views.editar_info_evaluador, name='editar_info_evaluador'),
    path('evaluador/evento/<int:evento_id>/comprobante/', views.descargar_comprobante_evaluador, name='descargar_comprobante_evaluador'),
    path('evaluador/evento/<int:evento_id>/detalle/', views.detalle_evento_evaluador, name='detalle_evento_evaluador'),
    path('crear-inscripcion-evaluador/<int:evento_id>/', views.crear_inscripcion_evaluador, name='crear_inscripcion_evaluador'),




    # --- Envío de correos masivos (admin) ---
    path('admin/enviar-correos/', views.seleccionar_evento_envio_correo, name='seleccionar_evento_envio_correo'),
    path('admin/enviar-correos/rol/<int:evento_id>/', views.seleccionar_rol_envio_correo, name='seleccionar_rol_envio_correo'),
    path('admin/enviar-correos/rol/<int:evento_id>/todos/', views.enviar_correo_masivo_evento, name='enviar_correo_masivo_evento'),
    path('admin/enviar-correos/usuarios/<int:evento_id>/<str:rol>/', views.seleccionar_usuarios_envio_correo, name='seleccionar_usuarios_envio_correo'),
    path('admin/enviar-correos/redactar/', views.redactar_envio_correo, name='redactar_envio_correo'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('descargar-certificado-asistente/<int:inscripcion_id>/', views.descargar_certificado_asistente, name='descargar_certificado_asistente'),
    path('descargar-certificado-participante/<int:inscripcion_id>/', views.descargar_certificado_participante, name='descargar_certificado_participante'),
    path('previsualizar-certificado-evento/<int:evento_id>/', views.previsualizar_certificado_evento, name='previsualizar_certificado_evento'),

    path('descargar-imagen/<int:evento_id>/', views.descargar_imagen, name='descargar_imagen'),
    path('editar-cuenta-asistente/', views.editar_cuenta_asistente, name='editar_cuenta_asistente'),
]

