import { combineReducers } from 'redux';
import {
  preguntasReducer,
  auditoriaReducer,
  respuestasReducer,
  respuestaReducer,
  auditoriaDetailsReducer,
  sendRespuestasReducer,
  getAuditoriasReducer,
} from './auditoriasReducer';
import { authReducer } from './authReducer';
import { sucursalesReducer, sucursalReducer } from './sucursalesReducer';
import {
  incidentesReducer,
  incidenteDetailsReducer,
} from './incidentesReducer';

export default combineReducers({
  sucursales: sucursalesReducer,
  sucursal: sucursalReducer,
  auditoria: auditoriaReducer,
  auditoriaDetails: auditoriaDetailsReducer,
  preguntas: preguntasReducer,
  respuestas: respuestasReducer,
  respuesta: respuestaReducer,
  sendRespuestas: sendRespuestasReducer,
  auth: authReducer,
  incidentes: incidentesReducer,
  incidente: incidenteDetailsReducer,
  auditorias: getAuditoriasReducer,
});
