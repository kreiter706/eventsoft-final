from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from eventos import views

urlpatterns = [
    path('habilitar-inscripciones/', views.habilitar_inscripciones_eventos, name='habilitar_inscripciones_eventos'),
    path('habilitar-inscripciones/<int:evento_id>/', views.habilitar_inscripciones_rol, name='habilitar_inscripciones_rol'),
    path('proximos/', views.eventos_proximos, name='eventos_proximos'),
    path('buscar/', views.buscar_eventos, name='buscar_eventos'),
    path('detalle/<int:evento_id>/', views.detalle_evento, name='detalle_evento'),
    path('crear/', views.crear_evento, name='crear_evento'),         # HU50
    path('editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),  # HU52
    path('registrarse/<int:evento_id>/', views.registro_visitante_evento, name='registro_visitante_evento'),
    path(
        'registrar-asistente/<int:evento_id>/',
        views.registro_asistente_evento,
        name='registrar_asistente'),
    path('opciones-participacion/<int:evento_id>/', views.opciones_participacion, name='opciones_participacion'),
    path('preinscripcion-participante/<int:evento_id>/', views.preinscripcion_participante, name='preinscripcion_participante'),
    path('descargar-programacion/<int:evento_id>/', views.descargar_programacion_evento, name='descargar_programacion_evento'),
    path('instrumentos/<int:evento_id>/', views.instrumentos_evento, name='instrumentos_evento'),
    path('evaluador/eventos-asignados/', views.eventos_asignados_evaluador, name='eventos_asignados_evaluador'),
    path('evaluador/evento/<int:evento_id>/instrumento/<int:instrumento_id>/items/', views.gestionar_items_instrumento, name='gestionar_items_instrumento'),
    path('evaluador/evento/<int:evento_id>/instrumento/<int:instrumento_id>/item/<int:item_id>/editar/', views.editar_item_instrumento, name='editar_item_instrumento'),
    path('evaluador/evento/<int:evento_id>/instrumento/<int:instrumento_id>/item/<int:item_id>/eliminar/', views.eliminar_item_instrumento, name='eliminar_item_instrumento'),
    path('evaluador/evento/<int:evento_id>/instrumento/<int:instrumento_id>/calificar/<int:participante_id>/', views.calificar_participante, name='calificar_participante'),
    path('evento/<int:evento_id>/ranking/', views.ranking_evento, name='ranking_evento'),
    path('evento/<int:evento_id>/comparativa/', views.comparativa_calificaciones_evento, name='comparativa_calificaciones_evento'),
    path('admin/evento/<int:evento_id>/instrumento/<int:instrumento_id>/items/', views.gestionar_items_instrumento, name='admin_gestionar_items_instrumento'),
    path('admin/evento/<int:evento_id>/instrumento/crear/', views.admin_crear_instrumento, name='admin_crear_instrumento'),
    path('admin/evento/<int:evento_id>/tabla-posiciones/', views.admin_tabla_posiciones, name='admin_tabla_posiciones'),
    path('memorias/', views.memorias_evento, name='memorias_evento'),
    path('memorias/eliminar/', views.eliminar_memorias, name='eliminar_memorias'),
    path('memorias/descargar/<str:filename>/', views.descargar_memoria, name='descargar_memoria'),
    path('admin/evento/<int:evento_id>/participante/<int:participante_id>/detalle-calificaciones/', views.admin_detalle_calificaciones_participante, name='admin_detalle_calificaciones_participante'),
    path('evento/<int:evento_id>/preinscripcion-evaluador/', views.preinscripcion_evaluador, name='preinscripcion_evaluador'),
    path('evaluador/evento/<int:evento_id>/editar-preinscripcion/', views.editar_preinscripcion_evaluador, name='editar_preinscripcion_evaluador'),
    path('evaluador/evento/<int:evento_id>/cancelar-preinscripcion/', views.cancelar_preinscripcion_evaluador, name='cancelar_preinscripcion_evaluador'),
    path('evento/<int:evento_id>/lista-participantes-evaluador/', views.lista_participantes_evaluador, name='lista_participantes_evaluador'),
    path('evento/<int:evento_id>/participante/<int:participante_id>/detalle/', views.detalle_participante_evaluador, name='detalle_participante_evaluador'),
    path('evento/<int:evento_id>/informacion-tecnica-evaluador/', views.ver_info_tecnica_evaluador, name='ver_info_tecnica_evaluador'),
    path('evento/<int:evento_id>/ver-info-tecnica-evaluador/', views.ver_info_tecnica_evaluador, name='ver_info_tecnica_evaluador'),
    path('evento/<int:evento_id>/informacion-tecnica-evaluador/', views.informacion_tecnica_evaluador, name='informacion_tecnica_evaluador'),
    path('admin/subir-memoria-evento/', views.subir_memoria_evento, name='subir_memoria_evento'),
    path('evento/<int:evento_id>/calificar-participantes/', views.calificar_participantes_evento, name='calificar_participantes_evento'),

    path('descargar-imagen/<int:evento_id>/', views.descargar_imagen, name='descargar_imagen'),
    #----SUPERADMIN ----
    path('superadmin/evento/<int:evento_id>/instrumento/<int:instrumento_id>/items/', views.gestionar_items_instrumento_superadmin, name='superadmin_gestionar_items_instrumento'),
    path('superadmin/evento/<int:evento_id>/instrumento/crear/', views.superadmin_crear_instrumento, name='superadmin_crear_instrumento'),
    path('superadmin/evento/<int:evento_id>/tabla-posiciones/', views.superadmin_tabla_posiciones, name='superadmin_tabla_posiciones'),
    path('superadmin/evento/<int:evento_id>/participante/<int:participante_id>/detalle-calificaciones/', views.superadmin_detalle_calificaciones_participante, name='superadmin_detalle_calificaciones_participante'),
    path('superadmin/evento/<int:evento_id>/instrumento/<int:instrumento_id>/item/<int:item_id>/editar/', views.editar_item_instrumento_superadmin, name='editar_item_instrumento_superadmin'),
    path('superadmin/evento/<int:evento_id>/instrumento/<int:instrumento_id>/item/<int:item_id>/eliminar/', views.eliminar_item_instrumento_superadmin, name='eliminar_item_instrumento_superadmin'),
    path('superadmin/subir-memoria-evento/', views.subir_memoria_evento, name='subir_memoria_evento_superadmin'),
    path('superadmin/editar/<int:evento_id>/', views.editar_evento_superadmin, name='editar_evento_superadmin'),
    path('superadmin/eventos/', views.eventos_lista_superadmin, name='eventos_lista_superadmin'),
    path('superadmin/eventos/<int:evento_id>/aprobar/', views.aprobar_evento, name='aprobar_evento'),
    path('superadmin/eventos/<int:evento_id>/rechazar/', views.rechazar_evento, name='rechazar_evento'),
]




