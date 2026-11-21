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
        if not valor or not valor.strip():
            raise ErrorValidacion("El codigo no puede estar vacio.")
        self._codigo = valor.strip()

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ErrorValidacion("El nombre no puede estar vacio.")
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
        if not valor or "@" not in valor or "." not in valor:
            raise ErrorValidacion("El correo electronico no es valido.")
        self._correo = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = valor.strip() if valor else ""
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
    def __init__(self, codigo, nombre, tarifa_base):
        super().__init__(codigo, nombre)
        self.tarifa_base = tarifa_base

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        if valor <= 0:
            raise ErrorValidacion("La tarifa base debe ser mayor que cero.")
        self._tarifa_base = float(valor)

    @abstractmethod
    def calcular_costo(self, cantidad):
        pass


class ReservaSala(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, capacidad):
        super().__init__(codigo, nombre, tarifa_base)
        if capacidad <= 0:
            raise ErrorValidacion("La capacidad de la sala debe ser mayor que cero.")
        self.capacidad = capacidad

    def calcular_costo(self, cantidad):
        if cantidad <= 0:
            raise ErrorValidacion("Las horas de reserva deben ser mayores que cero.")
        return self.tarifa_base * cantidad

    def mostrar_info(self):
        return (
            f"Sala [{self.codigo}] {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | Tarifa/hora: ${self.tarifa_base:,.0f}"
        )


class AlquilerEquipo(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, stock):
        super().__init__(codigo, nombre, tarifa_base)
        if stock < 0:
            raise ErrorValidacion("El stock del equipo no puede ser negativo.")
        self.stock = stock

    def calcular_costo(self, cantidad):
        if cantidad <= 0:
            raise ErrorValidacion("La cantidad de equipos debe ser mayor que cero.")
        if cantidad > self.stock:
            raise ErrorStockInsuficiente(
                f"No hay unidades suficientes de {self.nombre}. Disponibles: {self.stock}."
            )
        return self.tarifa_base * cantidad

    def mostrar_info(self):
        return (
            f"Equipo [{self.codigo}] {self.nombre} | "
            f"Unidades disponibles: {self.stock} | Tarifa: ${self.tarifa_base:,.0f}"
        )


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo, nombre, tarifa_base, tema, consultor):
        super().__init__(codigo, nombre, tarifa_base)
        if not tema or not tema.strip():
            raise ErrorValidacion("El tema de la asesoria es obligatorio.")
        if not consultor or not consultor.strip():
            raise ErrorValidacion("El nombre del consultor es obligatorio.")
        self.tema = tema.strip()
        self.consultor = consultor.strip()

    def calcular_costo(self, cantidad):
        if cantidad <= 0:
            raise ErrorValidacion("Las horas de asesoria deben ser mayores que cero.")
        return self.tarifa_base * cantidad

    def mostrar_info(self):
        return (
            f"Asesoria [{self.codigo}] {self.nombre} | Tema: {self.tema} | "
            f"Consultor: {self.consultor} | Tarifa/hora: ${self.tarifa_base:,.0f}"
        )


# Clase Reserva para gestionar estados, descuentos y validaciones
class Reserva:
    def __init__(self, codigo, cliente, servicio, cantidad, descuento=0.0, asistentes=1):
        if not codigo or not codigo.strip():
            raise ErrorValidacion("El codigo de la reserva es obligatorio.")
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("Debe asociarse un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("Debe asociarse un servicio valido.")
        if cantidad <= 0:
            raise ErrorValidacion("La cantidad debe ser mayor que cero.")
        if not (0.0 <= descuento < 1.0):
            raise ErrorValidacion("El descuento debe estar entre 0.0 y 0.99.")
        if asistentes <= 0:
            raise ErrorValidacion("El numero de asistentes debe ser mayor que cero.")

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
        logger.info(f"Reserva creada: {self.codigo} | Cliente: {self.cliente.nombre} | Estado: {self.estado}")

    def calcular_total(self):
        subtotal = self.servicio.calcular_costo(self.cantidad)
        return subtotal * (1 - self.descuento)

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

        if isinstance(self.servicio, AlquilerEquipo):
            self.servicio.stock -= self.cantidad
            logger.info(f"Stock actualizado para {self.servicio.nombre}: quedan {self.servicio.stock} unidades.")

        self.estado = "Procesada"
        logger.info(f"Reserva {self.codigo} procesada correctamente. Total: ${self.calcular_total():,.0f}")

    def cancelar(self):
        if self.estado == "Procesada":
            logger.warning(f"Intento de cancelar la reserva {self.codigo}, que ya esta Procesada.")
            raise ErrorEstadoReserva("No se puede cancelar una reserva ya procesada.")
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


# Pruebas del programa y manejo de excepciones
if __name__ == "__main__":
    gestor = GestorSoftwareFJ()

    try:
        cliente1 = Cliente("CLI-1", "Micaela Lopez", "micaela@correo.com", "3015678912")
        sala1 = ReservaSala("SAL-1", "Sala Norte", 50000, 10)
        equipo1 = AlquilerEquipo("EQP-1", "Portatil HP", 30000, 4)
        asesoria1 = AsesoriaEspecializada("ASE-1", "Soporte Python", 70000, "POO", "Cristian Orozco")

        gestor.agregar_cliente(cliente1)
        gestor.agregar_servicio(sala1)
        gestor.agregar_servicio(equipo1)
        gestor.agregar_servicio(asesoria1)

        reserva1 = Reserva("RES-1", cliente1, sala1, 2, descuento=0.10, asistentes=6)
        gestor.agregar_reserva(reserva1)
        reserva1.confirmar()
        reserva1.procesar()

        # Intentar cancelar una reserva ya procesada
        try:
            reserva1.cancelar()
        except ErrorEstadoReserva as e:
            print(f"Aviso controlado: {e}")

        # Intentar reservar mas portatiles de los disponibles
        try:
            reserva2 = Reserva("RES-2", cliente1, equipo1, 10)
            gestor.agregar_reserva(reserva2)
        except ErrorStockInsuficiente as e:
            print(f"Aviso controlado: {e}")

        # Buscar una reserva que no existe
        try:
            gestor.buscar_reserva("RES-999")
        except ErrorEntidadNoEncontrada as e:
            print(f"Aviso controlado: {e}")

        print("\n--- RESULTADOS ---")
        print(cliente1.mostrar_info())
        print(sala1.mostrar_info())
        print(equipo1.mostrar_info())
        print(asesoria1.mostrar_info())
        print(reserva1.mostrar_info())

    except ErrorSoftwareFJ as e:
        logger.error(f"Error general del sistema: {e}")
        print(f"Error: {e}")