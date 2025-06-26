def obtener_contenido(conocer):

    try:
        resData = (
                    "SELECT id,tema,intencion,texto "
                    "FROM parce_contenido "
                    f"WHERE empresas_id = '{idEmpresa}' "
                    f"AND tema = '{conocer}' "
                )      
        cursor.execute(resData)
        resultados = cursor.fetchall()
        num_rows = cursor.rowcount
        parametro = 'Empresa: ' + str(idEmpresa) + ' y tema es ' + conocer
        log_busqueda("obtener_contenido",parametro ,"",num_rows)
        if num_rows == 0:
            resultados = f"""
                            {{
                                "estado": "False",
                                "msg": "En este momento, no contamos con el contenido específico que estás buscando. Sin embargo, hemos tomado nota de tu solicitud y trabajaremos para proporcionar la información que necesitas lo antes posible. ¡Gracias por tu paciencia y comprensión!"
                            }}
                        """
        resJson = json.dumps(resultados)
        
    except mysql.connector.Error as error:
        resultados = f"""
                                {{
                                    "msg": "Tengo un inconveniente técnico para acceder al contenido del asistente. Por favor reintenta en unos minutos."
                                }}
                    """
        resJson = json.dumps(resultados)

    return resJson  

---

from datetime import time

def traerAgendaHospital():
    log_busqueda("traerAgendaHospital", "Consulta de agenda", "", 0)

    try:
        if not str(idEmpresa).isdigit():
            return json.dumps({
                "estado": "False",
                "msg": "ID de empresa inválido o no proporcionado."
            })

        consulta = """
            SELECT id, 
                   DAYNAME(fecha) AS nombre_dia, 
                   DAY(fecha) AS dia_mes, 
                   MONTHNAME(fecha) AS nombre_mes, 
                   HOUR(hora) AS hora, 
                   LPAD(MINUTE(hora),2,'0') AS minutos, 
                   YEAR(fecha) AS anio
            FROM parce_agenda
            WHERE empresas_id = %s 
              AND fecha > CURDATE()
              AND personas_id = 0
              AND estado = 'ACTIVO'
            ORDER BY fecha, hora ASC
            LIMIT 6
        """
        cursor.execute(consulta, (idEmpresa,))
        citas = cursor.fetchall()

        if not citas:
            return json.dumps({
                "estado": "False",
                "msg": "No tenemos horarios disponibles en este momento. ¿Deseas que te contactemos más adelante?"
            })

        def traducir_fecha(dia_ingles, mes_ingles):
            dias = {
                "Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles",
                "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"
            }
            meses = {
                "January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
                "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
                "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre"
            }
            return dias.get(dia_ingles, dia_ingles), meses.get(mes_ingles, mes_ingles)

        agenda_por_dia = {}
        for c in citas:
            dia_esp, mes_esp = traducir_fecha(c["nombre_dia"], c["nombre_mes"])
            clave_dia = f"{dia_esp} {c['dia_mes']} de {mes_esp} de {c['anio']}"
            hora_obj = time(int(c["hora"]), int(c["minutos"]))
            agenda_por_dia.setdefault(clave_dia, set()).add(hora_obj)

        bloques_frase = []
        for fecha, horas in sorted(agenda_por_dia.items()):
            horas_ordenadas = sorted(horas)
            horas_str = [h.strftime("%H:%M") for h in horas_ordenadas]
            if len(horas_str) > 1:
                horarios_formato = ", ".join(horas_str[:-1]) + f" y {horas_str[-1]}"
            else:
                horarios_formato = horas_str[0]
            bloques_frase.append(
                f"Tenemos disponibilidad para el {fecha} en los siguientes horarios: {horarios_formato}."
            )

        frase = " ".join(bloques_frase) + " ¿Te gustaría que te reserve alguno de estos?"

        return json.dumps({
            "estado": "True",
            "frase": frase
        })

    except Exception as e:
        logging.error(f"Error en traerAgendaHospital: {str(e)}")
        return json.dumps({
            "estado": "False",
            "msg": "Error interno del servidor al consultar disponibilidad."
        })
    
---

def reservarCita(nombre, documento, eps, fecha, hora, celular):
    log_busqueda("reservarCita", f"Reservando cita para {nombre} - Cel: {celular}", "", 0)

    try:
        # Normalizar el número de celular (solo dígitos)
        celular_normalizado = re.sub(r'\D', '', celular)

        # Validar prefijo y longitud según país
        if celular_normalizado.startswith("57") and len(celular_normalizado) == 12:
            pais = "Colombia"
        elif celular_normalizado.startswith("58") and len(celular_normalizado) == 12:
            pais = "Venezuela"
        elif celular_normalizado.startswith("34") and len(celular_normalizado) == 11:
            pais = "España"
        else:
            return json.dumps({
                "estado": "False",
                "mensaje": "El número de celular no es válido. Debe incluir el prefijo del país (57, 58 o 34) y tener la longitud adecuada."
            })

        # Buscar personas_id
        sql_persona = "SELECT id FROM personas WHERE empresas_id = %s AND celular = %s LIMIT 1"
        cursor.execute(sql_persona, (idEmpresa, celular_normalizado))
        resultado = cursor.fetchone()

        if not resultado:
            return json.dumps({
                "estado": "False",
                "mensaje": "El número de celular no está registrado. Por favor verifícalo con el candidato."
            })

        personas_id = resultado[0] if isinstance(resultado, tuple) else resultado["id"]

        # Actualizar agenda
        sql_update = """
            UPDATE parce_agenda 
            SET nombre = %s, telefono = %s, direccion = NULL, ciudad = NULL, email = NULL, 
                estado = 'ACTIVO', personas_id = %s
            WHERE empresas_id = %s AND fecha = %s AND hora = %s
        """
        cursor.execute(sql_update, (nombre, celular_normalizado, personas_id, idEmpresa, fecha, hora))
        conexion.commit()

        return json.dumps({
            "estado": "True",
            "mensaje": f"Cita confirmada para {nombre} el {fecha} a las {hora} ({pais})."
        })

    except Exception as e:
        logging.error(f"Error en reservarCita: {e}")
        return json.dumps({
            "estado": "False",
            "mensaje": "Ocurrió un error al registrar la cita. Intenta nuevamente."
        })
