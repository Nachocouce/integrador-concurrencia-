# Capa de presentación e interfaz de usuario del sistema de venta de boletos

from capa_logica import GestorEventos, GestorVentas, GestorConcurrencia, compra_lock


class InterfazUsuario:
    #Clase principal para manejar la interfaz de usuario del sistema
    
    def __init__(self):
        self.gestor_eventos = GestorEventos()
        self.gestor_ventas = GestorVentas()
        self.gestor_concurrencia = GestorConcurrencia()
        
        # Inicia la concurrencia y el simulador de compras
        self.gestor_concurrencia.iniciar_concurrencia(self.gestor_ventas)

    def mostrar_menu_principal(self) -> None:
        print("\n--- MENÚ SISTEMA DE VENTA DE BOLETOS ---")
        print("1) Agregar evento")
        print("2) Listar eventos")
        print("3) Comprar boletos")
        print("4) Historial de ventas")
        print("5) Salir")

    def agregar_evento(self) -> None:
        print("\n--- AGREGAR NUEVO EVENTO ---")
        try:
            nombre = input("Nombre del evento: ").strip()
            fecha = input("Fecha (YYYY-MM-DD): ").strip()
            lugar = input("Lugar del evento: ").strip()
            precio = float(input("Precio por boleto: $"))
            disponibles = int(input("Cantidad de boletos disponibles: "))
            
            self.gestor_eventos.crear_evento(nombre, fecha, lugar, precio, disponibles)
            print("✓ Evento agregado exitosamente.")
            
        except ValueError:
            print("\n✗ Error: Ingresa valores numéricos válidos.")
        except Exception as error:
            print(f"\n✗ Error: {str(error)}")

    def listar_eventos(self) -> None:
        print("\n--- EVENTOS DISPONIBLES ---")
        eventos = self.gestor_eventos.obtener_eventos()
        
        if not eventos:
            print("No hay eventos registrados en el sistema.")
            return
            
        for evento in eventos:
            disponibles = evento.boletos_disponibles - evento.boletos_vendidos
            print(f"ID {evento.id}: {evento.nombre}")
            print(f"  Fecha: {evento.fecha} | Lugar: {evento.lugar}")
            print(f"  Precio: ${evento.precio:.2f} | Boletos disponibles: {disponibles}")
            print()

    def comprar_boletos(self) -> None:
        print("\n--- COMPRAR BOLETOS ---")
        
        eventos = self.gestor_eventos.obtener_eventos()
        if not eventos:
            print("No hay eventos disponibles para comprar boletos.")
            return
            
        print("Eventos disponibles:")
        for evento in eventos:
            disponibles = evento.boletos_disponibles - evento.boletos_vendidos
            if disponibles > 0:
                print(f"  ID {evento.id}: {evento.nombre} - ${evento.precio:.2f} - Disponibles: {disponibles}")
        
        try:
            evento_id = int(input("\nID del evento: "))
            cliente = input("Nombre del cliente: ").strip()
            gmail = input("Correo electrónico del cliente: ").strip()
            cantidad = int(input("Cantidad de boletos a comprar: "))
            print("Intentando comprar boletos...")
            # Intentar adquirir el lock (espera si está ocupado)
            if not compra_lock.acquire(blocking=False):
                print("Hay otras personas comprando en este momento. Por favor espere...")
                compra_lock.acquire()
            try:
                exito, mensaje = self.gestor_ventas.vender_boletos(evento_id, cliente, gmail, cantidad)
                if exito:
                    print(mensaje)
                else:
                    print(f"\n✗ ADVERTENCIA: {mensaje}\n")
            finally:
                compra_lock.release()
                
        except ValueError:
            print("\n✗ Error: Ingresa valores numéricos válidos.")
        except Exception as error:
            print(f"\n✗ Error: {str(error)}")

    def mostrar_historial_ventas(self) -> None:
        print("\n--- HISTORIAL DE VENTAS ---")
        from capa_datos import RepositorioVentas
        ventas = RepositorioVentas().listar_ventas()
        
        if not ventas:
            print("No hay ventas registradas en el sistema.")
            return
            
        for venta in ventas:
            print(f"Venta #{venta.id}")
            print(f"  Evento ID: {venta.evento_id}")
            print(f"  Cliente: {venta.cliente} ({venta.gmail})")
            print(f"  Cantidad: {venta.cantidad_boletos} boletos")
            print(f"  Total: ${venta.total:.2f}")
            print(f"  Fecha: {venta.fecha_venta}")
            print()

    def ejecutar(self) -> None:
        
        while True:
            self.mostrar_menu_principal()
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                self.agregar_evento()
            elif opcion == "2":
                self.listar_eventos()
            elif opcion == "3":
                self.comprar_boletos()
            elif opcion == "4":
                self.mostrar_historial_ventas()
            elif opcion == "5":
                print("\nDeteniendo sistema...")
                try:
                    self.gestor_concurrencia.detener_concurrencia()
                except:
                    pass
                print("¡Gracias por usar el sistema de venta de boletos!")
                break
            else:
                print("Opción inválida. Intenta de nuevo.")


def main():
    #Función principal que inicia la aplicación
    interfaz = InterfazUsuario()
    interfaz.ejecutar()


if __name__ == "__main__":
    main()
