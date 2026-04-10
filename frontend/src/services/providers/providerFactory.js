import { DEMO_MODE } from '../../utils/constants';
import * as demo from '../mock/pipelineMock';
import * as basix from './providerBasix';

const source = (import.meta.env.VITE_DATA_SOURCE || 'demo').toLowerCase();

export function getProvider(){
  if(source === 'basix') return basix;
  return demo;
}

export function getSourceLabel(){
  return source === 'basix' ? 'basix' : (DEMO_MODE ? 'demo' : 'demo');
}

