from abc import ABC, abstractmethod
import logging

# Configuracion de logging para guardar eventos y errores en archivo y consola
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("software_fj.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SoftwareFJ")


# Excepciones personalizadas para controlar errores del sistema
class ErrorSoftwareFJ(Exception):
    pass

class ErrorValidacion(ErrorSoftwareFJ):
    pass

class ErrorEstadoReserva(ErrorSoftwareFJ):
    pass

class ErrorCapacidadExcedida(ErrorSoftwareFJ):
    pass

class ErrorStockInsuficiente(ErrorSoftwareFJ):
    pass

class ErrorEntidadNoEncontrada(ErrorSoftwareFJ):
    pass

class ErrorServicioNoDisponible(ErrorSoftwareFJ):
    pass

class ErrorCalculoInconsistente(ErrorSoftwareFJ):
    pass


# Clase abstracta base con atributos comunes validados
class EntidadSistema(ABC):
    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = nombre

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion("El codigo no puede estar vacio y debe ser texto.")
        self._codigo = valor.strip()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion("El nombre no puede estar vacio y debe ser texto.")
        self._nombre = valor.strip()

    @abstractmethod
    def mostrar_info(self):
        pass


# Clase Cliente que hereda de EntidadSistema
class Cliente(EntidadSistema):
    def __init__(self, codigo, nombre, correo, telefono):
        super().__init__(codigo, nombre)
        self.correo = correo
        self.telefono = telefono
        logger.info(f"Cliente registrado: {self.codigo} - {self.nombre}")

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor:
            raise ErrorValidacion("El correo electronico no es valido.")
        self._correo = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = valor.strip() if isinstance(valor, str) else ""
        if not limpio.isdigit() or len(limpio) < 7:
            raise ErrorValidacion("El telefono debe tener al menos 7 digitos numericos.")
        self._telefono = limpio

    def mostrar_info(self):
        return (
            f"Cliente [{self.codigo}] {self.nombre} | "
            f"Correo: {self.correo} | Celular: {self.telefono}"
        )


# Clase abstracta Servicio y tipos de servicios
class Servicio(EntidadSistema, ABC):
    def __init__(self, codigo, nombre, tarifa_base, disponible=True):
        super().__init__(codigo, nombre)
        self.tarifa_base = tarifa_base
        self.disponible = bool(disponible)

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        if not isinstance(valor, (int, float)) or isinstance(valor, bool) or valor <= 0:
            raise ErrorValidacion("La tarifa base debe ser un numero mayor que cero.")
        self._tarifa_base = float(valor)

    def cambiar_disponibilidad(self, estado):
        self.disponible = bool(estado)
        logger.info(f"Disponibilidad del servicio {self.nombre} actualizada a: {self.disponible}")

    def validar_disponibilidad(self):
        if not self.disponible:
            logger.warning(f"Intento de usar el servicio no disponible: {self.nombre}.")
            raise ErrorServicioNoDisponible(f"El servicio {self.nombre} no esta disponible en este momento.")

    @abstractmethod
    def calcular_costo(self, cantidad, descuento=0.0, impuesto=0.0):
        pass


