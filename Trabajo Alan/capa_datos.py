#Para acceso a la base de datos y modelos.

import sqlite3
import threading
import multiprocessing
import time
import shutil
from datetime import datetime
from typing import List


class Evento:
    def __init__(
        self,
        id: int,
        nombre: str,
        fecha: str,
        lugar: str,
        precio: float,
        boletos_disponibles: int,
        boletos_vendidos: int = 0
    ):
        self.id = id
        self.nombre = nombre
        self.fecha = fecha
        self.lugar = lugar
        self.precio = precio
        self.boletos_disponibles = boletos_disponibles
        self.boletos_vendidos = boletos_vendidos


class Venta:
    def __init__(
        self,
        id: int,
        evento_id: int,
        cliente: str,
        gmail: str,
        cantidad_boletos: int,
        total: float,
        fecha_venta: str
    ):
        self.id = id
        self.evento_id = evento_id
        self.cliente = cliente
        self.gmail = gmail
        self.cantidad_boletos = cantidad_boletos
        self.total = total
        self.fecha_venta = fecha_venta


class RepositorioEventos:
    DB = "entradas.db"

    def __init__(self):
        self._inicializar_bd()

    def _inicializar_bd(self) -> None:
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    lugar TEXT NOT NULL,
                    precio REAL NOT NULL,
                    boletos_disponibles INTEGER NOT NULL,
                    boletos_vendidos INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def insertar_evento(
        self,
        nombre: str,
        fecha: str,
        lugar: str,
        precio: float,
        disponibles: int
    ) -> None:
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO eventos (nombre, fecha, lugar, precio, boletos_disponibles)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, fecha, lugar, precio, disponibles))
            conn.commit()

    def listar_eventos(self) -> List[Evento]:
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, fecha, lugar, precio,
                       boletos_disponibles, boletos_vendidos
                FROM eventos
            """)
            filas = cursor.fetchall()
        return [Evento(*fila) for fila in filas]

    def obtener_evento_por_id(self, evento_id: int) -> Evento | None:
        """Obtiene un evento específico por su ID"""
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, fecha, lugar, precio,
                       boletos_disponibles, boletos_vendidos
                FROM eventos WHERE id = ?
            """, (evento_id,))
            fila = cursor.fetchone()
        return Evento(*fila) if fila else None

    def actualizar_boletos_vendidos(self, evento_id: int, cantidad: int) -> None:
        """Actualiza el contador de boletos vendidos de un evento"""
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE eventos
                SET boletos_vendidos = boletos_vendidos + ?
                WHERE id = ?
            """, (cantidad, evento_id))
            conn.commit()

    def establecer_boletos_vendidos(self, evento_id: int, cantidad: int) -> None:
        """Establece directamente el contador de boletos vendidos de un evento"""
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE eventos
                SET boletos_vendidos = ?
                WHERE id = ?
            """, (cantidad, evento_id))
            conn.commit()


