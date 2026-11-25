"""Motor experimental FARO v2: agrega estados explícitos de cobertura integral.

NO extrae productos ni infiere habilidades del cliente; requiere evaluación
por ítem respaldada por evidencias y una lista completa del requerimiento.
No modifica datos ni realiza solicitudes de red.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Afinidad = Literal["directa", "adyacente", "no_relacionada", "indeterminada"]
EstadoItem = Literal[
    "directa", "por_encargo_confirmada", "por_encargo_por_verificar",
    "desconocida", "no_cubierta",
]
Cobertura = Literal["confirmada", "posible_por_verificar", "desconocida", "imposible"]

ESTADOS_VALIDOS = frozenset(
    ("directa", "por_encargo_confirmada", "por_encargo_por_verificar",
     "desconocida", "no_cubierta")
)
AFINIDADES_VALIDAS = frozenset(
    ("directa", "adyacente", "no_relacionada", "indeterminada")
)
VERSION_REGLAS = "faro-v2-exp-0.1"


@dataclass(frozen=True)
class ElementoObligatorio:
    id: str
    descripcion: str
    estado: EstadoItem
    fuente: str
    motivo: str = ""


@dataclass(frozen=True)
class SolicitudEvaluacion:
    codigo: str
    afinidad: Afinidad
    elementos: tuple[ElementoObligatorio, ...]
    requisitos: tuple[ElementoObligatorio, ...] = ()
    detalle_completo: bool = False
    anexos_necesarios_revisados: bool = False
    # Un comprador puede pedir ítems en anexos no reflejados en el JSON.
    evidencia_afinidad: str = ""
    conflicto_unspsc: bool = False


def evaluar(solicitud: SolicitudEvaluacion) -> dict:
    """Resuelve cobertura sobre TODOS los elementos y requisitos obligatorios.

    No se infieren bienes a partir de UNSPSC ni del título. Se exige una ficha
    explícita de todos los requerimientos; en su ausencia hay abstención.
    """
    if not solicitud.codigo.strip():
        raise ValueError("La compra necesita codigo")
    if solicitud.afinidad not in AFINIDADES_VALIDAS:
        raise ValueError("Afinidad no válida")
    todos = (*solicitud.elementos, *solicitud.requisitos)
    ids = [e.id for e in todos]
    if len(ids) != len(set(ids)):
        raise ValueError("Los IDs de elementos y requisitos deben ser únicos")
    if any(not e.id.strip() or not e.descripcion.strip()
           or not e.fuente.strip() for e in todos):
        raise ValueError("Cada elemento requiere id, descripción y fuente")
    if any(e.estado not in ESTADOS_VALIDOS for e in todos):
        raise ValueError("Estado de cobertura no válido")
    if any(e.estado in ("no_cubierta", "por_encargo_confirmada",
                        "por_encargo_por_verificar") and not e.motivo.strip()
           for e in todos):
        raise ValueError("Estados especiales requieren motivo trazable")

    bloqueantes = [e for e in todos if e.estado == "no_cubierta"]
    dudas = [e for e in todos if e.estado in
             ("por_encargo_por_verificar", "desconocida")]

    # Un impedimento probado basta para descartar aunque falten anexos.
    if bloqueantes:
        cobertura: Cobertura = "imposible"
    elif not solicitud.detalle_completo or not solicitud.anexos_necesarios_revisados:
        cobertura = "desconocida"
    elif not solicitud.elementos:
        cobertura = "desconocida"
    elif any(e.estado == "desconocida" for e in todos):
        cobertura = "desconocida"
    elif dudas:
        cobertura = "posible_por_verificar"
    else:
        cobertura = "confirmada"

    if cobertura == "imposible":
        decision = "descartar_no_cotizable"
    elif solicitud.afinidad == "no_relacionada":
        decision = "no_priorizar"
    elif solicitud.afinidad == "indeterminada":
        decision = "pendiente_informacion"
    elif cobertura == "confirmada":
        decision = "recomendable"
    elif cobertura == "posible_por_verificar":
        decision = "consultar_cliente"
    else:
        decision = "pendiente_informacion"

    return {
        "codigo": solicitud.codigo,
        "version_reglas": VERSION_REGLAS,
        "afinidad": solicitud.afinidad,
        "cobertura_integral": cobertura,
        "decision": decision,
        "requiere_revision": (
            decision in ("consultar_cliente", "pendiente_informacion")
            or solicitud.conflicto_unspsc
        ),
        "items_bloqueantes": [
            {"id": e.id, "descripcion": e.descripcion,
             "motivo": e.motivo, "fuente": e.fuente}
            for e in bloqueantes
        ],
        "items_a_confirmar": [
            {"id": e.id, "descripcion": e.descripcion,
             "estado": e.estado, "motivo": e.motivo, "fuente": e.fuente}
            for e in dudas
        ],
        "evidencia_afinidad": solicitud.evidencia_afinidad,
        "conflicto_unspsc": solicitud.conflicto_unspsc,
        "detalle_completo": solicitud.detalle_completo,
        "anexos_necesarios_revisados": solicitud.anexos_necesarios_revisados,
        "elementos_evaluados": len(solicitud.elementos),
        "requisitos_evaluados": len(solicitud.requisitos),
    }
