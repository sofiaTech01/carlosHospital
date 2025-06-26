--
-- Estructura de tabla para la tabla `parce_contenido`
--

CREATE TABLE `parce_contenido` (
  `id` int(11) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `empresas_id` int(11) NOT NULL,
  `usuarios_id` int(11) NOT NULL,
  `tema` varchar(250) NOT NULL,
  `intencion` text NOT NULL,
  `texto` text NOT NULL,
  `archivo` varchar(100) NOT NULL,
  `tipoArchivo` enum('Ninguno','pdf','json') NOT NULL DEFAULT 'Ninguno'
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `parce_contenido`
--
ALTER TABLE `parce_contenido`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `parce_contenido`
--
ALTER TABLE `parce_contenido`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

---

--
-- Estructura de tabla para la tabla `parce_agenda`
--

CREATE TABLE `parce_agenda` (
  `id` int(11) NOT NULL,
  `empresas_id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `personas_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(50) NOT NULL,
  `direccion` varchar(100) NOT NULL,
  `ciudad` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `estado` enum('ACTIVO','INACTIVO') NOT NULL,
  `agendado` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `parce_agenda`
--
ALTER TABLE `parce_agenda`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `empresas_id` (`empresas_id`,`fecha`,`hora`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `parce_agenda`
--
ALTER TABLE `parce_agenda`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

---