class RepositorioVentas:
    DB = "entradas.db"

    def __init__(self):
        self._inicializar_bd()

    def _inicializar_bd(self) -> None:
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evento_id INTEGER NOT NULL,
                    cliente_nombre TEXT NOT NULL,
                    cliente_gmail TEXT NOT NULL,
                    cantidad_boletos INTEGER NOT NULL,
                    total REAL NOT NULL,
                    fecha_venta TEXT NOT NULL,
                    FOREIGN KEY (evento_id) REFERENCES eventos (id)
                )
            """)
            conn.commit()

    def insertar_venta(
        self,
        evento_id: int,
        cliente: str,
        gmail: str,
        cantidad_boletos: int,
        total: float,
        fecha_venta: str
    ) -> None:
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ventas (
                    evento_id, cliente_nombre, cliente_gmail,
                    cantidad_boletos, total, fecha_venta
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (evento_id, cliente, gmail, cantidad_boletos, total, fecha_venta))
            conn.commit()

    def listar_ventas(self) -> List[Venta]:
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, evento_id, cliente_nombre, cliente_gmail,
                       cantidad_boletos, total, fecha_venta
                FROM ventas
                ORDER BY fecha_venta DESC
            """)
            filas = cursor.fetchall()
        return [Venta(*fila) for fila in filas]

    def obtener_ventas_por_evento(self, evento_id: int) -> List[Venta]:
        #Obtiene todas las ventas de un evento específico
        with sqlite3.connect(self.DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, evento_id, cliente_nombre, cliente_gmail,
                       cantidad_boletos, total, fecha_venta
                FROM ventas WHERE evento_id = ?
            """, (evento_id,))
            filas = cursor.fetchall()
        return [Venta(*fila) for fila in filas]



# 5 Hilos

class HiloProcesadorVentas(threading.Thread):
    #Hilo para procesar ventas pendientes en segundo plano
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.activo = True

    def run(self):
        #Ejecuta el procesamiento de ventas en segundo plano
        while self.activo:
            try:
                time.sleep(5)
            except:
                pass


class HiloMonitorEventos(threading.Thread):
    #Hilo para monitorear eventos con baja disponibilidad
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.activo = True

    def run(self):
        #Monitoreo de disponibilidad de boletos
        while self.activo:
            try:
                repositorio_eventos = RepositorioEventos()
                eventos = repositorio_eventos.listar_eventos()
                
                for evento in eventos:
                    disponibles = evento.boletos_disponibles - evento.boletos_vendidos
                    if disponibles <= 5 and disponibles > 0:
                        # Alerta por baja disponibilidad de boletos
                        print(f"ALERTA: Evento '{evento.nombre}' tiene solo {disponibles} boletos disponibles")
                
                time.sleep(10)
            except Exception as e:
                print(f"Error en monitoreo de eventos: {e}")
                pass


class HiloGeneradorReportes(threading.Thread):
    #Genera reportes automáticos
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.activo = True

    def run(self):
        #Ejecuta la generación de reportes automáticos
        while self.activo:
            try:
                repositorio_ventas = RepositorioVentas()
                ventas = repositorio_ventas.listar_ventas()
                
                if ventas:
                    total_ventas = len(ventas)
                    total_ingresos = sum(venta.total for venta in ventas)
                    #Guardar el reporte
                    print(f"Reporte generado: {total_ventas} ventas, ${total_ingresos:.2f} en ingresos")
                
                time.sleep(360)
            except Exception as e:
                print(f"Error generando reporte: {e}")
                pass


class HiloRespaldoAutomatico(threading.Thread):
    #Realizar respaldos automáticos
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.activo = True

    def run(self):
        #Ejecuta el respaldo automático de la base de datos
        while self.activo:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta_respaldo = f"respaldo_entradas_{timestamp}.db"
                shutil.copy2("entradas.db", ruta_respaldo)
                print(f"Respaldo automático creado: {ruta_respaldo}")
                time.sleep(300) 
            except Exception as e:
                print(f"Error en respaldo automático: {e}")
                pass


class HiloSincronizadorDatos(threading.Thread):
    #Sincronizar datos entre tablas
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.activo = True

    def run(self):
        #Ejecuta la sincronización de datos entre tablas
        while self.activo:
            try:
                repositorio_eventos = RepositorioEventos()
                repositorio_ventas = RepositorioVentas()
                
                eventos = repositorio_eventos.listar_eventos()
                for evento in eventos:
                    ventas_evento = repositorio_ventas.obtener_ventas_por_evento(evento.id)
                    total_vendido = sum(venta.cantidad_boletos for venta in ventas_evento)
                    
                    if total_vendido != evento.boletos_vendidos:
                        # Sincronizar contador
                        repositorio_eventos.establecer_boletos_vendidos(evento.id, total_vendido)
                        print(f"Sincronizado evento {evento.id}: {total_vendido} boletos vendidos")
                
                time.sleep(30)  
            except Exception as e:
                print(f"Error en sincronización: {e}")
                pass


#3 Procesos 

class ProcesoCalculoEstadisticas(multiprocessing.Process):
    #Proceso para calcular estadísticas 
    
    def run(self):
        #Se calculan las estadisticas
        try:
            with sqlite3.connect("entradas.db") as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        SUM(total) as ingresos_totales,
                        AVG(total) as promedio_venta,
                        COUNT(DISTINCT evento_id) as eventos_con_ventas
                    FROM ventas
                """)
                estadisticas = cursor.fetchone()
                #Se guardan las estadisticas
                if estadisticas:
                    total_ventas, ingresos_totales, promedio_venta, eventos_con_ventas = estadisticas
                    print(f"Estadísticas calculadas: {total_ventas} ventas, ${ingresos_totales or 0:.2f} ingresos, ${promedio_venta or 0:.2f} promedio por venta, {eventos_con_ventas} eventos con ventas")
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
            pass


class ProcesoRespaldoCompleto(multiprocessing.Process):
    #Respaldar la base de datos con compresión
    
    def run(self):
        #Se respalda la base de datos
        try:
            time.sleep(1000)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_respaldo = f"respaldo_completo_{timestamp}.db"
            shutil.copy2("entradas.db", ruta_respaldo)
            print(f"Respaldo completo creado: {ruta_respaldo}")
        except Exception as e:
            print(f"Error en respaldo completo: {e}")
            pass


class ProcesoMantenimientoBaseDatos(multiprocessing.Process):
    #Mantener y optimizar la base de datos
    
    def run(self):
        #Se ejecuta
        try:
            with sqlite3.connect("entradas.db") as conexion:
                cursor = conexion.cursor()
                cursor.execute("VACUUM")
                cursor.execute("ANALYZE")
                print("Mantenimiento de base de datos completado")
        except Exception as e:
            print(f"Error en mantenimiento de BD: {e}")
            pass