class ReservaSala(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, capacidad, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ErrorValidacion("La capacidad de la sala debe ser un numero entero mayor que cero.")
        self.capacidad = capacidad

    # Sobrecarga mediante parametros opcionales de descuento e impuesto
    def calcular_costo(self, cantidad, descuento=0.0, impuesto=0.0):
        if not isinstance(cantidad, (int, float)) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorValidacion("Las horas de reserva deben ser mayores que cero.")
        if not (0.0 <= descuento < 1.0) or impuesto < 0:
            raise ErrorValidacion("Descuento o impuesto fuera de rango.")
        return (self.tarifa_base * cantidad) * (1 - descuento) * (1 + impuesto)

    def mostrar_info(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"Sala [{self.codigo}] {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | Tarifa/hora: ${self.tarifa_base:,.0f} | {estado}"
        )


class AlquilerEquipo(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, stock, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            raise ErrorValidacion("El stock del equipo debe ser un entero mayor o igual a cero.")
        self.stock = stock

    def calcular_costo(self, cantidad, descuento=0.0, impuesto=0.0):
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorValidacion("La cantidad de equipos debe ser un entero mayor que cero.")
        if cantidad > self.stock:
            raise ErrorStockInsuficiente(
                f"No hay unidades suficientes de {self.nombre}. Disponibles: {self.stock}."
            )
        if not (0.0 <= descuento < 1.0) or impuesto < 0:
            raise ErrorValidacion("Descuento o impuesto fuera de rango.")
        return (self.tarifa_base * cantidad) * (1 - descuento) * (1 + impuesto)

    def mostrar_info(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"Equipo [{self.codigo}] {self.nombre} | "
            f"Unidades disponibles: {self.stock} | Tarifa: ${self.tarifa_base:,.0f} | {estado}"
        )


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, tema, consultor, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(tema, str) or not tema.strip():
            raise ErrorValidacion("El tema de la asesoria es obligatorio.")
        if not isinstance(consultor, str) or not consultor.strip():
            raise ErrorValidacion("El nombre del consultor es obligatorio.")
        self.tema = tema.strip()
        self.consultor = consultor.strip()

    def calcular_costo(self, cantidad, descuento=0.0, impuesto=0.0):
        if not isinstance(cantidad, (int, float)) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorValidacion("Las horas de asesoria deben ser mayores que cero.")
        if not (0.0 <= descuento < 1.0) or impuesto < 0:
            raise ErrorValidacion("Descuento o impuesto fuera de rango.")
        return (self.tarifa_base * cantidad) * (1 - descuento) * (1 + impuesto)

    def mostrar_info(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"Asesoria [{self.codigo}] {self.nombre} | Tema: {self.tema} | "
            f"Consultor: {self.consultor} | Tarifa/hora: ${self.tarifa_base:,.0f} | {estado}"
        )


# Clase Reserva para gestionar estados, descuentos y validaciones
class Reserva:
    def __init__(self, codigo, cliente, servicio, cantidad, descuento=0.0, asistentes=1):
        if not isinstance(codigo, str) or not codigo.strip():
            raise ErrorValidacion("El codigo de la reserva es obligatorio.")
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("Debe asociarse un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("Debe asociarse un servicio valido.")
        if not isinstance(cantidad, (int, float)) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ErrorValidacion("La cantidad debe ser mayor que cero.")
        if not isinstance(descuento, (int, float)) or not (0.0 <= descuento < 1.0):
            raise ErrorValidacion("El descuento debe estar entre 0.0 y 0.99.")
        if not isinstance(asistentes, int) or isinstance(asistentes, bool) or asistentes <= 0:
            raise ErrorValidacion("El numero de asistentes debe ser mayor que cero.")

        # Verificar que el servicio este activo antes de reservar
        servicio.validar_disponibilidad()

        if isinstance(servicio, ReservaSala) and asistentes > servicio.capacidad:
            logger.warning(
                f"Intento de reservar {servicio.nombre} con {asistentes} asistentes (capacidad: {servicio.capacidad})."
            )
            raise ErrorCapacidadExcedida(
                f"La sala {servicio.nombre} solo admite {servicio.capacidad} personas."
            )

        if isinstance(servicio, AlquilerEquipo) and cantidad > servicio.stock:
            logger.warning(
                f"Intento de reservar {cantidad} de {servicio.nombre} con stock {servicio.stock}."
            )
            raise ErrorStockInsuficiente(
                f"No hay unidades suficientes de {servicio.nombre}. Disponibles: {servicio.stock}."
            )

        self.codigo = codigo.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.descuento = float(descuento)
        self.asistentes = asistentes
        self.estado = "Pendiente"
        # Guardar subtotal base para mantener el valor tras descontar stock
        self._subtotal_base = self.servicio.calcular_costo(self.cantidad)
        logger.info(f"Reserva creada: {self.codigo} | Cliente: {self.cliente.nombre} | Estado: {self.estado}")

    # Metodo sobrecargado con impuesto y recargo opcionales, try/except/else/finally y encadenamiento
    def calcular_total(self, impuesto=0.0, recargo=0.0):
        try:
            if not isinstance(impuesto, (int, float)) or isinstance(impuesto, bool) or impuesto < 0:
                raise ValueError("El impuesto debe ser un valor numerico no negativo.")
            if not isinstance(recargo, (int, float)) or isinstance(recargo, bool) or recargo < 0:
                raise ValueError("El recargo debe ser un valor numerico no negativo.")

            if self.estado == "Procesada":
                subtotal = self._subtotal_base
            else:
                subtotal = self.servicio.calcular_costo(self.cantidad)

            total = (subtotal * (1 - self.descuento) + recargo) * (1 + impuesto)
            if total <= 0:
                raise ValueError("El total calculado no puede ser menor o igual a cero.")

        except ErrorSoftwareFJ:
            raise
        except Exception as e:
            logger.error(f"Error en el calculo del total en reserva {self.codigo}: {e}")
            raise ErrorCalculoInconsistente(
                f"Calculo inconsistente al liquidar la reserva {self.codigo}."
            ) from e
        else:
            return total
        finally:
            logger.info(f"Verificacion de calculo completada para reserva {self.codigo}.")

    def confirmar(self):
        if self.estado != "Pendiente":
            logger.warning(f"No se puede confirmar la reserva {self.codigo} en estado {self.estado}.")
            raise ErrorEstadoReserva(f"Solo se pueden confirmar reservas Pendientes. Estado actual: {self.estado}")
        self.estado = "Confirmada"
        logger.info(f"Reserva {self.codigo} paso a estado Confirmada.")

    def procesar(self):
        if self.estado != "Confirmada":
            logger.warning(f"No se puede procesar la reserva {self.codigo} en estado {self.estado}.")
            raise ErrorEstadoReserva(f"Solo se pueden procesar reservas Confirmadas. Estado actual: {self.estado}")

        self.servicio.validar_disponibilidad()
        total_final = self.calcular_total()

        if isinstance(self.servicio, AlquilerEquipo):
            if self.cantidad > self.servicio.stock:
                raise ErrorStockInsuficiente(
                    f"Stock insuficiente al procesar {self.servicio.nombre}. Disponibles: {self.servicio.stock}."
                )
            self.servicio.stock -= self.cantidad
            logger.info(f"Stock actualizado para {self.servicio.nombre}: quedan {self.servicio.stock} unidades.")

        self.estado = "Procesada"
        logger.info(f"Reserva {self.codigo} procesada correctamente. Total: ${total_final:,.0f}")

    def cancelar(self):
        if self.estado == "Procesada":
            logger.warning(f"Intento de cancelar la reserva {self.codigo}, que ya esta Procesada.")
            raise ErrorEstadoReserva("No se puede cancelar una reserva ya procesada.")
        if self.estado == "Cancelada":
            logger.warning(f"La reserva {self.codigo} ya estaba cancelada.")
            raise ErrorEstadoReserva("La reserva ya se encuentra cancelada.")
        self.estado = "Cancelada"
        logger.info(f"Reserva {self.codigo} marcada como Cancelada.")

    def mostrar_info(self):
        return (
            f"Reserva [{self.codigo}] | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Cantidad: {self.cantidad} | "
            f"Estado: {self.estado} | Total: ${self.calcular_total():,.0f}"
        )


# Gestor en memoria para guardar y buscar registros
class GestorSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)
        logger.info(f"Cliente agregado al gestor: {cliente.codigo}")

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        logger.info(f"Servicio agregado al gestor: {servicio.codigo} - {servicio.nombre}")

    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)
        logger.info(f"Reserva agregada al gestor: {reserva.codigo}")

    def buscar_reserva(self, codigo):
        for r in self.reservas:
            if r.codigo == codigo:
                return r
        logger.error(f"No se encontro ninguna reserva con el codigo '{codigo}'.")
        raise ErrorEntidadNoEncontrada(f"No existe una reserva con el codigo '{codigo}'.")


# 12 simulaciones completas (operaciones validas e invalidas)
def ejecutar_simulaciones():
    gestor = GestorSoftwareFJ()
    print("=== INICIO DE SIMULACIONES SOFTWARE FJ ===\n")

    # Simulacion 1 (Valida): Registro correcto de clientes
    try:
        cliente1 = Cliente("CLI-1", "Micaela Lopez", "micaela@correo.com", "3015678912")
        cliente2 = Cliente("CLI-2", "Andres Ramirez", "andres.ramirez@correo.com", "3104567890")
    except ErrorSoftwareFJ as e:
        logger.error(f"Simulacion 1 fallo: {e}")
        print(f"[Sim 1] Error: {e}")
    else:
        gestor.agregar_cliente(cliente1)
        gestor.agregar_cliente(cliente2)
        print("[Sim 1 - Valida] Clientes registrados correctamente.")

    # Simulacion 2 (Invalida): Registro de cliente con correo y telefono erroneos
    try:
        cliente_malo = Cliente("CLI-3", "Carlos Ruiz", "carlos_sin_arroba", "123")
        gestor.agregar_cliente(cliente_malo)
    except ErrorValidacion as e:
        logger.error(f"Simulacion 2 controlada: {e}")
        print(f"[Sim 2 - Invalida] Error controlado de cliente: {e}")

    # Simulacion 3 (Valida): Creacion correcta de los 3 tipos de servicios
    try:
        sala1 = ReservaSala("SAL-1", "Sala Norte", 50000, 10)
        equipo1 = AlquilerEquipo("EQP-1", "Portatil HP", 30000, 4)
        asesoria1 = AsesoriaEspecializada("ASE-1", "Soporte Python", 70000, "POO", "Cristian Orozco")
    except ErrorSoftwareFJ as e:
        logger.error(f"Simulacion 3 fallo: {e}")
        print(f"[Sim 3] Error: {e}")
    else:
        gestor.agregar_servicio(sala1)
        gestor.agregar_servicio(equipo1)
        gestor.agregar_servicio(asesoria1)
        print("[Sim 3 - Valida] Servicios creados correctamente.")

    # Simulacion 4 (Invalida): Creacion de servicio con tarifa negativa
    try:
        sala_mala = ReservaSala("SAL-2", "Sala Sur", -25000, 8)
        gestor.agregar_servicio(sala_mala)
    except ErrorValidacion as e:
        logger.error(f"Simulacion 4 controlada: {e}")
        print(f"[Sim 4 - Invalida] Error controlado al crear servicio: {e}")

    # Simulacion 5 (Valida): Reserva de sala con flujo completo (try/except/else/finally)
    reserva1 = None
    try:
        reserva1 = Reserva("RES-1", cliente1, sala1, 2, descuento=0.10, asistentes=6)
        gestor.agregar_reserva(reserva1)
        reserva1.confirmar()
        reserva1.procesar()
    except ErrorSoftwareFJ as e:
        logger.error(f"Simulacion 5 fallo: {e}")
        print(f"[Sim 5] Error: {e}")
    else:
        print(f"[Sim 5 - Valida] Reserva de sala procesada: {reserva1.mostrar_info()}")
    finally:
        logger.info("Cierre de Simulacion 5.")

    # Simulacion 6 (Invalida): Intentar cancelar una reserva que ya fue procesada
    try:
        reserva1.cancelar()
    except ErrorEstadoReserva as e:
        logger.error(f"Simulacion 6 controlada: {e}")
        print(f"[Sim 6 - Invalida] Aviso controlado: {e}")

    # Simulacion 7 (Valida): Alquiler de 3 portatiles con descuento de stock
    try:
        reserva2 = Reserva("RES-2", cliente2, equipo1, 3)
        gestor.agregar_reserva(reserva2)
        reserva2.confirmar()
        reserva2.procesar()
    except ErrorSoftwareFJ as e:
        logger.error(f"Simulacion 7 fallo: {e}")
        print(f"[Sim 7] Error: {e}")
    else:
        print(f"[Sim 7 - Valida] Alquiler procesado: {reserva2.mostrar_info()}")

    # Simulacion 8 (Invalida): Intentar alquilar mas unidades del stock restante
    try:
        reserva_sin_stock = Reserva("RES-ERR1", cliente1, equipo1, 5)
        gestor.agregar_reserva(reserva_sin_stock)
    except ErrorStockInsuficiente as e:
        logger.error(f"Simulacion 8 controlada: {e}")
        print(f"[Sim 8 - Invalida] Aviso controlado: {e}")

    # Simulacion 9 (Invalida): Exceder la capacidad maxima de la sala
    try:
        reserva_llena = Reserva("RES-ERR2", cliente2, sala1, 3, asistentes=15)
        gestor.agregar_reserva(reserva_llena)
    except ErrorCapacidadExcedida as e:
        logger.error(f"Simulacion 9 controlada: {e}")
        print(f"[Sim 9 - Invalida] Aviso controlado: {e}")

    # Simulacion 10 (Invalida): Intentar reservar un servicio no disponible
    try:
        asesoria1.cambiar_disponibilidad(False)
        reserva_inactiva = Reserva("RES-ERR3", cliente1, asesoria1, 2)
        gestor.agregar_reserva(reserva_inactiva)
    except ErrorServicioNoDisponible as e:
        logger.error(f"Simulacion 10 controlada: {e}")
        print(f"[Sim 10 - Invalida] Aviso controlado: {e}")
    finally:
        asesoria1.cambiar_disponibilidad(True)

    # Simulacion 11 (Valida): Asesoria con calculo sobrecargado (IVA/recargo) y cancelacion valida
    reserva3 = None
    try:
        reserva3 = Reserva("RES-3", cliente2, asesoria1, 3, descuento=0.05)
        gestor.agregar_reserva(reserva3)
        reserva3.confirmar()
        reserva3.procesar()

        total_simple = reserva3.calcular_total()
        total_iva = reserva3.calcular_total(impuesto=0.19)
        total_completo = reserva3.calcular_total(impuesto=0.19, recargo=15000)

        reserva4 = Reserva("RES-4", cliente1, sala1, 1, asistentes=4)
        gestor.agregar_reserva(reserva4)
        reserva4.cancelar()
    except ErrorSoftwareFJ as e:
        logger.error(f"Simulacion 11 fallo: {e}")
        print(f"[Sim 11] Error: {e}")
    else:
        print(
            f"[Sim 11 - Valida] Asesoria procesada | Base: ${total_simple:,.0f} | "
            f"Con IVA: ${total_iva:,.0f} | IVA + recargo: ${total_completo:,.0f}"
        )
        print(f"[Sim 11 - Valida] Cancelacion valida: {reserva4.mostrar_info()}")

    # Simulacion 12 (Invalida): Encadenamiento de excepcion en calculo y busqueda inexistente
    try:
        reserva3.calcular_total(impuesto=-0.19)
    except ErrorCalculoInconsistente as e:
        logger.error(f"Simulacion 12a controlada: {e} | Causa: {e.__cause__}")
        print(f"[Sim 12a - Invalida] Encadenamiento controlado: {e} (Causa: {e.__cause__})")

    try:
        gestor.buscar_reserva("RES-999")
    except ErrorEntidadNoEncontrada as e:
        logger.error(f"Simulacion 12b controlada: {e}")
        print(f"[Sim 12b - Invalida] Aviso controlado: {e}")
    finally:
        logger.info("Finalizaron las 12 simulaciones del sistema Software FJ.")

    print("\n--- RESUMEN FINAL DEL SISTEMA ---")
    print(f"Total clientes registrados: {len(gestor.clientes)}")
    print(f"Total servicios registrados: {len(gestor.servicios)}")
    print(f"Total reservas registradas: {len(gestor.reservas)}")
    for r in gestor.reservas:
        print(" -", r.mostrar_info())
    print("\nSistema finalizado de forma estable sin interrupciones.")


if __name__ == "__main__":
    ejecutar_simulaciones()
