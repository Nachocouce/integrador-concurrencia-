

from os import system
import sqlite3
import datetime


class SistemaVentaBoletos:
    def __init__(self, db_name: str = "entradas.db"):
        self.db_name = db_name
        self.inicializar_bd()
    
    def inicializar_bd(self):
        # Inicio la base de datos
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Tabla de eventos 
        c.execute("""
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
        # Tabla de ventas
        c.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento_id INTEGER,
                cliente_nombre TEXT NOT NULL,
                cliente_gmail TEXT,
                cantidad_boletos INTEGER NOT NULL,
                total REAL NOT NULL,
                fecha_venta TEXT NOT NULL,
                FOREIGN KEY (evento_id) REFERENCES eventos (id)
           )
        """)

        conn.commit()  # conn.commit()
        conn.close()   # conn.close()
        print("Base de datos inicializada")
    
    def agregar_evento(self, nombre: str, fecha: str, lugar: str, precio: float, boletos_disponibles: int):
        # Se agrega un evento nuevo al sistema
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
            INSERT INTO eventos (nombre, fecha, lugar, precio, boletos_disponibles)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, fecha, lugar, precio, boletos_disponibles))

        conn.commit()
        conn.close()
        print(f"Evento '{nombre}' agregado exitosamente.")
    
    def mostrar_eventos(self) -> list[tuple]:
        # Muestra todos los eventos disponibles
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
            SELECT id, nombre, fecha, lugar, precio,
                  (boletos_disponibles - boletos_vendidos) as disponibles
            FROM eventos
            WHERE (boletos_disponibles - boletos_vendidos) > 0
        ''')

        eventos = c.fetchall()
        conn.close()
        return eventos
    
    def vender_boletos(self, evento_id: int, cliente_nombre: str, cliente_gmail: str, cantidad_boletos: int):
        # Proceso de venta de boletos 
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Verificar la disponibilidad antes de ejecutar la venta
        c.execute('''
            SELECT nombre, precio, (boletos_disponibles - boletos_vendidos) as disponibles 
            FROM eventos WHERE id = ?
        ''', (evento_id,))

        evento = c.fetchone()
        if not evento:
            conn.close()
            return False, "Evento no encontrado."
        
        nombre_evento, precio, disponibles = evento

        if cantidad_boletos > disponibles:
            conn.close()
            return False, f"Solo hay {disponibles} boletos disponibles."
        
        # Procesar venta 
        total = precio * cantidad_boletos
        fecha_venta = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Registrar venta
        c.execute('''
            INSERT INTO ventas (evento_id, cliente_nombre, cliente_gmail, cantidad_boletos, total, fecha_venta)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (evento_id, cliente_nombre, cliente_gmail, cantidad_boletos, total, fecha_venta))
    
        # Actualizar boletos vendidos
        c.execute('''
            UPDATE eventos SET boletos_vendidos = boletos_vendidos + ?
            WHERE id = ?
        ''', (cantidad_boletos, evento_id))

        conn.commit()
        conn.close()

        return True, f"Venta exitosa: {cantidad_boletos} boleto(s) para '{nombre_evento}' - Total: ${total:.2f} - Fecha: {fecha_venta}"
    
    def mostrar_ventas(self) -> list[tuple]:
        # Muestra todas las ventas 
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
            SELECT v.id, e.nombre, v.cliente_nombre, v.cantidad_boletos, v.total, v.fecha_venta
            FROM ventas v
            JOIN eventos e ON v.evento_id = e.id
            ORDER BY v.fecha_venta DESC
        ''')

        ventas = c.fetchall()
        conn.close()
        
        return ventas
    
    def reporte_evento(self, evento_id: int):
    # Genera un reporte del evento
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
            SELECT nombre, fecha, lugar, precio, boletos_disponibles, boletos_vendidos,
                   (boletos_disponibles - boletos_vendidos) as restantes,
                   (boletos_vendidos * precio) as ingresos_totales
            FROM eventos WHERE id = ?
        ''', (evento_id,))

        evento = c.fetchone()
        conn.close()

        return evento

    def mostrar_menu(self):
        # Muestra el menú del sistema
        print("\n" + "=" * 50)
        print("SISTEMA DE VENTA DE BOLETOS")
        print("=" * 50)
        print("1- Agregar evento")
        print("2- Mostrar eventos disponibles")
        print("3- Vender boletos")
        print("4- Ver historial de ventas")
        print("5- Reporte de evento")
        print("6- Salir")
        print("-" * 50)
    
    def agregar_evento_si_no_existe(self, nombre: str, fecha: str, lugar: str, precio: float, boletos_disponibles: int):
    # Verifica si el evento ya existe antes de agregarlo
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
            SELECT id FROM eventos WHERE nombre = ? AND fecha = ?
        ''', (nombre, fecha))

        evento_existente = c.fetchone()
        if evento_existente:
            print(f"El evento '{nombre}' ya existe en la base de datos.")
        else:
            c.execute('''
                INSERT INTO eventos (nombre, fecha, lugar, precio, boletos_disponibles)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, fecha, lugar, precio, boletos_disponibles))
            print(f"Evento '{nombre}' agregado exitosamente.")

        conn.commit()
        conn.close()
    
    def main(self):
        sistema = SistemaVentaBoletos()

        # Agregar ejemplos
        try:
            sistema.agregar_evento("Quevedo", "2025-06-21", "Movistar Arena", 15000.00, 100)
            sistema.agregar_evento("Bad Bunny", "2026-02-13", "Estadio MásMonumental", 85000.00, 200)
            sistema.agregar_evento("Dualipa", "2025-11-07", "Estadio MásMonumental", 85000.00, 150)
        except Exception as e:
            print(f"Error al agregar eventos: {e}")

        while True:
            sistema.mostrar_menu()
            try:
                opcion = input("Seleccionar una opción (1-6):").strip()

                if opcion == "1":
                    print("\n--- AGREGAR EVENTO ---")
                    nombre = input("Nombre del evento:").strip()
                    fecha = input("Fecha (YYYY-MM-DD):").strip()
                    lugar = input("Lugar:").strip()
                    precio = float(input("Precio por boleto:"))
                    boletos = int(input("Número de boletos disponibles:"))

                    sistema.agregar_evento(nombre, fecha, lugar, precio, boletos)
                elif opcion == "2":
                    print("\n--- EVENTOS DISPONIBLES ---")
                    eventos = sistema.mostrar_eventos()
                    if eventos:
                        print(f"{'ID': <3} {'Evento': <25} {'Fecha': <12} {'Lugar': <20} {'Precio': <10} {'Disponibles': <12}")
                        print("-" * 85)
                        for evento in eventos:
                            print(f"{evento[0]: <3} {evento[1]: <25} {evento[2]: <12} {evento[3]: <20} {evento[4]: <10.2f} {evento[5]: <12}")
                    else:
                        print("No hay eventos disponibles.")
                elif opcion == "3":
                    print("\n--- VENDER BOLETOS ---")
                    eventos = sistema.mostrar_eventos()
                    if not eventos:
                        print("No hay eventos disponibles para venta.")
                        continue
                    # Mostrar eventos disponibles
                    print(f"{'ID': <3} {'Evento': <25} {'Disponibles': <12} {'Precio': <10}")
                    print("-" * 85)
                    for evento in eventos:
                        print(f"{evento[0]: <3} {evento[1]: <25} {evento[5]: <12} {evento[4]: <10.2f}")
                    
                    try:
                        evento_id = int(input("\nID del evento:"))
                        cliente_nombre = input("Nombre del cliente:").strip()
                        cliente_gmail = input("Gmail del cliente:").strip()
                        cantidad = int(input("Cantidad de boletos:"))

                        exito, mensaje = sistema.vender_boletos(evento_id, cliente_nombre, cliente_gmail, cantidad)
                        print(mensaje)
                    except ValueError:
                        print("Ingrese valores válidos.")
                elif opcion == "4":
                    print("\n--- HISTORIAL DE VENTAS ---")
                    ventas = sistema.mostrar_ventas()
                    if ventas:
                        print(f"{'ID': <3} {'Evento': <20} {'Cliente': <20} {'Boletos': <8} {'Total': <10} {'Fecha': <20}")
                        print("-" * 80)
                        for venta in ventas:
                            print(f"{venta[0]: <3} {venta[1]: <20} {venta[2]: <20} {venta[3]: <8} {venta[4]: <10.2f} {venta[5]: <20}")
                    else:
                        print("No hay ventas registradas.")
                elif opcion == "5":
                    print("\n--- REPORTE DE EVENTO ---")
                    try:
                        evento_id = int(input("ID del evento:"))
                        reporte = sistema.reporte_evento(evento_id)
                        if reporte:
                            print(f"\nEvento: {reporte[0]}")
                            print(f"Fecha: {reporte[1]}")
                            print(f"Lugar: {reporte[2]}")
                            print(f"Precio por boleto: ${reporte[3]:.2f}")
                            print(f"Boletos disponibles: {reporte[4]}")
                            print(f"Boletos vendidos: {reporte[5]}")
                            print(f"Boletos restantes: {reporte[6]}")
                            print(f"Ingresos totales: ${reporte[7]:.2f}")
                        else:
                            print("Evento no encontrado.")
                    except ValueError:
                        print("Error: Ingrese un ID válido.")
                elif opcion == "6":
                    print("\nGracias por usar nuestro sistema")
                    break
                else:
                    print("Opción no válida, seleccione una opción del 1-6")
            except KeyboardInterrupt:
                print("\n\nSaliendo del sistema")
                break
            except Exception as e:
                print(f"Error: {e}")
            input("\nPresione Enter para continuar")


if __name__ == "__main__":
    SistemaVentaBoletos().main()