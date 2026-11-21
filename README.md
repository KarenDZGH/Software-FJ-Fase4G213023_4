# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto colaborativo de la **Fase 4 (Componente práctico - Prácticas simuladas)** del curso **Programación (213023)** de la UNAD, Grupo `213023_4`.

## Descripción
Aplicación orientada a objetos en Python, sin uso de bases de datos, para gestionar clientes, servicios (reserva de salas, alquiler de equipos y asesorías especializadas) y reservas en memoria. Implementa manejo robusto de excepciones y registro de eventos en archivo de logs para garantizar que el sistema continúe funcionando ante errores.

## Características implementadas
- **POO:** Clases abstractas (`EntidadSistema`, `Servicio`), encapsulación con validaciones en `Cliente`, herencia y polimorfismo en los tres tipos de servicio, clase `Reserva` y gestor en memoria (`GestorSoftwareFJ`).
- **Excepciones avanzadas:** Excepciones personalizadas, bloques `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones (`raise ... from e`).
- **Sobrecarga de métodos:** Cálculo de costos con parámetros opcionales de descuento, impuesto y recargo.
- **Simulaciones y logs:** 12 simulaciones completas (válidas e inválidas) con registro detallado en `software_fj.log`.

## Ejecución
1. Tener instalado Python 3.10 o superior.
2. Ejecutar el archivo principal desde la terminal:

    python softwareG4_fj.py

3. Al finalizar, se genera o actualiza el archivo `software_fj.log` con el historial de eventos y errores controlados.

## Integrantes
- Karen Alicia Diazgranados Diaz (`KarenDZGH`)
- Luis Fernando Ditta Barraza (`eledeluisito`)
