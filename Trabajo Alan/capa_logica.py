# Capa de lógica de negocio del sistema de venta de boletos

import datetime
import sqlite3
from capa_datos import RepositorioEventos, RepositorioVentas, Evento


class GestorEventos:
    """Gestor para manejar la lógica de negocio de eventos"""
    
    def __init__(self):
        self.repositorio_eventos = RepositorioEventos()

    def crear_evento(
        self,
        nombre: str,
        fecha: str,
        lugar: str,
        precio: float,
        disponibles: int
    ) -> None:
        """Crea un nuevo evento en el sistema"""
        self.repositorio_eventos.insertar_evento(nombre, fecha, lugar, precio, disponibles)

    def obtener_eventos(self) -> list[Evento]:
        """Obtiene todos los eventos del sistema"""
        return self.repositorio_eventos.listar_eventos()


class GestorVentas:
    """Gestor para manejar la lógica de negocio de ventas"""
    
    def __init__(self):
        self.repositorio_eventos = RepositorioEventos()
        self.repositorio_ventas = RepositorioVentas()  

    def vender_boletos(
        self,
        evento_id: int,
        cliente: str,
        gmail: str,
        cantidad: int
    ) -> tuple[bool, str]:
        """Procesa la venta de boletos para un evento"""
        eventos = self.repositorio_eventos.listar_eventos()
        evento = next((evento for evento in eventos if evento.id == evento_id), None)

        if evento is None:
            return False, "Evento no encontrado."

        entradas_restantes = evento.boletos_disponibles - evento.boletos_vendidos
        if cantidad > entradas_restantes:
            return False, f"Sólo quedan {entradas_restantes} boletos disponibles."

        total = evento.precio * cantidad
        fecha_venta = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Registrar la venta en la base de datos
        self.repositorio_ventas.insertar_venta(
            evento_id, cliente, gmail, cantidad, total, fecha_venta
        )

        # Actualizar contador de boletos vendidos
        with sqlite3.connect(RepositorioEventos.DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE eventos
                SET boletos_vendidos = boletos_vendidos + ?
                WHERE id = ?
            """, (cantidad, evento_id))
            conexion.commit()

        mensaje = (
            f"Venta exitosa: {cantidad} boleto(s) para '{evento.nombre}' - "
            f"Total: ${total:.2f} - Fecha: {fecha_venta}"
        )
        return True, mensaje


class GestorConcurrencia:
    """Gestor para manejar la concurrencia con hilos y procesos"""
    
    def __init__(self):
        from capa_datos import (
            HiloProcesadorVentas, 
            HiloMonitorEventos, 
            HiloGeneradorReportes, 
            HiloRespaldoAutomatico, 
            HiloSincronizadorDatos, 
            ProcesoCalculoEstadisticas, 
            ProcesoRespaldoCompleto, 
            ProcesoMantenimientoBaseDatos
        )
        
        # Inicializar 5 hilos concurrentes
        self.hilos = [
            HiloProcesadorVentas(),
            HiloMonitorEventos(),
            HiloGeneradorReportes(),
            HiloRespaldoAutomatico(),
            HiloSincronizadorDatos()
        ]
        
        # Inicializar 3 procesos concurrentes
        self.procesos = [
            ProcesoCalculoEstadisticas(),
            ProcesoRespaldoCompleto(),
            ProcesoMantenimientoBaseDatos()
        ]
    
    def iniciar_concurrencia(self):
        #Inicia todos los hilos y procesos concurrentes
        
        # Iniciar los 5 hilos
        for hilo in self.hilos:
            hilo.start()
        
        # Iniciar los 3 procesos
        for proceso in self.procesos:
            proceso.start()
    
    def detener_concurrencia(self):
        #Detiene todos los hilos y procesos concurrentes
        
        # Detener hilos
        for hilo in self.hilos:
            hilo.activo = False
            hilo.join()
        
        # Terminar procesos
        for proceso in self.procesos:
            proceso.terminate()
            proceso.join()
        

